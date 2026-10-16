import csv
import io
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy import Engine

from app.adapters.network_store import NetworkStore
from app.api.deps import require_capability
from app.application.channel_plan import plan
from app.application.network_diagnostics import summarize
from app.network_contracts import (
    ChannelPlan,
    ChannelSurvey,
    NetworkComparison,
    NetworkConfiguration,
    NetworkReport,
    NetworkSample,
)


def network_router(engine: Engine, dependencies: list) -> APIRouter:
    router = APIRouter(
        prefix="/api/v1/network", tags=["Network diagnostics"], dependencies=dependencies
    )
    store = NetworkStore(engine)

    @router.post("/samples")
    def ingest(sample: NetworkSample):
        age = (datetime.now(UTC) - sample.timestamp).total_seconds()
        if not -5 <= age <= 120:
            raise HTTPException(422, "sample must be recent UTC host telemetry")
        try:
            return {"inserted": store.save(sample)}
        except ValueError as error:
            raise HTTPException(409, str(error)) from error

    channel = [require_capability("network.channel_plan")]

    @router.post("/channel-surveys", dependencies=channel)
    def ingest_survey(survey: ChannelSurvey):
        age = (datetime.now(UTC) - survey.timestamp).total_seconds()
        if not -5 <= age <= 120:
            raise HTTPException(422, "survey must be recent UTC host telemetry")
        try:
            return {"inserted": store.save_survey(survey)}
        except ValueError as error:
            raise HTTPException(409, str(error)) from error

    @router.get("/channel-plan", response_model=ChannelPlan, dependencies=channel)
    def channel_plan(
        hours: float = Query(1, ge=1 / 60, le=24),
        location: str | None = Query(None, max_length=48),
    ):
        now = datetime.now(UTC)
        start = now - timedelta(hours=hours)
        try:
            surveys = store.read_surveys(start, now, location)
            samples = store.read(start, now)
        except ValueError as error:
            raise HTTPException(422, str(error)) from error
        connected = [
            row
            for row in samples
            if row.link_state == "CONNECTED" and (location is None or row.location == location)
        ]
        current = connected[-1].channel if connected else None
        return plan(surveys, current, start, now, location)

    @router.get("/config", response_model=NetworkConfiguration)
    def configuration():
        return NetworkConfiguration(location=store.configuration())

    @router.post("/config", response_model=NetworkConfiguration)
    def configure(config: NetworkConfiguration):
        try:
            store.configure(config.location)
        except ValueError as error:
            raise HTTPException(409, str(error)) from error
        return config

    def report(hours: float, location: str | None, limit: int, offset: int) -> NetworkReport:
        now = datetime.now(UTC)
        start = now - timedelta(hours=hours)
        try:
            all_rows = store.read(start, now)
        except ValueError as error:
            raise HTTPException(422, str(error)) from error
        rows = [row for row in all_rows if location is None or row.location == location]
        comparisons = [
            NetworkComparison(
                location=label,
                summary=summarize([row for row in all_rows if row.location == label], now),
            )
            for label in sorted({row.location for row in all_rows})[:20]
        ]
        return NetworkReport(
            start=start,
            end=now,
            summary=summarize(rows, now),
            latest=rows[-1] if rows else None,
            items=list(reversed(rows))[offset : offset + limit],
            total=len(rows),
            limit=limit,
            offset=offset,
            locations=store.locations(),
            comparisons=comparisons,
            configured_location=store.configuration(),
        )

    @router.get("/report", response_model=NetworkReport)
    def get_report(
        hours: float = Query(24, ge=1 / 60, le=24),
        location: str | None = Query(None, max_length=48),
        limit: int = Query(100, ge=1, le=200),
        offset: int = Query(0, ge=0, le=10000),
    ):
        return report(hours, location, limit, offset)

    @router.get("/export.csv")
    def export(
        hours: float = Query(24, ge=1 / 60, le=24),
        location: str | None = Query(None, max_length=48),
    ):
        result = report(hours, location, 200, 0)
        # Export the whole bounded window, never just the UI page.
        rows = store.read(result.start, result.end)
        output = io.StringIO(newline="")
        writer = csv.writer(output)
        writer.writerow(
            [
                "timestamp_utc",
                "location",
                "link_state",
                "signal_percent",
                "gateway_probes",
                "gateway_replies",
                "evidence_level",
                "channel",
                "radio_type",
                "rx_mbps",
                "tx_mbps",
                "gateway_rtt_ms",
                "collector_error",
            ]
        )
        for row in rows:
            if location is None or row.location == location:
                writer.writerow(
                    [
                        row.timestamp.isoformat(),
                        row.location,
                        row.link_state,
                        row.signal_percent,
                        row.probe_sent,
                        len(row.probe_rtt_ms),
                        row.evidence_level,
                        row.channel,
                        row.radio_type,
                        row.rx_mbps,
                        row.tx_mbps,
                        ";".join(str(value) for value in row.probe_rtt_ms),
                        row.collector_error,
                    ]
                )
        return Response(
            output.getvalue(),
            media_type="text/csv",
            headers={
                "Content-Disposition": 'attachment; filename="network-diagnostics.csv"',
                "Cache-Control": "no-store",
            },
        )

    return router
