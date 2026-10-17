"""Deliver network degradation alerts to the configured local webhook on state change.

Each location is evaluated against its own baseline, so moving the computer between
rooms never looks like a degradation. Only transitions are sent: ``alert.raised`` when
an alert appears and ``alert.cleared`` when it disappears. A failed delivery leaves the
state unchanged, so the next cycle retries it. Active state lives in memory: after a
restart, alerts that are still active are raised again (at-least-once delivery).
"""

import asyncio
import json
import logging
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from app.adapters.webhook import DeliveryResult
from app.application.network_health import degradation
from app.network_contracts import DegradationAlert, NetworkSample

logger = logging.getLogger("spatial.webhook")
WINDOW = timedelta(hours=24)
GLOBAL = "*"

Reader = Callable[[datetime, datetime], list[NetworkSample]]
Sender = Callable[[bytes], DeliveryResult]
Recorder = Callable[[dict], None]


class AlertWebhook:
    def __init__(self, read: Reader, send: Sender, record: Recorder, interval: float):
        self.read = read
        self.send = send
        self.record = record
        self.interval = interval
        self.active: dict[tuple[str, str], DegradationAlert] = {}
        self.stop = asyncio.Event()
        self.cycles = 0
        self.last_error: str | None = None

    def current_alerts(self, now: datetime) -> dict[tuple[str, str], DegradationAlert]:
        rows = self.read(now - WINDOW, now)
        found: dict[tuple[str, str], DegradationAlert] = {}
        for location in sorted({row.location for row in rows}):
            alerts = degradation([row for row in rows if row.location == location], now)[0]
            for alert in alerts:
                # Staleness of one room is expected after moving; only global silence counts.
                if alert.code != "COLLECTOR_STALE":
                    found[(location, alert.code)] = alert
        stale = degradation(rows, now)[0]
        for alert in stale:
            if alert.code == "COLLECTOR_STALE" and rows:
                found[(GLOBAL, alert.code)] = alert
        return found

    def deliver(
        self, event: str, location: str | None, alert: DegradationAlert | None, now: datetime
    ) -> bool:
        delivery_id = str(uuid4())
        body = {
            "schema_version": "1.0.0",
            "event": event,
            "delivery_id": delivery_id,
            "occurred_at": now.isoformat(),
            "data_class": "HOST_NETWORK_TELEMETRY",
            "evidence_level": "L2_LIVE_UNVALIDATED",
            "mode": "ADVISORY",
            "location": None if location == GLOBAL else location,
            "alert": alert.model_dump() if alert else None,
        }
        result = self.send(json.dumps(body, separators=(",", ":")).encode())
        self.record(
            {
                "id": delivery_id,
                "created_at": now.isoformat(),
                "event": event,
                "alert_code": alert.code if alert else None,
                "location": body["location"],
                "delivered": result.delivered,
                "http_status": result.http_status,
                "error": result.error,
            }
        )
        return result.delivered

    def cycle(self, now: datetime | None = None) -> None:
        now = now or datetime.now(UTC)
        current = self.current_alerts(now)
        for key, alert in current.items():
            if key not in self.active and self.deliver("alert.raised", key[0], alert, now):
                self.active[key] = alert
        for key in list(self.active):
            if key not in current and self.deliver("alert.cleared", key[0], self.active[key], now):
                del self.active[key]
        self.cycles += 1

    def test(self) -> bool:
        return self.deliver("webhook.test", None, None, datetime.now(UTC))

    async def run(self) -> None:
        while not self.stop.is_set():
            try:
                await asyncio.to_thread(self.cycle)
                self.last_error = None
            except Exception as error:
                # Keep the loop alive; never log payloads, URLs or the secret.
                self.last_error = type(error).__name__
                logger.error("alert webhook cycle failed type=%s", self.last_error)
            try:
                await asyncio.wait_for(self.stop.wait(), timeout=self.interval)
            except TimeoutError:
                pass
