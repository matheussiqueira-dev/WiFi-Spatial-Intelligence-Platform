"""Host network telemetry is separate from synthetic spatial observations."""

from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import Field, model_validator

from app.contracts import StrictModel

Location = Annotated[str, Field(min_length=1, max_length=48, pattern=r"^[^\W_][\w .-]*$")]


class NetworkConfiguration(StrictModel):
    location: Location = "Computador"


class NetworkSample(StrictModel):
    schema_version: Literal["1.0.0"] = "1.0.0"
    data_class: Literal["HOST_NETWORK_TELEMETRY"] = "HOST_NETWORK_TELEMETRY"
    evidence_level: Literal["L2_LIVE_UNVALIDATED"] = "L2_LIVE_UNVALIDATED"
    source: Literal["windows-netsh"] = "windows-netsh"
    sample_id: UUID
    collector_id: UUID
    timestamp: datetime
    location: Location = "Computador"
    link_state: Literal["CONNECTED", "DISCONNECTED", "UNAVAILABLE"]
    signal_percent: Annotated[int, Field(strict=True, ge=0, le=100)] | None = None
    channel: Annotated[int, Field(strict=True, ge=1, le=233)] | None = None
    radio_type: (
        Literal["802.11a", "802.11b", "802.11g", "802.11n", "802.11ac", "802.11ax", "802.11be"]
        | None
    ) = None
    rx_mbps: Annotated[float, Field(ge=0, le=100000)] | None = None
    tx_mbps: Annotated[float, Field(ge=0, le=100000)] | None = None
    probe_sent: Annotated[int, Field(strict=True, ge=0, le=3)] = 0
    probe_rtt_ms: list[Annotated[float, Field(ge=0, le=10000)]] = Field(
        default_factory=list, max_length=3
    )
    probe_status: Literal["NOT_RUN", "COMPLETED", "UNAVAILABLE"] = "NOT_RUN"
    collector_error: (
        Literal[
            "no_adapter",
            "read_failed",
            "unsupported_output",
            "multiple_adapters",
            "permission_required",
        ]
        | None
    ) = None

    @model_validator(mode="after")
    def coherent(self):
        if self.timestamp.utcoffset() is None or self.timestamp.utcoffset().total_seconds() != 0:
            raise ValueError("UTC timestamp required")
        if len(self.probe_rtt_ms) > self.probe_sent:
            raise ValueError("replies cannot exceed sent probes")
        if (self.probe_status == "COMPLETED") != (self.probe_sent > 0):
            raise ValueError("probe status and count disagree")
        if self.link_state != "CONNECTED" and any(
            value is not None
            for value in (
                self.signal_percent,
                self.channel,
                self.radio_type,
                self.rx_mbps,
                self.tx_mbps,
            )
        ):
            raise ValueError("unconnected link cannot have current radio metrics")
        return self


class NetworkSummary(StrictModel):
    samples: int
    connected_samples: int
    disconnected_samples: int
    unavailable_samples: int
    connected_percent: float | None
    signal_mean_percent: float | None
    signal_min_percent: int | None
    gateway_mean_ms: float | None
    gateway_p95_ms: float | None
    gateway_loss_percent: float | None
    disconnect_events: int
    missing_seconds: float
    last_seen: datetime | None
    collector_stale: bool


class NetworkComparison(StrictModel):
    location: str
    summary: NetworkSummary


class NetworkReport(StrictModel):
    data_class: Literal["HOST_NETWORK_TELEMETRY"] = "HOST_NETWORK_TELEMETRY"
    evidence_level: Literal["L2_LIVE_UNVALIDATED"] = "L2_LIVE_UNVALIDATED"
    start: datetime
    end: datetime
    summary: NetworkSummary
    latest: NetworkSample | None
    items: list[NetworkSample]
    total: int
    limit: int
    offset: int
    locations: list[str]
    comparisons: list[NetworkComparison]
    configured_location: str
