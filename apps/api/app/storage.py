import json
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy import String, Text, create_engine, delete, event, func, select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from app.contracts import Event
from app.domain.rules import RuleSpec, matches


def epoch_microseconds(timestamp: str) -> int:
    delta = datetime.fromisoformat(timestamp) - datetime(1970, 1, 1, tzinfo=UTC)
    return delta // timedelta(microseconds=1)


CURRENT_SEGMENT = object()


class Base(DeclarativeBase):
    pass


class EventRow(Base):
    __tablename__ = "sensing_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[str] = mapped_column(String(36), unique=True)
    timestamp: Mapped[str] = mapped_column(String(40), index=True)
    evidence_level: Mapped[str] = mapped_column(String(32))
    payload: Mapped[str] = mapped_column(Text)
    segment_id: Mapped[str | None] = mapped_column(String(36), index=True, nullable=True)


class AnalyticsReportRow(Base):
    __tablename__ = "analytics_reports"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    created_at: Mapped[str] = mapped_column(String(40))
    payload: Mapped[str] = mapped_column(Text)


class AuditRow(Base):
    __tablename__ = "audit_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    timestamp: Mapped[str] = mapped_column(String(40))
    action: Mapped[str] = mapped_column(String(64))


class SecurityDenialRow(Base):
    __tablename__ = "security_denials"
    action: Mapped[str] = mapped_column(String(64), primary_key=True)
    count: Mapped[int] = mapped_column()
    first_seen: Mapped[str] = mapped_column(String(40))
    last_seen: Mapped[str] = mapped_column(String(40))
    correlation_id: Mapped[str] = mapped_column(String(36))


class ModelRunRow(Base):
    __tablename__ = "model_lab_runs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    created_at: Mapped[str] = mapped_column(String(40))
    payload: Mapped[str] = mapped_column(Text)


class LocalRuleRow(Base):
    __tablename__ = "local_rules"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    active: Mapped[bool] = mapped_column()
    payload: Mapped[str] = mapped_column(Text)


class RuleDecisionRow(Base):
    __tablename__ = "rule_decisions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    created_at: Mapped[str] = mapped_column(String(40))
    payload: Mapped[str] = mapped_column(Text)


class ExperimentJobRow(Base):
    __tablename__ = "experiment_jobs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    payload: Mapped[str] = mapped_column(Text)


