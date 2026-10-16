"""Synthetic experiment API boundary, separate from immutable scene truth."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import Field

from app.contracts import StrictModel

MotionClass = Literal["stationary", "walking", "unknown"]


class ModelMetadata(StrictModel):
    id: Literal["geometry-motion-v1"]
    version: Literal["geometry-speed-v1"]
    threshold_m_per_s: float = Field(gt=0)
    abstention_margin: float = Field(ge=0, le=1)
    features: list[str]
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")


class WindowPrediction(StrictModel):
    session_id: str
    window: int = Field(ge=0)
    prediction: MotionClass
    reference: MotionClass
    quality: Literal["gap", "complete"]
    mean_speed: float | None = Field(ge=0)
    start_seconds: float = Field(ge=0)
    end_seconds: float = Field(ge=0)


class Evaluation(StrictModel):
    classes: list[MotionClass]
    confusion_matrix: list[list[int]]
    samples: int = Field(ge=0, le=100)
    support: dict[str, int]
    rejected: int = Field(ge=0)
    rejection_rate: float | None = Field(ge=0, le=1)
    accuracy_accepted: float | None = Field(ge=0, le=1)
    false_positive_rate: float | None = Field(ge=0, le=1)
    predictions: list[WindowPrediction] = Field(max_length=100)


class ExperimentResult(StrictModel):
    id: UUID
    created_at: datetime
    seed: int
    duration_ms: float = Field(ge=0)
    model: ModelMetadata
    dataset_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    dataset_version: Literal["virtual-motion-v1"]
    evidence_level: Literal["L0_SYNTHETIC"]
    validation: Evaluation
    evaluation: Evaluation
    splits: dict[str, list[str]]
    unsupported: list[str]
    limitation: str
