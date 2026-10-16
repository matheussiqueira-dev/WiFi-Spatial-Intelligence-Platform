import asyncio
import time
from pathlib import Path

import pytest

from app.application.experiment_jobs import ExperimentJobs
from app.application.model_lab import ExperimentRequest, ModelLab


def test_queue_capacity_cancel_and_shutdown(client, tmp_path):
    store = client.app.state.store

    async def exercise():
        lock = asyncio.Lock()
        await lock.acquire()
        jobs = ExperimentJobs(ModelLab(store, tmp_path / "lab"), lock)
        await jobs.start()
        first = await jobs.submit(ExperimentRequest())
        # Observe dequeue by the worker while its CPU lock is deliberately held.
        async with asyncio.timeout(2):
            while not jobs.queue.empty():
                await asyncio.sleep(0)
        second = await jobs.submit(ExperimentRequest(seed=43))
        await jobs.submit(ExperimentRequest(seed=44))
        with pytest.raises(ValueError):
            await jobs.submit(ExperimentRequest(seed=45))
        assert jobs.cancel(first["id"]) and jobs.cancel(second["id"])
        lock.release()
        await jobs.close()
        assert store.job(first["id"])["state"] == "cancelled"
        assert store.model_runs()["total"] == 0

    asyncio.run(exercise())


def test_job_api_completion_and_restart_status(client):
    response = client.post("/api/v1/model-lab/jobs", json={"seed": 51})
    assert response.status_code == 200
    identifier = response.json()["id"]
    deadline = time.monotonic() + 3
    while time.monotonic() < deadline:
        job = client.get(f"/api/v1/model-lab/jobs/{identifier}").json()
        if job["state"] == "completed":
            break
    assert job["progress"] == 100 and job["run_id"]
    assert client.get(f"/api/v1/model-lab/runs/{job['run_id']}").status_code == 200
    assert client.post(f"/api/v1/model-lab/jobs/{identifier}/cancel").status_code == 409
    store = client.app.state.store
    store.save_job("interrupted-fixture", {"state": "training"})
    store.interrupt_jobs()
    assert store.job("interrupted-fixture")["state"] == "interrupted"


def test_job_failure_is_durable_and_sanitized(client, tmp_path):
    class FailingLab(ModelLab):
        def execute(self, *args):
            raise ValueError("secret-sentinel")

    async def exercise():
        jobs = ExperimentJobs(FailingLab(client.app.state.store, Path(tmp_path)), asyncio.Lock())
        await jobs.start()
        submitted = await jobs.submit(ExperimentRequest())
        await jobs.queue.join()
        assert jobs.store.job(submitted["id"])["error"] == "experiment_failed"
        await jobs.close()

    asyncio.run(exercise())