class Store:
    def __init__(self, url: str, retention: int):
        self.engine = create_engine(url, connect_args={"check_same_thread": False, "timeout": 15})

        @event.listens_for(self.engine, "connect")
        def configure_sqlite(connection, _):
            connection.create_function(
                "spatial_epoch_us", 1, epoch_microseconds, deterministic=True
            )
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute("PRAGMA busy_timeout=15000")

        self.session = sessionmaker(self.engine)
        self.retention = retention
        self.segment_id = None

    def write(self, event: Event, segment_id=CURRENT_SEGMENT):
        # The pipeline passes the segment captured at enqueue time; it may have changed since.
        if segment_id is CURRENT_SEGMENT:
            segment_id = self.segment_id
        with self.session.begin() as session:
            if session.scalar(select(EventRow.id).where(EventRow.event_id == str(event.event_id))):
                return False  # Idempotent replay after a RuView reconnect/backend restart.
            session.add(
                EventRow(
                    event_id=str(event.event_id),
                    timestamp=event.timestamp.isoformat(),
                    evidence_level=event.evidence_level,
                    payload=event.model_dump_json(),
                    segment_id=segment_id,
                )
            )
            session.flush()
            boundary = session.scalar(
                select(EventRow.id).order_by(EventRow.id.desc()).offset(self.retention).limit(1)
            )
            if boundary is not None:
                session.execute(delete(EventRow).where(EventRow.id <= boundary))
            rules = session.scalars(select(LocalRuleRow).where(LocalRuleRow.active)).all()
            if rules:
                available = 1000 - session.scalar(select(func.count()).select_from(RuleDecisionRow))
                for rule in rules[: max(0, available)]:
                    decision = {
                        "rule_id": rule.id,
                        "rule_version": 1,
                        "event_id": str(event.event_id),
                        "matched": matches(
                            RuleSpec(**json.loads(rule.payload)), event.measurements.model_dump()
                        ),
                        "mode": "DRY_RUN",
                        "evidence_level": "L0_SYNTHETIC",
                        "dispatched": False,
                    }
                    session.add(
                        RuleDecisionRow(
                            id=str(uuid4()),
                            created_at=datetime.now(UTC).isoformat(),
                            payload=json.dumps(decision),
                        )
                    )
        return True

    def create_rule(self, specification):
        with self.session.begin() as session:
            if session.scalar(select(func.count()).select_from(LocalRuleRow)) >= 20:
                raise ValueError("maximum 20 rules; review offline retention")
            identifier = str(uuid4())
            session.add(LocalRuleRow(id=identifier, active=True, payload=json.dumps(specification)))
            session.add(
                AuditRow(timestamp=datetime.now(UTC).isoformat(), action="automation.rule.created")
            )
        return {"id": identifier, "active": True, "version": 1, "mode": "DRY_RUN", **specification}

    def local_rules(self):
        with self.session() as session:
            return {
                "items": [
                    {
                        "id": r.id,
                        "active": r.active,
                        "version": 1,
                        "mode": "DRY_RUN",
                        **json.loads(r.payload),
                    }
                    for r in session.scalars(select(LocalRuleRow).order_by(LocalRuleRow.id))
                ],
                "maximum_rules": 20,
                "maximum_decisions": 1000,
                "decision_capacity_reached": session.scalar(
                    select(func.count()).select_from(RuleDecisionRow)
                )
                >= 1000,
            }

    def revoke_rule(self, identifier):
        with self.session.begin() as session:
            rule = session.get(LocalRuleRow, identifier)
            if rule is None:
                return False
            rule.active = False
            session.add(
                AuditRow(timestamp=datetime.now(UTC).isoformat(), action="automation.rule.revoked")
            )
        return True

    def rule_decisions(self, limit, offset):
        with self.session() as session:
            rows = session.scalars(
                select(RuleDecisionRow)
                .order_by(RuleDecisionRow.created_at.desc(), RuleDecisionRow.id.desc())
                .limit(limit)
                .offset(offset)
            )
            return {
                "items": [
                    {"id": r.id, "created_at": r.created_at, **json.loads(r.payload)} for r in rows
                ],
                "total": session.scalar(select(func.count()).select_from(RuleDecisionRow)),
                "limit": limit,
                "offset": offset,
            }

    def observations(self, start, end, source_id=None, scenario=None, segment_id=None):
        """Bounded snapshot; validate UTC and order in the analytics domain layer."""
        query = select(EventRow).where(
            func.spatial_epoch_us(EventRow.timestamp) >= epoch_microseconds(start.isoformat()),
            func.spatial_epoch_us(EventRow.timestamp) < epoch_microseconds(end.isoformat()),
        )
        if source_id:
            query = query.where(func.json_extract(EventRow.payload, "$.source_id") == source_id)
        if scenario:
            query = query.where(
                func.json_extract(EventRow.payload, "$.provenance.scenario") == scenario
            )
        if segment_id:
            query = query.where(EventRow.segment_id == segment_id)
        with self.session() as session:
            rows = session.scalars(query.limit(10001)).all()
            if len(rows) > 10000:
                raise ValueError("more than 10000 events; narrow the time range or source")
            return [
                {"event": json.loads(row.payload), "segment_id": row.segment_id} for row in rows
            ]

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
                .offset(100)
            )
            session.execute(delete(AnalyticsReportRow).where(AnalyticsReportRow.id.in_(obsolete)))
        self.audit("analytics.report.saved")
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

    def save_model_run(self, result):
        with self.session.begin() as session:
            session.add(
                ModelRunRow(
                    id=result["id"],
                    created_at=result["created_at"],
                    payload=json.dumps(result, allow_nan=False),
                )
            )
        self.audit("model_lab.run.saved")

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
                if data["state"] not in {"completed", "cancelled", "failed", "interrupted"}:
                    data.update(state="interrupted", error="process_restarted")
                    row.payload = json.dumps(data)

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

    def audit(self, action: str):
        with self.session.begin() as session:
            session.add(AuditRow(timestamp=datetime.now(UTC).isoformat(), action=action))

    def security_denial(self, action: str):
        allowed = {
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
        if action not in allowed:
            raise ValueError("unsupported security audit action")
        now = datetime.now(UTC).isoformat()
        table = SecurityDenialRow.__table__
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
                for r in session.scalars(select(AuditRow).order_by(AuditRow.id.desc()).limit(100))
            ]

    def delete_synthetic(self):
        with self.session.begin() as session:
            session.execute(delete(EventRow).where(EventRow.evidence_level == "L0_SYNTHETIC"))
            session.execute(delete(AnalyticsReportRow))
            session.add(
                AuditRow(
                    timestamp=datetime.now(UTC).isoformat(), action="synthetic_history.deleted"
                )
            )
