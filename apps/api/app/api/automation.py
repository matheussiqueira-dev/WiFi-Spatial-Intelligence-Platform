"""Dry-run local rules: no dispatch, decisions only over persisted L0 events."""

import asyncio

from fastapi import APIRouter, HTTPException, Query

from app.api.deps import ContainerDep, gated
from app.rule_contracts import RuleRequest

router = APIRouter(dependencies=gated("automation.dry_run_rules"))


@router.post("/api/v1/automation/rules")
async def create_rule(rule: RuleRequest, c: ContainerDep):
    async with c.rules_lock:
        try:
            return await asyncio.to_thread(c.store.create_rule, rule.model_dump())
        except ValueError as error:
            raise HTTPException(422, str(error)) from error


@router.get("/api/v1/automation/rules")
def get_rules(c: ContainerDep):
    return c.store.local_rules()


@router.post("/api/v1/automation/rules/{identifier}/revoke")
async def revoke_rule(identifier: str, c: ContainerDep):
    # Same lock as ingestion: no in-flight decision can commit after revocation returns.
    async with c.pipeline.quiesced():
        if not await asyncio.to_thread(c.store.revoke_rule, identifier):
            raise HTTPException(404, "rule not found")
    return {"revoked": True, "mode": "DRY_RUN"}


@router.get("/api/v1/automation/decisions")
def get_decisions(
    c: ContainerDep,
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0, le=1000),
):
    return c.store.rule_decisions(limit, offset)
