"""Synthetic geometric baseline experiments and their bounded job queue."""

import asyncio

from fastapi import HTTPException, Query

from app.api.deps import ContainerDep, GatedRouter, ProtectiveDenial, operator, viewer
from app.application.model_lab import ExperimentRequest
from app.lab_contracts import ExperimentResult

router = GatedRouter("spatial.activity_baseline")


@router.post("/api/v1/model-lab/jobs", dependencies=operator)
async def submit_experiment(query: ExperimentRequest, c: ContainerDep):
    try:
        return await c.experiment_jobs.submit(query)
    except ValueError as error:
        raise ProtectiveDenial(str(error)) from error


@router.get("/api/v1/model-lab/jobs/{identifier}", dependencies=viewer)
def get_job(identifier: str, c: ContainerDep):
    if c.experiment_jobs.last_error:
        raise HTTPException(503, "job status persistence unavailable")
    job = c.store.job(identifier)
    if job is None:
        raise HTTPException(404, "job not found")
    return job


@router.post("/api/v1/model-lab/jobs/{identifier}/cancel", dependencies=operator)
def cancel_job(identifier: str, c: ContainerDep):
    if not c.experiment_jobs.cancel(identifier):
        raise HTTPException(409, "job is already terminal or absent")
    return {"cancel_requested": True}


@router.post("/api/v1/model-lab/runs", response_model=ExperimentResult, dependencies=operator)
async def run_experiment(query: ExperimentRequest, c: ContainerDep):
    if c.model_lock.locked():
        raise ProtectiveDenial("one experiment at a time")
    async with c.model_lock:
        try:
            return await asyncio.to_thread(c.model_lab.execute, query)
        except ValueError as error:
            raise HTTPException(422, str(error)) from error


@router.get("/api/v1/model-lab/runs", dependencies=viewer)
def list_experiments(
    c: ContainerDep,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0, le=100),
):
    return c.store.model_runs(limit, offset)


@router.get(
    "/api/v1/model-lab/runs/{identifier}", response_model=ExperimentResult, dependencies=viewer
)
def get_experiment(identifier: str, c: ContainerDep):
    result = c.store.model_run(identifier)
    if result is None:
        raise HTTPException(404, "experiment not found")
    return result
