"""Loopback-only RuView sensing stream adapter. No hardware or REST polling fallback."""

import asyncio
import json
import time
from collections import deque
from datetime import UTC, datetime
from urllib.error import HTTPError
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener
from uuid import NAMESPACE_URL, uuid5

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, ValidationError
from websockets.asyncio.client import connect
from websockets.exceptions import WebSocketException

from app.config import Settings
from app.contracts import RuViewEvent, RuViewMeasurements, RuViewProvenance, SimulationConfig


class Classification(BaseModel):
    presence: StrictBool


class UpstreamUpdate(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)
    type: str
    source: str
    timestamp: float = Field(gt=0)
    tick: StrictInt = Field(ge=0)
    classification: Classification
    estimated_persons: StrictInt | None = Field(default=None, ge=0, le=20)


def normalize_update(payload: object, stale_seconds: float = 5) -> RuViewEvent:
    update = UpstreamUpdate.model_validate(payload)
    if update.type != "sensing_update" or update.source != "simulated":
        raise ValueError("only explicit simulated sensing_update frames are supported")
    age = time.time() - update.timestamp
    if not -2 <= age <= stale_seconds:
        raise ValueError("stale or future upstream timestamp")
    count = update.estimated_persons
    if not update.classification.presence and count is None:
        count = 0
    return RuViewEvent(
        event_id=uuid5(NAMESPACE_URL, f"ruview-simulated:{update.timestamp}:{update.tick}"),
        timestamp=datetime.fromtimestamp(update.timestamp, UTC),
        measurements=RuViewMeasurements(
            presence_detected=update.classification.presence, occupancy_estimate=count
        ),
        provenance=RuViewProvenance(tick=update.tick),
    )


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Never forward the service credential to a redirected origin.
        return None


class LocalConnect(connect):
    def process_redirect(self, exc):
        # The configured local origin is the only allowed destination.
        return exc


class RuViewProvider:
    streaming = True

    def __init__(self, settings: Settings):
        self.settings = settings
        self.config = SimulationConfig()  # Kept for the existing status contract only.
        self.tick = 0
        self.connected = False
        self.active = False
        self.socket = None
        self.retry_at = 0.0
        self.failures = 0
        self.received = 0
        self.rejected = 0
        self.ignored = 0
        self.duplicates = 0
        self.reconnections = 0
        self.last_received = None
        self.last_timestamp = None
        self.last_tick = None
        self.service_status = "stopped"
        self.last_error = None
        self.seen = deque(maxlen=256)

    async def connect(self):
        self.active = True
        self.retry_at = 0
        self.service_status = "connecting"

    async def disconnect(self):
        self.active = False
        self.service_status = "stopped"
        self.last_error = None
        await self._close_socket()
        self.service_status = "stopped"

    async def _close_socket(self):
        self.connected = False
        socket, self.socket = self.socket, None
        if socket is not None:
            await socket.close()

    def _probe(self):
        headers = {"Authorization": f"Bearer {self.settings.ruview_token}"}
        req = Request(f"{self.settings.ruview_http_url}/api/v1/status", headers=headers)
        # Disable environment proxies for this local-only integration.
        with build_opener(ProxyHandler({}), NoRedirect()).open(req, timeout=2) as response:
            raw = response.read(65537)
        if len(raw) > 65536:
            raise ValueError("oversized upstream status")
        data = json.loads(raw)
        if (
            not isinstance(data, dict)
            or data.get("source") != "simulated"
            or data.get("source_state") != "synthetic"
            or data.get("status") != "ready"
        ):
            raise ValueError("RuView must be ready in explicit simulated/synthetic mode")

    async def _fail(self, message: str):
        if not self.active:
            return  # An intentional stop is not a connectivity failure.
        self.last_error = message
        self.service_status = "reconnecting"
        self.failures += 1
        self.retry_at = time.monotonic() + min(0.5 * 2 ** min(self.failures - 1, 5), 10)
        await self._close_socket()

    async def next_event(self):
        if not self.active or time.monotonic() < self.retry_at:
            return None
        try:
            if self.socket is None:
                await asyncio.to_thread(self._probe)
                if not self.active:
                    return None
                socket = await LocalConnect(
                    self.settings.ruview_ws_url,
                    additional_headers={"Authorization": f"Bearer {self.settings.ruview_token}"},
                    open_timeout=2,
                    close_timeout=1,
                    ping_interval=10,
                    ping_timeout=5,
                    max_size=262144,
                    max_queue=4,
                    proxy=None,
                )
                if not self.active:
                    await socket.close()
                    return None
                self.socket = socket
                self.last_timestamp = None
                self.last_tick = None
                self.last_received = time.monotonic()
                self.service_status = "waiting"
                self.reconnections += 1
            try:
                raw = await asyncio.wait_for(self.socket.recv(), timeout=0.5)
            except TimeoutError:
                if time.monotonic() - self.last_received > self.settings.ruview_stale_seconds:
                    await self._fail("RuView stream stale; reconnecting.")
                return None
            payload = json.loads(raw)
            if not isinstance(payload, dict):
                raise ValueError("upstream frame must be a JSON object")
            if payload.get("type") != "sensing_update":
                self.ignored += 1
                if time.monotonic() - self.last_received > self.settings.ruview_stale_seconds:
                    await self._fail("No fresh sensing_update; reconnecting.")
                return None
            event = normalize_update(payload, self.settings.ruview_stale_seconds)
            if event.event_id in self.seen:
                self.duplicates += 1
                return None
            if self.last_tick is not None and (
                event.provenance.tick <= self.last_tick or event.timestamp <= self.last_timestamp
            ):
                raise ValueError("out-of-order upstream frame")
            self.seen.append(event.event_id)
            self.last_tick = event.provenance.tick
            self.last_timestamp = event.timestamp
            self.tick = event.provenance.tick
            self.last_received = time.monotonic()
            self.received += 1
            self.connected = True
            self.service_status = "receiving"
            self.failures = 0
            self.last_error = None
            return event
        except (ValueError, ValidationError, OverflowError):
            self.rejected += 1
            await self._fail("RuView frame/status rejected: incompatible or non-synthetic data.")
        except HTTPError as error:
            await self._fail(
                f"RuView REST returned HTTP {error.code}; check service authentication."
            )
        except (OSError, WebSocketException, TimeoutError):
            await self._fail("RuView unavailable; check service, ports and credentials.")
        return None

    def diagnostics(self):
        age = (
            None
            if self.last_timestamp is None
            else max(0, (datetime.now(UTC) - self.last_timestamp).total_seconds())
        )
        return {
            "service_status": self.service_status,
            "connected": self.connected,
            "received_frames": self.received,
            "rejected_frames": self.rejected,
            "ignored_frames": self.ignored,
            "duplicate_frames": self.duplicates,
            "reconnections": max(0, self.reconnections - 1),
            "last_event_age_seconds": age,
            "stale": age is None or age > self.settings.ruview_stale_seconds,
            "last_error": self.last_error,
            "data_quality": "synthetic estimates; no measured confidence or ground truth positions",
            "upstream_source": "simulated",
            "evidence_level": "L0_SYNTHETIC",
        }
