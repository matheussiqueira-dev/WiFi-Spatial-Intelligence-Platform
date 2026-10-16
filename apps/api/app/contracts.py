"""Single source of truth: export JSON Schema for the frontend contract."""

from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic.config import JsonDict

Scenario = Literal[
    "empty",
    "stationary",
    "walking",
    "entering",
    "leaving",
    "interference",
    "packet_loss",
    "disconnect",
]
RoomX = Annotated[float, Field(ge=0, le=8)]
RoomY = Annotated[float, Field(ge=0, le=6)]
# Published form of the runtime presence/count rule; count == len(positions) stays runtime-only.
PRESENCE_MATCHES_COUNT: JsonDict = {
    "if": {"properties": {"presence_detected": {"const": True}}, "required": ["presence_detected"]},
    "then": {"properties": {"occupancy_estimate": {"minimum": 1}}},
    "else": {"properties": {"occupancy_estimate": {"maximum": 0}}},
}


class StrictModel(BaseModel):
    # Emitted payloads always carry defaulted fields, so the published schema requires them.
    model_config = ConfigDict(
        extra="forbid", allow_inf_nan=False, json_schema_serialization_defaults_required=True
    )


class Measurements(StrictModel):
    model_config = ConfigDict(json_schema_extra=PRESENCE_MATCHES_COUNT)

    presence_detected: bool
    occupancy_estimate: int = Field(ge=0, le=20)
    ground_truth_positions: list[tuple[RoomX, RoomY]] = Field(max_length=20)


class Quality(StrictModel):
    """L0 ground truth has no measured signal quality or confidence."""

    signal_quality: None = None
    confidence: None = None


class ModelReference(StrictModel):
    """L0 ground truth is never attributed to a model inference."""

    id: None = None
    version: None = None


class Provenance(StrictModel):
    generator: Literal["local-simulator"] = "local-simulator"
    seed: int
    tick: int = Field(ge=0)
    scenario: str
    dataset_id: str | None = None


class Privacy(StrictModel):
    classification: Literal["synthetic"] = "synthetic"
    consent_record_id: None = None


class SensingEvent(StrictModel):
    schema_version: Literal["1.0.0"] = "1.0.0"
    event_id: UUID
    timestamp: datetime
    source_id: Literal["simulator-01"] = "simulator-01"
    room_id: Literal["living-room"] = "living-room"
    event_type: Literal["simulation.observation"] = "simulation.observation"
    source_type: Literal["SIMULATED"] = "SIMULATED"
    evidence_level: Literal["L0_SYNTHETIC"] = "L0_SYNTHETIC"
    validation_status: Literal["IMPLEMENTED_SYNTHETIC"] = "IMPLEMENTED_SYNTHETIC"
    measurements: Measurements
    quality: Quality = Field(default_factory=Quality)
    model: ModelReference = Field(default_factory=ModelReference)
    provenance: Provenance
    privacy: Privacy = Field(default_factory=Privacy)
    processing_latency_ms: float | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def coherent_observation(self):
        if (offset := self.timestamp.utcoffset()) is None or offset.total_seconds() != 0:
            raise ValueError("timestamp must be timezone-aware UTC")
        if self.measurements.presence_detected != (self.measurements.occupancy_estimate > 0):
            raise ValueError("inconsistent synthetic presence")
        if len(self.measurements.ground_truth_positions) != self.measurements.occupancy_estimate:
            raise ValueError("synthetic positions must match ground truth count")
        return self


class SimulationConfig(StrictModel):
    scenario: Scenario = "walking"
    seed: int = Field(default=42, ge=0, le=2**32 - 1)
    occupants: int = Field(default=2, ge=0, le=20)
    speed: float = Field(default=1, ge=0.25, le=4)


class RuViewMeasurements(StrictModel):
    model_config = ConfigDict(json_schema_extra=PRESENCE_MATCHES_COUNT)

    presence_detected: bool
    occupancy_estimate: int | None = Field(default=None, ge=0, le=20)
    # Upstream field peaks/pose estimates are not simulator ground truth.
    ground_truth_positions: list = Field(default_factory=list, max_length=0)


class RuViewProvenance(StrictModel):
    generator: Literal["ruview-simulated"] = "ruview-simulated"
    scenario: Literal["ruview-simulated"] = "ruview-simulated"
    seed: None = None  # Upstream exposes no reproducible seed in this API.
    tick: int = Field(ge=0)
    dataset_id: None = None
    upstream_source: Literal["simulated"] = "simulated"
    upstream_type: Literal["sensing_update"] = "sensing_update"
    adapter_version: Literal["1.0.0"] = "1.0.0"


class RuViewEvent(StrictModel):
    """Additive contract; never relabel upstream estimates as ground truth."""

    schema_version: Literal["1.1.0"] = "1.1.0"
    event_id: UUID
    timestamp: datetime
    source_id: Literal["ruview-01"] = "ruview-01"
    room_id: Literal["living-room"] = "living-room"
    event_type: Literal["simulation.ruview.observation"] = "simulation.ruview.observation"
    source_type: Literal["SIMULATED"] = "SIMULATED"
    evidence_level: Literal["L0_SYNTHETIC"] = "L0_SYNTHETIC"
    validation_status: Literal["IMPLEMENTED_SYNTHETIC"] = "IMPLEMENTED_SYNTHETIC"
    measurements: RuViewMeasurements
    quality: Quality = Field(default_factory=Quality)
    model: ModelReference = Field(default_factory=ModelReference)
    provenance: RuViewProvenance
    privacy: Privacy = Field(default_factory=Privacy)
    processing_latency_ms: float | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def synthetic_only(self):
        if (offset := self.timestamp.utcoffset()) is None or offset.total_seconds() != 0:
            raise ValueError("timestamp must be timezone-aware UTC")
        count = self.measurements.occupancy_estimate
        if count is not None and self.measurements.presence_detected != (count > 0):
            raise ValueError("inconsistent upstream presence/count")
        return self


class NativeProvenance(Provenance):
    # Stricter than legacy 1.0.0, whose stored payloads keep their historical tolerance.
    generator: Literal["synthetic-native"] = "synthetic-native"  # type: ignore[assignment]
    seed: int = Field(ge=0, le=2**32 - 1)
    scenario: Scenario
    dataset_id: None = None


class NativeEvent(SensingEvent):
    # Contract 2.0.0 deliberately replaces the 1.x literals (additive versioning, ADR);
    # pydantic validates the narrowed field, mypy only sees an incompatible override.
    schema_version: Literal["2.0.0"] = "2.0.0"  # type: ignore[assignment]
    source_id: Literal["native-01"] = "native-01"  # type: ignore[assignment]
    event_type: Literal["synthetic.spatial.observation"] = "synthetic.spatial.observation"  # type: ignore[assignment]
    provider: Literal["synthetic-native"] = "synthetic-native"
    provenance: NativeProvenance


# Stored payloads always carry schema_version, so the tag never relabels a version.
Event = Annotated[SensingEvent | RuViewEvent | NativeEvent, Field(discriminator="schema_version")]


class SourceSelection(StrictModel):
    source: Literal["synthetic-native", "SIMULATED", "RUVIEW_STREAM"]
