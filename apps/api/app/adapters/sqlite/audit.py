"""Operation audit trail and bounded, aggregated security denials (no tokens, IPs or payloads)."""

from datetime import UTC, datetime
from typing import cast
from uuid import uuid4

from sqlalchemy import Table, select
from sqlalchemy.dialects.sqlite import insert

from app.adapters.sqlite.database import Database
from app.adapters.sqlite.models import AuditRow, SecurityDenialRow, audit_row

SECURITY_ACTIONS = {
    "auth.denied",
    "origin.denied",
    "rate.denied",
    "operation.denied",
    "ws.origin_denied",
    "ws.auth_denied",
    "ws.timeout",
    "ws.limit",
    "ws.rate_denied",
}


class AuditRepository:
    def __init__(self, database: Database):
        self.engine = database.engine
        self.session = database.session

    def audit(self, action: str):
        with self.session.begin() as session:
            session.add(audit_row(action))

    def security_denial(self, action: str):
        if action not in SECURITY_ACTIONS:
            raise ValueError("unsupported security audit action")
        now = datetime.now(UTC).isoformat()
        table = cast(Table, SecurityDenialRow.__table__)
        statement = insert(table).values(
            action=action, count=1, first_seen=now, last_seen=now, correlation_id=str(uuid4())
        )
        statement = statement.on_conflict_do_update(
            index_elements=[table.c.action],
            set_={
                "count": table.c.count + 1,
                "last_seen": now,
                "correlation_id": statement.excluded.correlation_id,
            },
        )
        with self.engine.begin() as connection:
            connection.execute(statement)

    def security_audits(self):
        with self.session() as session:
            return [
                {
                    "action": r.action,
                    "count": r.count,
                    "first_seen": r.first_seen,
                    "last_seen": r.last_seen,
                    "correlation_id": r.correlation_id,
                    "result": "denied",
                }
                for r in session.scalars(
                    select(SecurityDenialRow).order_by(SecurityDenialRow.action)
                )
            ]

    def audits(self):
        with self.session() as session:
            return [
                {"timestamp": r.timestamp, "action": r.action}
                | ({"subject_id": r.subject_id} if r.subject_id else {})
                for r in session.scalars(select(AuditRow).order_by(AuditRow.id.desc()).limit(100))
            ]
