import asyncio
import json
import threading
import time

import pytest
from sqlalchemy.exc import OperationalError

from app.application.experiment_jobs import ExperimentJobs
from app.application.model_lab import ExperimentRequest


class StubLab:
    """Fast stand-in for ModelLab: each call consumes one scripted outcome."""

    def __init__(self, store, outcomes=()):
        self.store = store
        self.outcomes = list(outcomes)

    def execute(self, request, cancelled=lambda: False, progress=lambda _: None):
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        progress("preparing")
        return outcome


async def wait_dequeued(jobs):
    async with asyncio.timeout(2):
        while not jobs.queue.empty():
            await asyncio.sleep(0)


def test_unexpected_lab_error_fails_job_and_worker_survives(client):
    store = client.app.state.store

    async def exercise():
        jobs = ExperimentJobs(
            StubLab(store, [KeyError("secret-boom"), {"id": "run-2"}]), asyncio.Lock()
        )
        await jobs.start()
        first = await jobs.submit(ExperimentRequest(seed=1))
        second = await jobs.submit(ExperimentRequest(seed=2))
        async with asyncio.timeout(3):
            await jobs.queue.join()
        assert not jobs.task.done() and jobs.last_error is None
        async with asyncio.timeout(3):
            await jobs.close()
        return first["id"], second["id"]

    first, second = asyncio.run(exercise())
    failed = store.job(first)
    assert failed["state"] == "failed" and failed["error"] == "experiment_failed"
    assert "secret-boom" not in json.dumps(failed)
    assert store.job(second)["state"] == "completed" and store.job(second)["run_id"] == "run-2"


def test_worker_store_read_error_fails_job_and_worker_survives(client, monkeypatch):
    store = client.app.state.store
    original = store.job
    failing = {"armed": False}

    def flaky_job(identifier):
        if failing["armed"]:
            failing["armed"] = False
            raise OperationalError("SELECT", {}, Exception("database is locked"))
        return original(identifier)

    monkeypatch.setattr(store, "job", flaky_job)

    async def exercise():
        jobs = ExperimentJobs(StubLab(store, [{"id": "run-2"}]), asyncio.Lock())
        await jobs.start()
        first = await jobs.submit(ExperimentRequest(seed=1))
        # The next read is the worker's own lookup of the job it just dequeued.
        failing["armed"] = True
        async with asyncio.timeout(3):
            await jobs.queue.join()
        second = await jobs.submit(ExperimentRequest(seed=2))
        async with asyncio.timeout(3):
            await jobs.queue.join()
        assert not jobs.task.done() and not jobs.cancelled
        async with asyncio.timeout(3):
            await jobs.close()
        return first["id"], second["id"]

    first, second = asyncio.run(exercise())
    failed = store.job(first)
    assert failed["state"] == "failed" and failed["error"] == "experiment_failed"
    assert failed["seed"] == 1 and failed["evidence_level"] == "L0_SYNTHETIC"
    assert store.job(second)["state"] == "completed"


def test_dead_worker_rejects_submissions_and_close_does_not_hang(client, monkeypatch):
    store = client.app.state.store

    async def exercise():
        lock = asyncio.Lock()
        await lock.acquire()
        jobs = ExperimentJobs(StubLab(store, [{"id": "run-1"}]), lock)
        await jobs.start()
        first = await jobs.submit(ExperimentRequest(seed=1))
        await wait_dequeued(jobs)
        second = await jobs.submit(ExperimentRequest(seed=2))
        original = jobs.queue.task_done

        def broken_task_done():
            jobs.queue.task_done = original
            raise RuntimeError("worker bookkeeping bug")

        monkeypatch.setattr(jobs.queue, "task_done", broken_task_done)
        lock.release()
        async with asyncio.timeout(2):
            while not jobs.last_error:
                await asyncio.sleep(0)
        assert jobs.task.done() and jobs.last_error == "job_worker_stopped"
        with pytest.raises(ValueError):
            await jobs.submit(ExperimentRequest(seed=3))
        async with asyncio.timeout(3):
            await jobs.close()
        assert not jobs.cancelled
        return first["id"], second["id"]

    first, second = asyncio.run(exercise())
    assert store.job(first)["state"] == "completed"
    assert store.job(second)["state"] == "interrupted"


