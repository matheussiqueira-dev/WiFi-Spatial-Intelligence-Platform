"""Model registry and RF environment fingerprint evaluation (synthetic, L0)."""

import asyncio

from fastapi import HTTPException

from app.adapters.sqlite.lab import MAX_REGISTERED_MODELS
from app.api.deps import ContainerDep, GatedRouter, admin, operator, viewer
from app.application.model_registry import model_card, project_models
from app.application.rf_fingerprint_lab import evaluate
from app.lab_contracts import (
    ModelCard,
    ModelCardRequest,
    ModelRegistry,
    RfFingerprintEvaluation,
    RfFingerprintRequest,
)

registry = GatedRouter("lab.model_registry")
fingerprint = GatedRouter("spatial.rf_fingerprint")


@registry.get("/api/v1/model-lab/models", response_model=ModelRegistry, dependencies=viewer)
async def list_models(c: ContainerDep):
    project = await asyncio.to_thread(project_models, c.model_lab.artifacts)
    return ModelRegistry(
        project=project,
        third_party=[ModelCard.model_validate(card) for card in c.store.registered_models()],
        maximum_third_party=MAX_REGISTERED_MODELS,
    )


@registry.post("/api/v1/model-lab/models", response_model=ModelCard, dependencies=admin)
async def register_model(request: ModelCardRequest, c: ContainerDep):
    card = model_card(request)
    try:
        await asyncio.to_thread(c.store.register_model, card.model_dump(mode="json"))
    except ValueError as error:
        raise HTTPException(409, str(error)) from error
    return card


@registry.delete("/api/v1/model-lab/models/{identifier}", dependencies=admin)
async def unregister_model(identifier: str, c: ContainerDep):
    if not await asyncio.to_thread(c.store.unregister_model, identifier):
        raise HTTPException(404, "model card not found")
    return {"removed": True}


@fingerprint.post(
    "/api/v1/model-lab/rf-fingerprint/evaluations",
    response_model=RfFingerprintEvaluation,
    dependencies=operator,
)
async def evaluate_fingerprint(request: RfFingerprintRequest):
    # Deterministic for a seed and bounded (~2.700 synthetic frames): nothing is stored.
    return await asyncio.to_thread(evaluate, request.seed)
