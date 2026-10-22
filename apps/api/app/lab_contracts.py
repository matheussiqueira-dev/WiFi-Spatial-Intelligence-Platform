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


License = Literal[
    "MIT",
    "Apache-2.0",
    "BSD-2-Clause",
    "BSD-3-Clause",
    "CC-BY-4.0",
    "CC-BY-NC-4.0",
    "GPL-3.0-only",
    "PROPRIETARY",
    "UNKNOWN",
]
# Working classification for later legal review, not legal advice.
COMMERCIAL_USE: dict[str, str] = {
    "MIT": "ALLOWED",
    "Apache-2.0": "ALLOWED",
    "BSD-2-Clause": "ALLOWED",
    "BSD-3-Clause": "ALLOWED",
    "CC-BY-4.0": "ALLOWED",
    "CC-BY-NC-4.0": "NOT_ALLOWED",
    "GPL-3.0-only": "REVIEW_REQUIRED",
    "PROPRIETARY": "REVIEW_REQUIRED",
    "UNKNOWN": "REVIEW_REQUIRED",
}


class ModelCardRequest(StrictModel):
    """Metadata of an external model. The file is never uploaded, fetched or executed."""

    name: str = Field(min_length=1, max_length=80, pattern=r"^[\w .+-]+$")
    version: str = Field(min_length=1, max_length=40, pattern=r"^[\w.+-]+$")
    license: License
    source_url: str = Field(max_length=200, pattern=r"^https://[^\s]+$")
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    intended_use: str = Field(min_length=1, max_length=200)


class ModelCard(ModelCardRequest):
    id: UUID
    created_at: datetime
    origin: Literal["third_party"] = "third_party"
    commercial_use: Literal["ALLOWED", "REVIEW_REQUIRED", "NOT_ALLOWED"]
    status: Literal["NOT_LOADED"] = "NOT_LOADED"
    evidence_level: Literal["UNVERIFIED"] = "UNVERIFIED"


class ProjectModel(StrictModel):
    origin: Literal["project"] = "project"
    id: str
    version: str
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    size_bytes: int = Field(ge=0)
    integrity: Literal["VERIFIED", "MISMATCH", "UNREADABLE"]
    license: Literal["MIT"] = "MIT"
    evidence_level: Literal["L0_SYNTHETIC"] = "L0_SYNTHETIC"


class ModelRegistry(StrictModel):
    project: list[ProjectModel]
    third_party: list[ModelCard]
    maximum_third_party: int


class RfFingerprintRequest(StrictModel):
    seed: int = Field(default=42, ge=0, le=100000)


class RfFingerprintEvaluation(StrictModel):
    method: Literal["rf-fingerprint-zscore-v1"]
    evidence_level: Literal["L0_SYNTHETIC"]
    transport: Literal["SWF1"]
    seed: int
    fingerprint_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    reference_frames: int = Field(gt=0)
    window_frames: int = Field(gt=0)
    min_frames: int = Field(gt=0)
    subcarriers: int = Field(gt=0)
    threshold: float = Field(gt=0)
    reference_scores_max: float = Field(ge=0)
    normal_windows: int
    false_positives: int
    false_positive_rate: float = Field(ge=0, le=1)
    changed_windows: int
    detections: int
    detection_rate: float = Field(ge=0, le=1)
    subtle_windows: int
    subtle_detection_rate: float = Field(ge=0, le=1)
    other_environment_windows: int
    other_environment_detection_rate: float = Field(ge=0, le=1)
    sparse_windows: int
    abstained: int
    frames_received: int
    limitations: list[str]