def test_close_returns_when_worker_dies_while_draining(client, monkeypatch):
    store = client.app.state.store

    async def exercise():
        lock = asyncio.Lock()
        await lock.acquire()
        jobs = ExperimentJobs(StubLab(store), lock)
        await jobs.start()
        first = await jobs.submit(ExperimentRequest(seed=1))
        await wait_dequeued(jobs)
        second = await jobs.submit(ExperimentRequest(seed=2))
        original = jobs.queue.task_done

        def broken_task_done():
            jobs.queue.task_done = original
            raise RuntimeError("worker bookkeeping bug")

        monkeypatch.setattr(jobs.queue, "task_done", broken_task_done)
        closing = asyncio.create_task(jobs.close())
        await asyncio.sleep(0)
        lock.release()
        async with asyncio.timeout(3):
            await closing
        assert jobs.task.done() and jobs.last_error == "job_worker_stopped"
        return first["id"], second["id"]

    first, second = asyncio.run(exercise())
    assert store.job(first)["state"] == "cancelled"
    assert store.job(second)["state"] == "interrupted"


def test_store_io_runs_off_the_event_loop_thread(client, monkeypatch):
    store = client.app.state.store
    calls = []
    for name in ("job_count", "save_job", "job"):

        def recorder(*args, _original=getattr(store, name), _name=name):
            calls.append((_name, threading.get_ident()))
            return _original(*args)

        monkeypatch.setattr(store, name, recorder)

    async def exercise():
        jobs = ExperimentJobs(StubLab(store, [{"id": "run-1"}]), asyncio.Lock())
        await jobs.start()
        submitted = await jobs.submit(ExperimentRequest())
        assert submitted["state"] == "queued" and submitted["progress"] == 0
        async with asyncio.timeout(3):
            await jobs.queue.join()
        await jobs.close()
        return threading.get_ident()

    loop_thread = asyncio.run(exercise())
    assert {name for name, _ in calls} == {"job_count", "save_job", "job"}
    assert all(thread != loop_thread for _, thread in calls)


def test_concurrent_submits_respect_queue_slots(client, monkeypatch):
    store = client.app.state.store
    original = store.save_job

    def slow_save(*args):
        time.sleep(0.02)
        return original(*args)

    async def exercise():
        lock = asyncio.Lock()
        await lock.acquire()
        jobs = ExperimentJobs(StubLab(store), lock)
        await jobs.start()
        await jobs.submit(ExperimentRequest(seed=1))
        await wait_dequeued(jobs)
        monkeypatch.setattr(store, "save_job", slow_save)
        outcomes = await asyncio.gather(
            *(jobs.submit(ExperimentRequest(seed=seed)) for seed in (2, 3, 4)),
            return_exceptions=True,
        )
        assert jobs.queue.qsize() == 2
        lock.release()
        await jobs.close()
        return outcomes

    outcomes = asyncio.run(exercise())
    assert sum(isinstance(item, ValueError) for item in outcomes) == 1
    assert store.job_count() == 3


def test_concurrent_submits_respect_history_capacity(client, monkeypatch):
    store = client.app.state.store
    for index in range(99):
        store.save_job(f"fixture-{index}", {"state": "completed"})
    original = store.save_job

    def slow_save(*args):
        time.sleep(0.02)
        return original(*args)

    monkeypatch.setattr(store, "save_job", slow_save)

    async def exercise():
        lock = asyncio.Lock()
        await lock.acquire()
        jobs = ExperimentJobs(StubLab(store), lock)
        await jobs.start()
        outcomes = await asyncio.gather(
            *(jobs.submit(ExperimentRequest(seed=seed)) for seed in (1, 2)),
            return_exceptions=True,
        )
        lock.release()
        await jobs.close()
        return outcomes

    outcomes = asyncio.run(exercise())
    assert sum(isinstance(item, ValueError) for item in outcomes) == 1
    assert store.job_count() == 100
