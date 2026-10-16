"""Project-native synthetic scene. Pure domain; no HTTP, ORM or external engine."""

import random
from dataclasses import dataclass


@dataclass(frozen=True)
class MeasurementFrame:
    presence: bool
    occupancy: int
    positions: tuple[tuple[float, float], ...]
    evidence_level: str = "L0_SYNTHETIC"


@dataclass(frozen=True)
class SyntheticScene:
    seed: int = 42
    occupants: int = 2
    scenario: str = "walking"

    def __post_init__(self):
        if not 0 <= self.seed < 2**32 or not 0 <= self.occupants <= 20:
            raise ValueError("invalid synthetic scene bounds")
        if self.scenario not in {
            "empty",
            "stationary",
            "walking",
            "entering",
            "leaving",
            "interference",
            "packet_loss",
            "disconnect",
        }:
            raise ValueError("unsupported scene")

    def sample(self, tick: int) -> MeasurementFrame | None:
        if tick < 0:
            raise ValueError("tick must be nonnegative")
        randomizer = random.Random(f"native-scene-v1:{self.seed}:{tick}")
        if self.scenario == "disconnect" and tick >= 5:
            return None
        if self.scenario == "packet_loss" and randomizer.random() < 0.3:
            return None
        count = self.occupants
        if self.scenario == "empty":
            count = 0
        elif self.scenario == "entering":
            count = min(count, tick // 3)
        elif self.scenario == "leaving":
            count = max(0, count - tick // 3)
        positions = []
        for index in range(count):
            if self.scenario == "stationary":
                x, y = 1 + index % 5 * 1.4, 1 + index // 5 * 1.2
            else:
                # Triangle-wave paths in a rectangle, not an RF propagation model.
                x = 8 - abs((tick * 0.17 + index * 1.3) % 16 - 8)
                y = 6 - abs((tick * 0.11 + index * 0.9 + 2) % 12 - 6)
            if self.scenario == "interference":
                x = min(8, max(0, x + randomizer.uniform(-0.3, 0.3)))
                y = min(6, max(0, y + randomizer.uniform(-0.3, 0.3)))
            positions.append((round(x, 3), round(y, 3)))
        return MeasurementFrame(count > 0, count, tuple(positions))
