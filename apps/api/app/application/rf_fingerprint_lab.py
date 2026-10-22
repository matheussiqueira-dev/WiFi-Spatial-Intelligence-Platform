"""Reproducible L0 evaluation of the RF environment fingerprint over the SWF1 path.

Frames are encoded, authenticated and received exactly as a paired sensor's frames
would be, then fingerprinted. Results describe this synthetic channel model only.
"""

import hashlib
import json
import random
from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from uuid import UUID

from app.domain.csi_frame import CsiFrame, FrameReceiver, encode
from app.domain.rf_fingerprint import (
    MIN_FRAMES,
    SUBCARRIERS,
    WINDOW,
    Change,
    assess,
    calibrate,
    environment_frames,
)

START = datetime(2026, 1, 1, tzinfo=UTC)
REFERENCE_FRAMES = 400
WINDOWS = 40
LIMITATIONS = [
    "Canal sintético (perfil multipercurso fixo + 5% de ruído); não é CSI real.",
    "Indica apenas que o canal difere da referência; não identifica objeto, pessoa ou causa.",
    "Taxas são da avaliação sintética e não representam acurácia em ambientes reais.",
    "Mudanças pequenas (1–5% em poucas subportadoras) tendem a passar despercebidas.",
]


def transmit(frames: Sequence[CsiFrame], key: bytes) -> list[CsiFrame]:
    """SWF1 round trip: encode, authenticate, receive. Raises if any frame is refused."""
    receiver = FrameReceiver(
        {frames[0].device_id: key}, clock=lambda: frames[-1].timestamp + timedelta(seconds=1)
    )
    received = [receiver.receive(encode(frame, key)) for frame in frames]
    if receiver.rejected:
        raise RuntimeError(f"synthetic frames refused: {dict(receiver.rejected)}")
    return [frame for frame in received if frame is not None]


def evaluate(seed: int) -> dict:
    if not 0 <= seed <= 100000:
        raise ValueError("unsupported evaluation seed")
    device = UUID(int=seed + 1)
    key = hashlib.sha256(f"rf-lab-key:{seed}".encode()).digest()
    randomizer = random.Random(f"rf-lab:{seed}")
    sequence = 0

    def frames(count, frame_seed, environment=seed, change=None):
        nonlocal sequence
        batch = environment_frames(
            device,
            START + timedelta(seconds=sequence / 10),
            count,
            environment,
            frame_seed,
            change,
            first_sequence=sequence,
        )
        sequence += count
        return transmit(batch, key)

    model = calibrate(frames(REFERENCE_FRAMES, 0))
    normal = [assess(frames(WINDOW, 1 + i), model)[0] for i in range(WINDOWS)]
    changed = []
    for i in range(WINDOWS):
        width = randomizer.randint(4, 16)
        first = randomizer.randrange(SUBCARRIERS - width)
        factor = randomizer.choice([randomizer.uniform(1.15, 1.5), randomizer.uniform(0.6, 0.85)])
        change = Change(first, first + width - 1, factor)
        changed.append(assess(frames(WINDOW, 1000 + i, change=change), model)[0])
    subtle = []
    for i in range(WINDOWS):
        width = randomizer.randint(2, 6)
        first = randomizer.randrange(SUBCARRIERS - width)
        factor = randomizer.choice([randomizer.uniform(1.01, 1.05), randomizer.uniform(0.95, 0.99)])
        change = Change(first, first + width - 1, factor)
        subtle.append(assess(frames(WINDOW, 4000 + i, change=change), model)[0])
    shifted = [assess(frames(WINDOW, 2000 + i, environment=seed + 1), model)[0] for i in range(10)]
    sparse = [assess(frames(MIN_FRAMES - 1, 3000 + i), model)[0] for i in range(10)]
    digest = hashlib.sha256(
        json.dumps(
            {"mean": [round(v, 6) for v in model.fingerprint.mean], "threshold": model.threshold},
            sort_keys=True,
        ).encode()
    ).hexdigest()
    return {
        "method": "rf-fingerprint-zscore-v1",
        "evidence_level": "L0_SYNTHETIC",
        "transport": "SWF1",
        "seed": seed,
        "fingerprint_sha256": digest,
        "reference_frames": REFERENCE_FRAMES,
        "window_frames": WINDOW,
        "min_frames": MIN_FRAMES,
        "subcarriers": SUBCARRIERS,
        "threshold": model.threshold,
        "reference_scores_max": max(model.reference_scores),
        "normal_windows": len(normal),
        "false_positives": normal.count("CHANGED"),
        "false_positive_rate": normal.count("CHANGED") / len(normal),
        "changed_windows": len(changed),
        "detections": changed.count("CHANGED"),
        "detection_rate": changed.count("CHANGED") / len(changed),
        # Reported apart: small changes are expected to be missed by this baseline.
        "subtle_windows": len(subtle),
        "subtle_detection_rate": subtle.count("CHANGED") / len(subtle),
        "other_environment_windows": len(shifted),
        "other_environment_detection_rate": shifted.count("CHANGED") / len(shifted),
        "sparse_windows": len(sparse),
        "abstained": sparse.count("ABSTAIN"),
        "frames_received": sequence,
        "limitations": LIMITATIONS,
    }
