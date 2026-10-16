import asyncio
import logging
import time
from collections import deque
from uuid import uuid4

from app.adapters.providers import build_provider
from app.config import Settings
from app.contracts import SimulationConfig
from app.storage import Store

logger = logging.getLogger("spatial.pipeline")


class Pipeline:
    def __init__(self, store: Store, settings: Settings | None = None):
        self.store = store
        self.settings = settings
        self.source = "synthetic-native"
        self.provider = build_provider(self.source, SimulationConfig(), settings)
        self.state = "stopped"
        self.queue = asyncio.Queue(maxsize=64)
        self.subscribers: set[asyncio.Queue] = set()
        self.latest = None
        self.produced = 0
        self.dropped = 0
        self.delivery_attempts = 0
        self.error = None
        self.tasks = []
        self.control_lock = asyncio.Lock()
        self.session_generation = 0
        # Items queued before this generation belong to a failed session and are dropped.
        self.discard_before = 0
        self.measurements = deque(maxlen=2000)
        self.telemetry_started = time.monotonic()

    async def select_source(self, source: str):
        async with self.control_lock:
            if self.state != "stopped":
                raise ValueError("stop the session before changing source")
            if source not in {"synthetic-native", "SIMULATED", "RUVIEW_STREAM"}:
                raise ValueError("unsupported source")
            source = "synthetic-native" if source == "SIMULATED" else source
            candidate = build_provider(source, SimulationConfig(), self.settings)
            await self.provider.disconnect()
            await self.queue.join()
            self.session_generation += 1
            self.source = source
            self.provider = candidate
            self.latest = None
            self.error = None
            self.produced = 0
            self.dropped = 0
            self.delivery_attempts = 0
            await asyncio.to_thread(self.store.audit, f"source.select.{source}")

    def _new_provider(self, config):
        return build_provider(self.source, config, self.settings)

    async def start_tasks(self):
        self.tasks = [asyncio.create_task(self.ingest()), asyncio.create_task(self.consume())]

    async def close(self):
        self.tasks[0].cancel()
        await asyncio.gather(self.tasks[0], return_exceptions=True)
        await self.queue.join()
        self.tasks[1].cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)
        await self.provider.disconnect()

    async def control(self, action: str, config: SimulationConfig | None = None):
        async with self.control_lock:
            await self._control(action, config)

    async def _control(self, action: str, config: SimulationConfig | None = None):
        if action == "start":
            if self.state != "stopped":
                raise ValueError("stop the simulation before starting a new session")
            # Settle any backlog of an abnormally ended session before counters reset.
            await self.queue.join()
            self.session_generation += 1
            self.store.segment_id = str(uuid4())
            self.provider = self._new_provider(config or SimulationConfig())
            await self.provider.connect()
            self.state = "running"
            self.error = None
            self.latest = None
            self.produced = 0
            self.dropped = 0
            self.delivery_attempts = 0
        elif action == "pause" and self.state == "running":
            self.state = "paused"
            self.session_generation += 1
        elif action == "resume" and self.state == "paused":
            self.session_generation += 1
            self.state = "running"
            self.store.segment_id = str(uuid4())
        elif action in {"stop", "reset"}:
            self.state = "stopped"
            self.session_generation += 1
            await self.provider.disconnect()
            if action == "reset":
                self.provider.tick = 0
                self.latest = None
        else:
            raise ValueError("invalid simulation state transition")
        if self.state != "running":
            await self.queue.join()
        if action == "reset":
            self.latest = None
        await asyncio.to_thread(self.store.audit, f"simulation.{action}")

    async def delete_history(self):
        async with self.control_lock:
            if self.state != "stopped":
                raise ValueError("stop simulation before deleting history")
            await self.queue.join()
            await asyncio.to_thread(self.store.delete_synthetic)
            self.latest = None

    async def ingest(self):
        while True:
            provider = self.provider
            generation = self.session_generation
            event = None
            # Network I/O must never hold the control lock (stop/pause stay responsive).
            if provider.streaming and self.state in {"running", "paused"}:
                event = await provider.next_event()
            async with self.control_lock:
                if self.state == "running" and generation == self.session_generation:
                    if not provider.streaming:
                        event = provider.sample()
                    if not provider.streaming and not provider.connected:
                        self.state = "stopped"
                        self.error = "Simulated sensor disconnected; start a new session."
                    if event:
                        await self.queue.put(
                            (generation, self.store.segment_id, time.perf_counter(), event)
                        )
            await asyncio.sleep(0.01 if provider.streaming else 0.5 / provider.config.speed)

    async def consume(self):
        while True:
            generation, segment_id, started, event = await self.queue.get()
            try:
                if generation < self.discard_before:
                    continue
                event.processing_latency_ms = (time.perf_counter() - started) * 1000
                persisted = await asyncio.to_thread(self.store.write, event, segment_id)
                if persisted is False:
                    if self.provider.streaming:
                        self.provider.duplicates += 1
                    continue
                self.latest = event.model_dump(mode="json")
                self.produced += 1
                self.measurements.append((time.monotonic(), event.processing_latency_ms))
                for queue in tuple(self.subscribers):
                    self.delivery_attempts += 1
                    if queue.full():
                        queue.get_nowait()
                        self.dropped += 1
                    queue.put_nowait(self.latest)
            except Exception:
                logger.exception("event.persistence_failed")
                self.error = "Event persistence failed. Check backend logs."
                self.state = "stopped"
                self.session_generation += 1
                self.discard_before = self.session_generation
                await self.provider.disconnect()
            finally:
                self.queue.task_done()

    def status(self):
        # tuple() copies the deque atomically; routes may call this from the threadpool.
        samples = tuple(self.measurements)
        latest = self.latest
        recent = [item for item in samples if item[0] >= time.monotonic() - 60]
        latencies = sorted(item[1] for item in recent)
        window = min(60, max(0.001, time.monotonic() - self.telemetry_started))
        return {
            "metrics": {
                "window_seconds": window,
                "event_rate": len(recent) / window,
                "queue_depth": self.queue.qsize(),
                "visualization_drops": self.dropped,
                "visualization_drop_rate": self.dropped / self.delivery_attempts
                if self.delivery_attempts
                else None,
                "last_seen": latest["timestamp"] if latest else None,
                "reconnections": self.provider.diagnostics()["reconnections"]
                if self.provider.streaming
                else 0,
                "queue_wait_p50_ms": latencies[int((len(latencies) - 1) * 0.5)]
                if latencies
                else None,
                "queue_wait_p95_ms": latencies[int((len(latencies) - 1) * 0.95)]
                if latencies
                else None,
                "segment_id": self.store.segment_id,
                "rf_drop_rate": None,
            },
            "state": self.state,
            "provider": self.source,
            "legacy_lab_enabled": bool(self.settings and self.settings.legacy_lab_enabled),
            "evidence_level": "L0_SYNTHETIC",
            "latest": latest,
            "produced_events": self.produced,
            "dropped_visualization_events": self.dropped,
            "queue_depth": self.queue.qsize(),
            "error": self.error,
            "config": self.provider.config.model_dump(),
            "connected": self.provider.connected,
            "source_diagnostics": self.provider.diagnostics() if self.provider.streaming else None,
        }
