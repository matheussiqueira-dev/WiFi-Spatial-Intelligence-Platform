"""Bounded synchronous experiments; never loads client-supplied model files."""

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter
from uuid import uuid4

from pydantic import Field, ValidationError

from app.contracts import StrictModel
from app.domain.motion import checksum, evaluate_baseline, prepare_dataset
from app.lab_contracts import ExperimentResult


class ExperimentRequest(StrictModel):
    seed: int = Field(default=42, ge=0, le=100000)


def write_artifact(target: Path, payload: str) -> None:
    """Content-addressed write; a torn file from an interrupted run is replaced, never kept."""
    data = payload.encode("utf-8")
    try:
        if target.read_bytes() == data:
            return
    except FileNotFoundError:
        pass
    temporary = target.with_name(f".{target.name}.{uuid4().hex}.tmp")
    try:
        with temporary.open("xb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)


class ModelLab:
    def __init__(self, store, artifacts: Path):
        self.store = store
        self.artifacts = artifacts

    def execute(self, request: ExperimentRequest, cancelled=lambda: False, progress=lambda _: None):
        if self.store.model_runs(1, 0)["total"] >= 100:
            raise ValueError("experiment capacity reached; export and review retention offline")
        start = perf_counter()
        progress("preparing")
        dataset = prepare_dataset(request.seed)
        if cancelled():
            return None
        progress("training")
        result = evaluate_baseline(dataset)
        if cancelled():
            return None
        progress("persisting")
        self.artifacts.mkdir(parents=True, exist_ok=True)
        # Server-computed hex digest only; no user path or serialized executable object.
        payload = json.dumps(dataset, sort_keys=True, allow_nan=False)
        write_artifact(self.artifacts / f"dataset-{checksum(dataset)}.json", payload)
        write_artifact(
            self.artifacts / f"model-{result['model']['sha256']}.json",
            json.dumps(result["model"], sort_keys=True, allow_nan=False),
        )
        result.update(
            {
                "id": str(uuid4()),
                "created_at": datetime.now(UTC).isoformat(),
                "seed": request.seed,
                "duration_ms": (perf_counter() - start) * 1000,
            }
        )
        try:
            ExperimentResult.model_validate(result)
        except ValidationError:
            # Contract drift is a server defect: nothing is persisted and no detail leaks.
            raise RuntimeError("experiment result violates its contract") from None
        self.store.save_model_run(result)
        return result
