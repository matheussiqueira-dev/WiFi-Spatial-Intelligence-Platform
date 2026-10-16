"""Persisted observations: idempotent ingestion, retention, history and analytics windows."""

import json
from datetime import UTC, timedelta

from sqlalchemy import delete, func, select

from app.adapters.sqlite.database import Database, epoch_microseconds
from app.adapters.sqlite.models import AnalyticsReportRow, EventRow, audit_row
from app.adapters.sqlite.rules import record_decisions
from app.contracts import Event

CURRENT_SEGMENT = object()
MAX_SELECTION = 10000


class EventRepository:
    def __init__(self, database: Database, retention: int):
        self.session = database.session
        self.retention = retention
        self.segment_id = None
        # Lexical timestamp ranges are only valid while every stored value is UTC isoformat.
        self.utc_timestamps = None

    def write(self, event: Event, segment_id=CURRENT_SEGMENT):
        # The pipeline passes the segment captured at enqueue time; it may have changed since.
        if segment_id is CURRENT_SEGMENT:
            segment_id = self.segment_id
        with self.session.begin() as session:
            if session.scalar(select(EventRow.id).where(EventRow.event_id == str(event.event_id))):
                return False  # Idempotent replay after a RuView reconnect/backend restart.
            timestamp = event.timestamp.isoformat()
            if not timestamp.endswith("+00:00"):
                self.utc_timestamps = False
            session.add(
                EventRow(
                    event_id=str(event.event_id),
                    timestamp=timestamp,
                    evidence_level=event.evidence_level,
                    payload=event.model_dump_json(),
                    segment_id=segment_id,
                )
            )
            session.flush()
            # count(*) uses a covering index; an OFFSET boundary walked `retention` entries.
            excess = session.scalar(select(func.count()).select_from(EventRow)) - self.retention
            if excess > 0:
                # FIFO for synthetic data only; future L1/L2 evidence needs its own
                # retention policy and is never purged as a side effect of L0 ingestion.
                oldest = (
                    select(EventRow.id)
                    .where(EventRow.evidence_level == "L0_SYNTHETIC")
                    .order_by(EventRow.id)
                    .limit(excess)
                )
                session.execute(delete(EventRow).where(EventRow.id.in_(oldest)))
            record_decisions(session, event)
        return True

    def observations(self, start, end, source_id=None, scenario=None, segment_id=None):
        """Bounded snapshot; validate UTC and order in the analytics domain layer."""
        query = self._window(start, end, source_id, scenario, segment_id)
        with self.session() as session:
            rows = session.scalars(query.limit(MAX_SELECTION + 1)).all()
            if len(rows) > MAX_SELECTION:
                raise ValueError("more than 10000 events; narrow the time range or source")
            return [
                {"event": json.loads(row.payload), "segment_id": row.segment_id} for row in rows
            ]

    def observation_page(
        self, start, end, offset, limit, source_id=None, scenario=None, segment_id=None
    ):
        """One replay page ordered in SQL; only the page payloads are decoded."""
        query = self._window(start, end, source_id, scenario, segment_id)
        with self.session() as session:
            total = session.scalar(select(func.count()).select_from(query.subquery()))
            if total > MAX_SELECTION:
                raise ValueError("more than 10000 events; narrow the time range or source")
            rows = session.scalars(
                query.order_by(func.spatial_epoch_us(EventRow.timestamp), EventRow.event_id)
                .offset(offset)
                .limit(limit)
            ).all()
            items = [
                {"event": json.loads(row.payload), "segment_id": row.segment_id} for row in rows
            ]
            return items, total

    def _window(self, start, end, source_id=None, scenario=None, segment_id=None):
        query = select(EventRow).where(
            func.spatial_epoch_us(EventRow.timestamp) >= epoch_microseconds(start.isoformat()),
            func.spatial_epoch_us(EventRow.timestamp) < epoch_microseconds(end.isoformat()),
        )
        if self.lexical_timestamps():
            # Indexed coarse range; the UDF above stays the exact, submillisecond filter.
            query = query.where(
                EventRow.timestamp >= (start - timedelta(seconds=1)).astimezone(UTC).isoformat(),
                EventRow.timestamp < (end + timedelta(seconds=1)).astimezone(UTC).isoformat(),
            )
        if source_id:
            query = query.where(func.json_extract(EventRow.payload, "$.source_id") == source_id)
        if scenario:
            query = query.where(
                func.json_extract(EventRow.payload, "$.provenance.scenario") == scenario
            )
        if segment_id:
            query = query.where(EventRow.segment_id == segment_id)
        return query

    def lexical_timestamps(self) -> bool:
        if self.utc_timestamps is None:
            with self.session() as session:
                other = session.scalar(
                    select(EventRow.id).where(EventRow.timestamp.not_like("%+00:00")).limit(1)
                )
            self.utc_timestamps = other is None
        return self.utc_timestamps

    def history(self, limit: int, offset: int):
        with self.session() as session:
            rows = session.scalars(
                select(EventRow).order_by(EventRow.id.desc()).offset(offset).limit(limit)
            ).all()
            return {
                "items": [json.loads(row.payload) for row in rows],
                "total": session.scalar(select(func.count()).select_from(EventRow)),
                "limit": limit,
                "offset": offset,
            }

    def delete_synthetic(self):
        with self.session.begin() as session:
            session.execute(delete(EventRow).where(EventRow.evidence_level == "L0_SYNTHETIC"))
            # Saved reports are derived from the deleted synthetic history.
            session.execute(delete(AnalyticsReportRow))
            session.add(audit_row("synthetic_history.deleted"))
