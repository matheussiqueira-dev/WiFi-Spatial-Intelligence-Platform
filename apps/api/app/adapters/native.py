"""Translate the native domain scene to the versioned public API contract."""

import asyncio
from datetime import UTC, datetime
from uuid import uuid4

from app.contracts import Measurements, NativeEvent, NativeProvenance, SimulationConfig
from app.domain.acquisition import SyntheticScene
from app.ports.clock import Clock


class UtcClock:
    def now(self):
        return datetime.now(UTC)


class NativeProvider:
    streaming = False

    def __init__(self, config: SimulationConfig, clock: Clock | None = None):
        self.config = config
        self.clock = clock or UtcClock()
        self.scene = SyntheticScene(config.seed, config.occupants, config.scenario)
        self.tick = 0
        self.connected = False

    async def connect(self):
        self.connected = True

    async def disconnect(self):
        self.connected = False

    async def health(self):
        return {
            "connected": self.connected,
            "source_type": "SIMULATED",
            "provider": "synthetic-native",
        }

    async def read_events(self):
        while self.connected:
            event = self.sample()
            if event is not None:
                yield event
            await asyncio.sleep(0.5 / self.config.speed)

    def sample(self, timestamp=None):
        tick = self.tick
        self.tick += 1
        frame = self.scene.sample(tick)
        if self.config.scenario == "disconnect" and tick >= 5:
            self.connected = False
        if frame is None:
            return None
        return NativeEvent(
            event_id=uuid4(),
            timestamp=timestamp or self.clock.now(),
            measurements=Measurements(
                presence_detected=frame.presence,
                occupancy_estimate=frame.occupancy,
                ground_truth_positions=list(frame.positions),
            ),
            provenance=NativeProvenance(
                seed=self.config.seed, tick=tick, scenario=self.config.scenario
            ),
        )
