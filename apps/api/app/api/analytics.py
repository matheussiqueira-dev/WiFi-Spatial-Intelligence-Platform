"""Historical analytics, replay, export and saved reports over persisted observations."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from app.analytics import AnalyticsQuery, aggregate, csv_report, replay_page
from app.api.deps import ContainerDep, protected
from app.bootstrap import Container
from app.ports.history import HistorySelection

router = APIRouter(dependencies=protected)


def selection(query: AnalyticsQuery) -> HistorySelection:
    return HistorySelection(
        query.start, query.end, query.source_id, query.scenario, query.segment_id
    )


def analysis_rows(c: Container, query: AnalyticsQuery):
    try:
        return c.history.execute(selection(query))
    except ValueError as error:
        raise HTTPException(422, str(error)) from error


@router.get("/api/v1/analytics")
def analytics(query: Annotated[AnalyticsQuery, Query()], c: ContainerDep):
    return aggregate(analysis_rows(c, query), query)


@router.get("/api/v1/analytics/replay")
def analytics_replay(query: Annotated[AnalyticsQuery, Query()], c: ContainerDep):
    try:
        rows, total = c.history.page(selection(query), query.offset, query.limit)
    except ValueError as error:
        raise HTTPException(422, str(error)) from error
    return replay_page(rows, total, query)


@router.get("/api/v1/analytics/export.csv")
def analytics_export(query: Annotated[AnalyticsQuery, Query()], c: ContainerDep):
    return Response(
        csv_report(aggregate(analysis_rows(c, query), query)),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="synthetic-analytics.csv"'},
    )


@router.post("/api/v1/analytics/reports")
def save_analytics(query: AnalyticsQuery, c: ContainerDep):
    report = aggregate(analysis_rows(c, query), query)
    return {"id": c.store.save_report(report), "evidence_level": "L0_SYNTHETIC"}


@router.get("/api/v1/analytics/reports")
def list_reports(
    c: ContainerDep,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0, le=10000),
):
    return c.store.reports(limit, offset)


@router.get("/api/v1/analytics/reports/{identifier}")
def get_report(identifier: str, c: ContainerDep):
    result = c.store.report(identifier)
    if result is None:
        raise HTTPException(404, "report not found")
    return result
