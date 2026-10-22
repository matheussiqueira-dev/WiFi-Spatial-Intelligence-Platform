"""Model registry: project artifacts re-verified on every read, external models as cards only."""

import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from app.domain.motion import checksum
from app.lab_contracts import COMMERCIAL_USE, ModelCard, ModelCardRequest, ProjectModel

MAX_PROJECT_ARTIFACTS = 200


def project_models(artifacts: Path) -> list[ProjectModel]:
    """Recompute each artifact's parameter checksum instead of trusting its filename."""
    models = []
    for path in sorted(artifacts.glob("model-*.json"))[:MAX_PROJECT_ARTIFACTS]:
        named = path.stem.removeprefix("model-")
        try:
            data = path.read_bytes()
            model = json.loads(data)
            parameters = {k: v for k, v in model.items() if k not in {"sha256", "id"}}
            intact = model["sha256"] == named == checksum(parameters)
            models.append(
                ProjectModel(
                    id=model["id"],
                    version=model["version"],
                    sha256=named,
                    size_bytes=len(data),
                    integrity="VERIFIED" if intact else "MISMATCH",
                )
            )
        except (OSError, ValueError, KeyError, TypeError):
            models.append(
                ProjectModel(
                    id="unreadable",
                    version="unknown",
                    sha256=named if len(named) == 64 else "0" * 64,
                    size_bytes=path.stat().st_size if path.exists() else 0,
                    integrity="UNREADABLE",
                )
            )
    return models


def model_card(request: ModelCardRequest) -> ModelCard:
    return ModelCard(
        **request.model_dump(),
        id=uuid4(),
        created_at=datetime.now(UTC),
        commercial_use=COMMERCIAL_USE[request.license],
    )
