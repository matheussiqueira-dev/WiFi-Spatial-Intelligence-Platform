"""Facade over the per-context SQLite repositories in app.adapters.sqlite.

Keeps the historical Store interface stable for the pipeline, routes, scripts and tests;
new code should depend on the specific repository instead.
"""

from app.adapters.sqlite.audit import AuditRepository
from app.adapters.sqlite.database import Database, epoch_microseconds
from app.adapters.sqlite.events import CURRENT_SEGMENT, EventRepository
from app.adapters.sqlite.lab import LabRepository
from app.adapters.sqlite.models import (
    AnalyticsReportRow,
    AuditRow,
    Base,
    EventRow,
    ExperimentJobRow,
    LocalRuleRow,
    ModelRunRow,
    RuleDecisionRow,
    SecurityDenialRow,
    audit_row,
)
from app.adapters.sqlite.reports import ReportRepository
from app.adapters.sqlite.rules import RuleRepository
from app.contracts import Event

__all__ = [
    "AnalyticsReportRow",
    "AuditRow",
    "Base",
    "EventRow",
    "ExperimentJobRow",
    "LocalRuleRow",
    "ModelRunRow",
    "RuleDecisionRow",
    "SecurityDenialRow",
    "Store",
    "audit_row",
    "epoch_microseconds",
]


class Store:
    def __init__(self, url: str, retention: int):
        self.database = Database(url)
        self.engine = self.database.engine
        self.session = self.database.session
        self.events = EventRepository(self.database, retention)
        self.rules = RuleRepository(self.database)
        self.reports_repository = ReportRepository(self.database)
        self.lab = LabRepository(self.database)
        self.audit_log = AuditRepository(self.database)

    # Session state lives in the event repository; the pipeline sets segment_id.
    @property
    def retention(self):
        return self.events.retention

    @retention.setter
    def retention(self, value):
        self.events.retention = value

    @property
    def segment_id(self):
        return self.events.segment_id

    @segment_id.setter
    def segment_id(self, value):
        self.events.segment_id = value

    @property
    def utc_timestamps(self):
        return self.events.utc_timestamps

    @utc_timestamps.setter
    def utc_timestamps(self, value):
        self.events.utc_timestamps = value

    # Events and history.
    def write(self, event: Event, segment_id=CURRENT_SEGMENT):
        return self.events.write(event, segment_id)

    def observations(self, start, end, source_id=None, scenario=None, segment_id=None):
        return self.events.observations(start, end, source_id, scenario, segment_id)

    def observation_page(
        self, start, end, offset, limit, source_id=None, scenario=None, segment_id=None
    ):
        return self.events.observation_page(
            start, end, offset, limit, source_id, scenario, segment_id
        )

    def lexical_timestamps(self):
        return self.events.lexical_timestamps()

    def history(self, limit: int, offset: int):
        return self.events.history(limit, offset)

    def delete_synthetic(self):
        return self.events.delete_synthetic()

    # Dry-run rules.
    def create_rule(self, specification):
        return self.rules.create_rule(specification)

    def local_rules(self):
        return self.rules.local_rules()

    def revoke_rule(self, identifier):
        return self.rules.revoke_rule(identifier)

    def rule_decisions(self, limit, offset):
        return self.rules.rule_decisions(limit, offset)

    # Saved analytics reports.
    def save_report(self, report):
        return self.reports_repository.save_report(report)

    def reports(self, limit, offset):
        return self.reports_repository.reports(limit, offset)

    def report(self, identifier):
        return self.reports_repository.report(identifier)

    # Model lab runs and jobs.
    def register_model(self, card):
        return self.lab.register_model(card)

    def registered_models(self):
        return self.lab.registered_models()

    def unregister_model(self, identifier):
        return self.lab.unregister_model(identifier)

    def save_model_run(self, result):
        return self.lab.save_model_run(result)

    def model_runs(self, limit=20, offset=0):
        return self.lab.model_runs(limit, offset)

    def model_run(self, identifier):
        return self.lab.model_run(identifier)

    def model_run_count(self):
        return self.lab.model_run_count()

    def job_count(self):
        return self.lab.job_count()

    def save_job(self, identifier, payload):
        return self.lab.save_job(identifier, payload)

    def job(self, identifier):
        return self.lab.job(identifier)

    def interrupt_jobs(self):
        return self.lab.interrupt_jobs()

    # Audit trail and security denials.
    def audit(self, action: str):
        return self.audit_log.audit(action)

    def security_denial(self, action: str):
        return self.audit_log.security_denial(action)

    def security_audits(self):
        return self.audit_log.security_audits()

    def audits(self):
        return self.audit_log.audits()
