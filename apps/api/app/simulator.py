import asyncio
import math
import random
from datetime import UTC, datetime
from typing import AsyncIterator, Protocol
from uuid import uuid4

from app.contracts import Measurements, Provenance, SensingEvent, SimulationConfig


class SensingProvider(Protocol):
    async def connect(self) -> None: ...
    def read_events(self) -> AsyncIterator[SensingEvent]: ...
    async def health(self) -> dict: ...
    async def disconnect(self) -> None: ...


class SimulationProvider:
    """Deterministic scene truth, not a physical CSI or model prediction simulator."""

    def __init__(self, config: SimulationConfig):
        self.config = config
        self.tick = 0
        self.connected = False

    async def connect(self):
        self.connected = True

    async def disconnect(self):
        self.connected = False

    async def health(self):
        return {"connected": self.connected, "source_type": "SIMULATED"}

    async def read_events(self):
        while self.connected:
            event = self.sample()
            if event is not None:
                yield event
            await asyncio.sleep(0.5 / self.config.speed)

    def sample(self, timestamp: datetime | None = None):
        tick = self.tick
        self.tick += 1
        rng = random.Random(self.config.seed + tick)
        scenario = self.config.scenario
        if scenario == "disconnect" and tick >= 5:
            self.connected = False
            return None
        if scenario == "packet_loss" and rng.random() < 0.3:
            return None
        count = self.config.occupants
        if scenario == "empty":
            count = 0
        elif scenario == "entering":
            count = min(count, tick // 3)
        elif scenario == "leaving":
            count = max(0, count - tick // 3)
        positions = [
            (
                round(4 + 2.5 * math.sin((tick if scenario != "stationary" else 0) * 0.12 + i), 3),
                round(
                    3 + 1.8 * math.cos(tick * 0.09 + i) if scenario != "stationary" else 1 + i % 5,
                    3,
                ),
            )
            for i in range(count)
        ]
        if scenario == "interference":
            positions = [
                (
                    round(max(0, min(8, x + rng.uniform(-0.4, 0.4))), 3),
                    round(max(0, min(6, y + rng.uniform(-0.4, 0.4))), 3),
                )
                for x, y in positions
            ]
        return SensingEvent(
            event_id=uuid4(),
            timestamp=timestamp or datetime.now(UTC),
            measurements=Measurements(
                presence_detected=count > 0,
                occupancy_estimate=count,
                ground_truth_positions=positions,
            ),
            provenance=Provenance(seed=self.config.seed, tick=tick, scenario=scenario),
        )
