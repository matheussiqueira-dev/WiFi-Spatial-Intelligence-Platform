"""ORM tables. Alembic migrations are the schema source; a test compares both at head."""

from datetime import UTC, datetime

from sqlalchemy import String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


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
    # Identifier of the affected record (e.g. a rule); never tokens, IPs or payloads.
    subject_id: Mapped[str | None] = mapped_column(String(36), nullable=True)


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
    created_at: Mapped[str | None] = mapped_column(String(40), nullable=True)
    revoked_at: Mapped[str | None] = mapped_column(String(40), nullable=True)


class RuleDecisionRow(Base):
    __tablename__ = "rule_decisions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    created_at: Mapped[str] = mapped_column(String(40))
    payload: Mapped[str] = mapped_column(Text)


class ExperimentJobRow(Base):
    __tablename__ = "experiment_jobs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    payload: Mapped[str] = mapped_column(Text)


def audit_row(action: str, subject_id: str | None = None) -> AuditRow:
    return AuditRow(timestamp=datetime.now(UTC).isoformat(), action=action, subject_id=subject_id)
