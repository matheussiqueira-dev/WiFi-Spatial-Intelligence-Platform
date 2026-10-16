"""One CPU job, two queued, cooperative cancellation before persistence."""

import asyncio
import logging
import threading
from uuid import uuid4

from app.application.model_lab import ExperimentRequest

logger = logging.getLogger("spatial.jobs")


def queued(identifier, request):
    return {
        "id": identifier,
        "state": "queued",
        "seed": request.seed,
        "progress": 0,
        "run_id": None,
        "error": None,
        "evidence_level": "L0_SYNTHETIC",
    }


class ExperimentJobs:
    def __init__(self, lab, lock):
        self.lab = lab
        self.store = lab.store
        self.lock = lock
        self.queue = asyncio.Queue(maxsize=2)
        self.cancelled = {}
        self.task = None
        self.closed = False
        self.last_error = None
        # Serializes capacity checks with persistence so awaited I/O cannot oversubscribe.
        self.admission = asyncio.Lock()

    async def start(self):
        await asyncio.to_thread(self.store.interrupt_jobs)
        self.task = asyncio.create_task(self.work())
        self.task.add_done_callback(self.stopped)

    def stopped(self, task):
        if task.cancelled():
            return
        self.last_error = self.last_error or "job_worker_stopped"
        logger.error("experiment job worker stopped", exc_info=task.exception())

    def accepting(self):
        worker_gone = self.task is not None and self.task.done()
        return not (self.closed or self.last_error or worker_gone or self.queue.full())

    async def submit(self, request: ExperimentRequest):
        async with self.admission:
            if not self.accepting() or await asyncio.to_thread(self.store.job_count) >= 100:
                raise ValueError("experiment queue or history capacity reached")
            identifier = str(uuid4())
            job = queued(identifier, request)
            self.cancelled[identifier] = threading.Event()
            try:
                await asyncio.to_thread(self.store.save_job, identifier, job)
            except BaseException:
                self.cancelled.pop(identifier, None)
                raise
            # No await between the persisted state and the enqueue.
            self.queue.put_nowait((identifier, request))
            return dict(job)

    def cancel(self, identifier):
        flag = self.cancelled.get(identifier)
        if flag:
            flag.set()
            return True
        return False

    async def work(self):
        while True:
            identifier, request = await self.queue.get()
            try:
                await self.run(identifier, request)
            finally:
                self.cancelled.pop(identifier, None)
                self.queue.task_done()

    async def run(self, identifier, request):
        job = queued(identifier, request)
        try:
            flag = self.cancelled[identifier]
            job = await asyncio.to_thread(self.store.job, identifier) or job
            async with self.lock:
                if flag.is_set():
                    result = None
                else:

                    def progress(state):
                        job.update(
                            state=state,
                            progress={"preparing": 10, "training": 40, "persisting": 80}[state],
                        )
                        self.store.save_job(identifier, job)

                    result = await asyncio.to_thread(
                        self.lab.execute, request, flag.is_set, progress
                    )
                job.update(
                    state="completed" if result else "cancelled",
                    progress=100 if result else job["progress"],
                    run_id=result["id"] if result else None,
                )
        except Exception:
            # Diagnostics stay in the local log; the job record keeps a sanitized code.
            logger.exception("experiment job failed")
            job.update(state="failed", error="experiment_failed")
        try:
            await asyncio.to_thread(self.store.save_job, identifier, job)
        except Exception:
            self.last_error = "job_status_persistence_failed"
            logger.exception("experiment job status persistence failed")

    async def close(self):
        async with self.admission:
            self.closed = True
        for flag in self.cancelled.values():
            flag.set()
        if self.task is None:
            return
        drained = asyncio.create_task(self.queue.join())
        await asyncio.wait({drained, self.task}, return_when=asyncio.FIRST_COMPLETED)
        worker_stopped = self.task.done()
        drained.cancel()
        self.task.cancel()
        await asyncio.gather(self.task, drained, return_exceptions=True)
        if worker_stopped:
            await self.abandon()

    async def abandon(self):
        # The worker stopped before draining: never wait on it, record the jobs as interrupted.
        while not self.queue.empty():
            identifier, _ = self.queue.get_nowait()
            self.cancelled.pop(identifier, None)
            self.queue.task_done()
        try:
            await asyncio.to_thread(self.store.interrupt_jobs)
        except Exception:
            logger.exception("experiment job interruption persistence failed")
