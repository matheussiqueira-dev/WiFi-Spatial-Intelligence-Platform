"""RF environment fingerprint baseline over SWF1 frames (synthetic only, L0).

A fingerprint is the per-subcarrier mean and spread of CSI amplitude in a reference
period. A later window is compared by the mean absolute z-score of its subcarrier
means; the decision threshold is calibrated on held-out reference windows. The method
says only that the channel differs from the reference. It never names what changed
(furniture, a door, a person) and synthetic scores are not real-world accuracy.
"""

import math
import random
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta
from statistics import fmean, pstdev
from uuid import UUID

from app.domain.csi_frame import CsiFrame

SUBCARRIERS = 64
WINDOW = 20
MIN_FRAMES = 12
NOISE = 0.05
THRESHOLD_MARGIN = 1.5


@dataclass(frozen=True)
class Change:
    """Multiplicative amplitude change on a contiguous band of subcarriers."""

    first: int
    last: int
    factor: float


def environment_frames(
    device: UUID,
    start: datetime,
    count: int,
    environment_seed: int,
    frame_seed: int,
    change: Change | None = None,
    first_sequence: int = 0,
) -> list[CsiFrame]:
    """Deterministic synthetic channel: a fixed multipath profile plus 5% amplitude noise."""
    profile_random = random.Random(f"rf-environment:{environment_seed}")
    paths = [
        (profile_random.uniform(0.5, 4), profile_random.uniform(0, 2 * math.pi)) for _ in range(3)
    ]
    profile = [
        600 + sum(200 * math.sin(2 * math.pi * k * f / SUBCARRIERS + p) for f, p in paths) / 3
        for k in range(SUBCARRIERS)
    ]
    noise = random.Random(f"rf-frames:{environment_seed}:{frame_seed}")
    frames = []
    for index in range(count):
        iq = []
        for k, base in enumerate(profile):
            amplitude = base * (1 + noise.gauss(0, NOISE))
            if change and change.first <= k <= change.last:
                amplitude *= change.factor
            phase = noise.uniform(0, 2 * math.pi)
            iq.append(
                (
                    max(-32768, min(32767, round(amplitude * math.cos(phase)))),
                    max(-32768, min(32767, round(amplitude * math.sin(phase)))),
                )
            )
        frames.append(
            CsiFrame(
                device_id=device,
                sequence=first_sequence + index,
                timestamp=start + timedelta(milliseconds=100 * index),
                channel=149,
                bandwidth_mhz=80,
                rssi_dbm=-55,
                noise_floor_dbm=-95,
                synthetic=True,
                iq=tuple(iq),
            )
        )
    return frames


def amplitudes(frame: CsiFrame) -> list[float]:
    return [math.hypot(i, q) for i, q in frame.iq]


@dataclass(frozen=True)
class Fingerprint:
    mean: tuple[float, ...]
    spread: tuple[float, ...]
    frames: int


def build(frames: Sequence[CsiFrame]) -> Fingerprint:
    if len(frames) < 2 * WINDOW:
        raise ValueError("reference needs at least two windows of frames")
    rows = [amplitudes(frame) for frame in frames]
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise ValueError("reference frames must share the subcarrier layout")
    columns = list(zip(*rows))
    return Fingerprint(
        mean=tuple(fmean(column) for column in columns),
        # A floor keeps a perfectly flat synthetic subcarrier from dividing by zero.
        spread=tuple(max(pstdev(column), 1.0) for column in columns),
        frames=len(frames),
    )


def distance(window: Sequence[CsiFrame], reference: Fingerprint) -> float:
    rows = [amplitudes(frame) for frame in window]
    if any(len(row) != len(reference.mean) for row in rows):
        raise ValueError("window does not match the fingerprint layout")
    scale = math.sqrt(len(rows))
    return fmean(
        abs(fmean(column) - mean) / (spread / scale)
        for column, mean, spread in zip(zip(*rows), reference.mean, reference.spread)
    )


@dataclass(frozen=True)
class Calibrated:
    fingerprint: Fingerprint
    threshold: float
    reference_scores: tuple[float, ...]


def calibrate(frames: Sequence[CsiFrame]) -> Calibrated:
    """First half builds the fingerprint; held-out windows of the second half set the bar."""
    half = len(frames) // 2
    fingerprint = build(frames[:half])
    held_out = [frames[i : i + WINDOW] for i in range(half, len(frames) - WINDOW + 1, WINDOW)]
    if len(held_out) < 3:
        raise ValueError("reference needs at least three held-out windows")
    scores = tuple(distance(window, fingerprint) for window in held_out)
    return Calibrated(fingerprint, max(scores) * THRESHOLD_MARGIN, scores)


def assess(window: Sequence[CsiFrame], model: Calibrated) -> tuple[str, float | None]:
    if len(window) < MIN_FRAMES:
        return "ABSTAIN", None
    score = distance(window, model.fingerprint)
    return ("CHANGED" if score > model.threshold else "NORMAL"), score
