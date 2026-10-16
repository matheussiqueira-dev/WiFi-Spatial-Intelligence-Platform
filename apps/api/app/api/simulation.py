"""Session controls, source selection and persisted event history."""

import asyncio

from fastapi import APIRouter, HTTPException, Query

from app.api.deps import ContainerDep, ProtectiveDenial, gated
from app.contracts import SimulationConfig, SourceSelection
from app.domain.acquisition import SCENARIOS

router = APIRouter(dependencies=gated("spatial.presence"))


@router.get("/api/v1/events")
async def events(
    c: ContainerDep,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0, le=100000),
):
    return await asyncio.to_thread(c.store.history, limit, offset)


@router.delete("/api/v1/events/synthetic")
async def delete_events(c: ContainerDep):
    try:
        await c.pipeline.delete_history()
    except ValueError as error:
        raise ProtectiveDenial(str(error)) from error
    return {"deleted": "L0_SYNTHETIC", "audit_preserved": True}


@router.get("/api/v1/simulation/scenarios")
def scenarios():
    return list(SCENARIOS)


@router.post("/api/v1/simulation/start")
async def start(config: SimulationConfig, c: ContainerDep):
    try:
        await c.pipeline.control("start", config)
    except ValueError as error:
        raise HTTPException(409, str(error)) from error
    return c.pipeline.status()


@router.post("/api/v1/sources/select")
async def select_source(selection: SourceSelection, c: ContainerDep):
    try:
        await c.pipeline.select_source(selection.source)
    except ValueError as error:
        raise ProtectiveDenial(str(error)) from error
    return c.pipeline.status()


# Registered after /simulation/start so the literal path keeps precedence.
@router.post("/api/v1/simulation/{action}")
async def control(action: str, c: ContainerDep):
    if action not in {"pause", "resume", "stop", "reset"}:
        raise HTTPException(404, "unknown simulation action")
    try:
        await c.pipeline.control(action)
    except ValueError as error:
        raise HTTPException(409, str(error)) from error
    return c.pipeline.status()
