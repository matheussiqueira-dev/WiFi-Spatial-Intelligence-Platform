"""Model lab runs and experiment job lifecycle."""

import json

from sqlalchemy import func, select

from app.adapters.sqlite.database import Database
from app.adapters.sqlite.models import ExperimentJobRow, ModelRunRow, audit_row

TERMINAL_JOB_STATES = {"completed", "cancelled", "failed", "interrupted"}


class LabRepository:
    def __init__(self, database: Database):
        self.session = database.session

    def save_model_run(self, result):
        with self.session.begin() as session:
            session.add(
                ModelRunRow(
                    id=result["id"],
                    created_at=result["created_at"],
                    payload=json.dumps(result, allow_nan=False),
                )
            )
            session.add(audit_row("model_lab.run.saved"))

    def model_runs(self, limit=20, offset=0):
        with self.session() as session:
            rows = session.scalars(
                select(ModelRunRow)
                .order_by(ModelRunRow.created_at.desc(), ModelRunRow.id.desc())
                .limit(limit)
                .offset(offset)
            )
            return {
                "items": [{"id": r.id, "created_at": r.created_at} for r in rows],
                "total": session.scalar(select(func.count()).select_from(ModelRunRow)),
                "limit": limit,
                "offset": offset,
            }

    def model_run(self, identifier):
        with self.session() as session:
            row = session.get(ModelRunRow, identifier)
            return json.loads(row.payload) if row else None

    def job_count(self):
        with self.session() as session:
            return session.scalar(select(func.count()).select_from(ExperimentJobRow))

    def save_job(self, identifier, payload):
        with self.session.begin() as session:
            session.merge(ExperimentJobRow(id=identifier, payload=json.dumps(payload)))

    def job(self, identifier):
        with self.session() as session:
            row = session.get(ExperimentJobRow, identifier)
            return json.loads(row.payload) if row else None

    def interrupt_jobs(self):
        with self.session.begin() as session:
            for row in session.scalars(select(ExperimentJobRow)):
                data = json.loads(row.payload)
                if data["state"] not in TERMINAL_JOB_STATES:
                    data.update(state="interrupted", error="process_restarted")
                    row.payload = json.dumps(data)
