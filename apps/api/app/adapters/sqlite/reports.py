"""Saved analytics snapshots, bounded to the newest 100."""

import json
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import delete, func, select

from app.adapters.sqlite.database import Database
from app.adapters.sqlite.models import AnalyticsReportRow, audit_row

MAX_REPORTS = 100


class ReportRepository:
    def __init__(self, database: Database):
        self.session = database.session

    def save_report(self, report):
        identifier = str(uuid4())
        with self.session.begin() as session:
            session.add(
                AnalyticsReportRow(
                    id=identifier,
                    created_at=datetime.now(UTC).isoformat(),
                    payload=json.dumps(report, allow_nan=False),
                )
            )
            session.flush()
            obsolete = (
                select(AnalyticsReportRow.id)
                .order_by(AnalyticsReportRow.created_at.desc(), AnalyticsReportRow.id.desc())
                .offset(MAX_REPORTS)
            )
            session.execute(delete(AnalyticsReportRow).where(AnalyticsReportRow.id.in_(obsolete)))
            session.add(audit_row("analytics.report.saved"))
        return identifier

    def reports(self, limit, offset):
        with self.session() as session:
            rows = session.scalars(
                select(AnalyticsReportRow)
                .order_by(AnalyticsReportRow.created_at.desc(), AnalyticsReportRow.id.desc())
                .limit(limit)
                .offset(offset)
            ).all()
            return {
                "items": [{"id": row.id, "created_at": row.created_at} for row in rows],
                "total": session.scalar(select(func.count()).select_from(AnalyticsReportRow)),
                "limit": limit,
                "offset": offset,
            }

    def report(self, identifier):
        with self.session() as session:
            row = session.get(AnalyticsReportRow, identifier)
            return None if row is None else json.loads(row.payload)
