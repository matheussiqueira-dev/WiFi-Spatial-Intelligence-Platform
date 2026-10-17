import asyncio
import threading
import time

from app.config import Settings
from app.contracts import SimulationConfig
from app.pipeline import Pipeline


class GatedStore:
    """Fails the first write, then blocks writes until released."""

    def __init__(self):
        self.segment_id = None
        self.calls = 0
        self.release = threading.Event()
        self.written = []

    def write(self, event, segment_id=...):
        self.calls += 1
        if self.calls == 1:
            raise OSError("injected transient storage failure")
        self.release.wait(5)
        self.written.append(self.segment_id if segment_id is ... else segment_id)
        return True

    def audit(self, action):
        pass


def settings():
    return Settings(token="test-only-" + "x" * 40, _env_file=None)


def test_backlog_after_persistence_failure_never_joins_the_next_session():
    async def scenario():
        store = GatedStore()
        pipeline = Pipeline(store, settings())
        config = SimulationConfig(speed=4)
        await pipeline.control("start", config)
        old_segment = store.segment_id
        ingest = asyncio.create_task(pipeline.ingest())
        deadline = time.monotonic() + 5
        while pipeline.queue.qsize() < 4 and time.monotonic() < deadline:
            await asyncio.sleep(0.01)
        ingest.cancel()
        await asyncio.gather(ingest, return_exceptions=True)
        assert pipeline.queue.qsize() >= 4
        consume = asyncio.create_task(pipeline.consume())
        while pipeline.error is None and time.monotonic() < deadline:
            await asyncio.sleep(0.01)
        assert pipeline.state == "stopped"
        restart = asyncio.create_task(pipeline.control("start", config))
        await asyncio.sleep(0.05)
        store.release.set()
        await asyncio.wait_for(restart, 5)
        new_segment = store.segment_id
        await pipeline.queue.join()
        consume.cancel()
        await asyncio.gather(consume, return_exceptions=True)
        await pipeline.provider.disconnect()
        return old_segment, new_segment, store.written, pipeline

    old_segment, new_segment, written, pipeline = asyncio.run(scenario())
    assert old_segment != new_segment
    assert new_segment not in written, "stale backlog was persisted under the new segment"
    assert pipeline.produced == 0
    assert pipeline.latest is None
    assert pipeline.state == "running"
    assert pipeline.error is None


def test_status_snapshot_tolerates_concurrent_measurement_appends():
    pipeline = Pipeline(GatedStore(), settings())
    now = time.monotonic()
    pipeline.measurements.extend((now, 1.0) for _ in range(2000))
    stop = threading.Event()
    failures = []

    def poll():
        while not stop.is_set():
            try:
                pipeline.status()
            except RuntimeError as error:
                failures.append(error)
                return

    reader = threading.Thread(target=poll)
    reader.start()
    deadline = time.monotonic() + 1.5
    while time.monotonic() < deadline and not failures:
        pipeline.measurements.append((time.monotonic(), 1.0))
    stop.set()
    reader.join()
    assert not failures


class ExplodingProvider:
    streaming = True
    connected = True
    config = SimulationConfig()

    async def next_event(self):
        raise RuntimeError("unexpected provider defect")

    async def disconnect(self):
        self.connected = False

    def diagnostics(self):
        return {"reconnections": 0}


def test_unexpected_provider_error_stops_the_session_but_keeps_ingest_alive():
    async def scenario():
        pipeline = Pipeline(GatedStore(), settings())
        pipeline.provider = ExplodingProvider()
        pipeline.state = "running"
        ingest = asyncio.create_task(pipeline.ingest())
        deadline = time.monotonic() + 3
        while pipeline.error is None and time.monotonic() < deadline:
            await asyncio.sleep(0.01)
        alive = not ingest.done()
        ingest.cancel()
        await asyncio.gather(ingest, return_exceptions=True)
        return pipeline, alive

    pipeline, alive = asyncio.run(scenario())
    assert alive, "ingest task died; no source would produce events until restart"
    assert pipeline.state == "stopped"
    assert pipeline.error


def test_paused_state_is_reported_only_after_the_queue_is_drained():
    class SlowStore(GatedStore):
        def write(self, event, segment_id=...):
            time.sleep(0.05)
            self.written.append(segment_id)
            return True

    async def scenario():
        store = SlowStore()
        pipeline = Pipeline(store, settings())
        await pipeline.control("start", SimulationConfig(speed=4))
        for tick in range(3):
            await pipeline.queue.put(
                (pipeline.session_generation, "s", 0.0, pipeline.provider.sample())
            )
        consume = asyncio.create_task(pipeline.consume())
        pause = asyncio.create_task(pipeline.control("pause"))
        observed = []
        while not pause.done():
            observed.append((pipeline.state, len(store.written)))
            await asyncio.sleep(0.005)
        consume.cancel()
        await asyncio.gather(consume, return_exceptions=True)
        await pipeline.provider.disconnect()
        return observed, len(store.written)

    observed, written = asyncio.run(scenario())
    assert written == 3
    assert all(count == written for state, count in observed if state == "paused")
