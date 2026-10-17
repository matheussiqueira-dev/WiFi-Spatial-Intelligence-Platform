import asyncio
import csv
import io
from datetime import UTC, datetime, timedelta
from urllib.parse import urlsplit

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from app.adapters.network_store import NetworkStore
from app.api.deps import GatedRouter, admin, operator, require_capability, viewer
from app.application.alert_webhook import AlertWebhook
from app.application.channel_plan import plan
from app.application.network_diagnostics import summarize
from app.application.network_health import health
from app.config import Settings
from app.network_contracts import (
    ChannelPlan,
    ChannelSurvey,
    NetworkComparison,
    NetworkConfiguration,
    NetworkHealth,
    NetworkReport,
    NetworkSample,
)


def network_router(
    store: NetworkStore,
    webhook: AlertWebhook | None,
    settings: Settings,
) -> APIRouter:
    router = GatedRouter(
        "network.link_diagnostics", prefix="/api/v1/network", tags=["Network diagnostics"]
    )
    webhook_gate = [require_capability("network.alert_webhook")]

    @router.get("/webhook", dependencies=[*viewer, *webhook_gate])
    def webhook_status():
        destination = None
        if settings.alert_webhook_url:
            # Path and query can carry the receiver's own secret (e.g. a webhook ID).
            url = urlsplit(settings.alert_webhook_url)
            destination = f"{url.scheme}://{url.netloc}"
        return {
            "configured": webhook is not None,
            "destination": destination,
            "interval_seconds": settings.alert_webhook_interval_seconds,
            "active_alerts": len(webhook.active) if webhook else 0,
            "cycles": webhook.cycles if webhook else 0,
            "last_error": webhook.last_error if webhook else None,
            "deliveries": store.deliveries(),
            "mode": "ADVISORY",
        }

    @router.post("/webhook/test", dependencies=[*admin, *webhook_gate])
    async def webhook_test():
        if webhook is None:
            raise HTTPException(409, "alert webhook is not configured")
        delivered = await asyncio.to_thread(webhook.test)
        return {"delivered": delivered, "delivery": store.deliveries(1)[0]}

    @router.post("/samples", dependencies=operator)
    def ingest(sample: NetworkSample):
        age = (datetime.now(UTC) - sample.timestamp).total_seconds()
        if not -5 <= age <= 120:
            raise HTTPException(422, "sample must be recent UTC host telemetry")
        try:
            return {"inserted": store.save(sample)}
        except ValueError as error:
            raise HTTPException(409, str(error)) from error

    channel = [require_capability("network.channel_plan")]

    @router.post("/channel-surveys", dependencies=[*operator, *channel])
    def ingest_survey(survey: ChannelSurvey):
        age = (datetime.now(UTC) - survey.timestamp).total_seconds()
        if not -5 <= age <= 120:
            raise HTTPException(422, "survey must be recent UTC host telemetry")
        try:
            return {"inserted": store.save_survey(survey)}
        except ValueError as error:
            raise HTTPException(409, str(error)) from error

    @router.get("/channel-plan", response_model=ChannelPlan, dependencies=[*viewer, *channel])
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

    @router.get(
        "/health",
        response_model=NetworkHealth,
        dependencies=[*viewer, require_capability("network.degradation_alerts")],
    )
    def get_health(
        hours: int = Query(24, ge=2, le=24),
        bucket_minutes: int = Query(60, ge=15, le=240),
        location: str | None = Query(None, max_length=48),
    ):
        if bucket_minutes not in {15, 30, 60, 120, 240}:
            raise HTTPException(422, "bucket_minutes must be 15, 30, 60, 120 or 240")
        now = datetime.now(UTC)
        start = now - timedelta(hours=hours)
        try:
            rows = store.read(start, now)
        except ValueError as error:
            raise HTTPException(422, str(error)) from error
        rows = [row for row in rows if location is None or row.location == location]
        return health(rows, start, now, timedelta(minutes=bucket_minutes), location)

    @router.delete("/history", dependencies=admin)
    def erase_history(
        confirm: str = Query(..., description="Must be ERASE to confirm the deletion"),
        location: str | None = Query(None, max_length=48),
    ):
        if confirm != "ERASE":
            raise HTTPException(422, "confirm=ERASE is required")
        erased = store.erase(location)
        return {"erased": erased, "location": location, "audit_preserved": True}

    @router.get("/config", response_model=NetworkConfiguration, dependencies=viewer)
    def configuration():
        return NetworkConfiguration(location=store.configuration())

    @router.post("/config", response_model=NetworkConfiguration, dependencies=operator)
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

    @router.get("/report", response_model=NetworkReport, dependencies=viewer)
    def get_report(
        hours: float = Query(24, ge=1 / 60, le=24),
        location: str | None = Query(None, max_length=48),
        limit: int = Query(100, ge=1, le=200),
        offset: int = Query(0, ge=0, le=10000),
    ):
        return report(hours, location, limit, offset)

    @router.get("/export.csv", dependencies=viewer)
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
