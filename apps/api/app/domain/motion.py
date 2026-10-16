"""CPU baseline on virtual geometry only. Reference labels never enter prediction."""

import hashlib
import json
import math
from statistics import mean

from app.domain.acquisition import SyntheticScene

CLASSES = ("stationary", "walking", "unknown")


def checksum(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


def extract_window(points: list[tuple[float, float, float]]) -> float | None:
    if len(points) < 3:
        return None
    speeds = []
    for (t0, x0, y0), (t1, x1, y1) in zip(points, points[1:]):
        if not all(math.isfinite(v) for v in (t0, x0, y0, t1, x1, y1)):
            return None
        delta = t1 - t0
        if not 0 < delta <= 2 or not (
            0 <= x0 <= 8 and 0 <= y0 <= 6 and 0 <= x1 <= 8 and 0 <= y1 <= 6
        ):
            return None
        speeds.append(math.hypot(x1 - x0, y1 - y0) / delta)
    return mean(speeds)


def prepare_dataset(seed: int):
    if not 0 <= seed <= 100000:
        raise ValueError("unsupported dataset seed")
    dataset = {name: [] for name in ("train", "validation", "test")}
    for split_index, split in enumerate(dataset):
        for session in range(8):
            reference = "walking" if session % 2 else "stationary"
            session_seed = seed * 100 + split_index * 10 + session
            scene = SyntheticScene(seed=session_seed, occupants=1, scenario=reference)
            spacing = 0.5 + 0.2 * split_index + 0.02 * (session % 5)
            for window in range(4):
                first_tick = 4 + split_index * 1000 + session * 60 + window * 12
                points = []
                for tick in range(first_tick, first_tick + 8):
                    frame = scene.sample(tick)
                    x, y = frame.positions[0]
                    points.append((tick * spacing, x, y))
                # A missing observation tests abstention, never a fabricated RF quality.
                if window == 3:
                    points[-1] = (points[-1][0] + 10, *points[-1][1:])
                dataset[split].append(
                    {
                        "session_id": f"virtual-{session_seed}",
                        "sample_spacing": spacing,
                        "window": window,
                        "points": points,
                        "reference": reference,
                    }
                )
    return dataset


def predict(speed: float | None, threshold: float) -> str:
    if speed is None or abs(speed - threshold) < threshold * 0.1:
        return "unknown"
    return "walking" if speed > threshold else "stationary"


def evaluate_baseline(dataset):
    sessions = [{row["session_id"] for row in dataset[split]} for split in dataset]
    if any(a & b for index, a in enumerate(sessions) for b in sessions[index + 1 :]):
        raise ValueError("session leakage across splits")
    train = [(extract_window(r["points"]), r["reference"]) for r in dataset["train"]]
    values = sorted({speed for speed, _ in train if speed is not None})
    if len(values) < 2 or {label for _, label in train} != set(CLASSES[:2]):
        raise ValueError("both distinguishable training classes are required")
    candidates = [(a + b) / 2 for a, b in zip(values, values[1:])]
    threshold = min(
        candidates,
        key=lambda t: (
            sum(predict(speed, t) != label for speed, label in train if speed is not None),
            t,
        ),
    )
    parameters = {
        "version": "geometry-speed-v1",
        "threshold_m_per_s": threshold,
        "features": ["mean_virtual_speed_m_per_s"],
        "abstention_margin": 0.1,
    }
    model = {**parameters, "sha256": checksum(parameters), "id": "geometry-motion-v1"}

    def evaluate(split):
        matrix = [[0] * 3 for _ in CLASSES]
        predictions = []
        for row in dataset[split]:
            speed = extract_window(row["points"])
            label = predict(speed, threshold)
            matrix[CLASSES.index(row["reference"])][CLASSES.index(label)] += 1
            predictions.append(
                {
                    "session_id": row["session_id"],
                    "window": row["window"],
                    "prediction": label,
                    "reference": row["reference"],
                    "quality": "gap" if speed is None else "complete",
                    "mean_speed": speed,
                    "start_seconds": row["points"][0][0],
                    "end_seconds": row["points"][-1][0],
                }
            )
        total = len(predictions)
        rejected = sum(p["prediction"] == "unknown" for p in predictions)
        accepted = total - rejected
        correct = sum(p["prediction"] == p["reference"] for p in predictions)
        stationary = sum(p["reference"] == "stationary" for p in predictions)
        false_positive = sum(
            p["reference"] == "stationary" and p["prediction"] == "walking" for p in predictions
        )
        return {
            "classes": CLASSES,
            "confusion_matrix": matrix,
            "samples": total,
            "support": {c: sum(p["reference"] == c for p in predictions) for c in CLASSES},
            "rejected": rejected,
            "rejection_rate": rejected / total if total else None,
            "accuracy_accepted": correct / accepted if accepted else None,
            "false_positive_rate": false_positive / stationary if stationary else None,
            "predictions": predictions,
        }

    return {
        "model": model,
        "dataset_sha256": checksum(dataset),
        "dataset_version": "virtual-motion-v1",
        "evidence_level": "L0_SYNTHETIC",
        "validation": evaluate("validation"),
        "evaluation": evaluate("test"),
        "splits": {name: sorted({r["session_id"] for r in rows}) for name, rows in dataset.items()},
        "unsupported": ["sitting", "possible_fall", "rf_fingerprint", "vitals", "pose"],
        "limitation": "Virtual single-point geometry; no RF, human activity or real accuracy.",
    }
