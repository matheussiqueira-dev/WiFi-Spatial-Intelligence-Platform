"""Composition root: builds every adapter and service once per application instance."""

import asyncio
from dataclasses import dataclass, field
from pathlib import Path

from app.adapters.history import SqliteHistoryRepository
from app.application.experiment_jobs import ExperimentJobs
from app.application.model_lab import ModelLab
from app.application.read_history import ReadHistory
from app.config import Settings
from app.pipeline import Pipeline
from app.recurring_backup import RecurringBackup
from app.security import LocalLimiter
from app.storage import Store

WORKSPACE = Path(__file__).parents[3]


@dataclass
class Container:
    settings: Settings
    database_path: Path
    store: Store
    pipeline: Pipeline
    model_lock: asyncio.Lock
    model_lab: ModelLab
    experiment_jobs: ExperimentJobs
    limiter: LocalLimiter
    history: ReadHistory
    backup_worker: RecurringBackup | None
    rules_lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    # Pending WebSocket handshakes hold a slot of the subscriber cap.
    stream_handshakes: set[object] = field(default_factory=set)


def build_container(settings: Settings) -> Container:
    if not settings.database_url.startswith("sqlite:///"):
        raise ValueError("only local SQLite is supported in phase 1")
    database_path = Path(settings.database_url.removeprefix("sqlite:///"))
    database_path.parent.mkdir(parents=True, exist_ok=True)
    store = Store(settings.database_url, settings.retention_events)
    model_lock = asyncio.Lock()
    model_lab = ModelLab(store, database_path.parent / "model-lab")
    return Container(
        settings=settings,
        database_path=database_path,
        store=store,
        pipeline=Pipeline(store, settings),
        model_lock=model_lock,
        model_lab=model_lab,
        experiment_jobs=ExperimentJobs(model_lab, model_lock),
        limiter=LocalLimiter(
            {
                "auth": settings.rate_auth,
                "write": settings.rate_write,
                "read": settings.rate_read,
                "stream": settings.rate_stream,
            }
        ),
        history=ReadHistory(SqliteHistoryRepository(store)),
        backup_worker=RecurringBackup(
            database_path,
            Path(settings.backup_destination),
            WORKSPACE,
            settings.backup_interval_seconds,
        )
        if settings.backup_enabled
        else None,
    )
