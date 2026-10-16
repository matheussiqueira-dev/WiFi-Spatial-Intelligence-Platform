"""Dry-run local rules and their decisions; decisions share the event transaction."""

import json
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import func, select

from app.adapters.sqlite.database import Database
from app.adapters.sqlite.models import LocalRuleRow, RuleDecisionRow, audit_row
from app.domain.rules import MAX_DECISIONS, MAX_RULES, RuleSpec, matches


def record_decisions(session, event) -> None:
    """Evaluate active rules inside the caller's transaction (ADR-007 atomicity)."""
    rules = session.scalars(select(LocalRuleRow).where(LocalRuleRow.active)).all()
    if not rules:
        return
    available = MAX_DECISIONS - session.scalar(select(func.count()).select_from(RuleDecisionRow))
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


class RuleRepository:
    def __init__(self, database: Database):
        self.session = database.session

    def create_rule(self, specification):
        with self.session.begin() as session:
            if session.scalar(select(func.count()).select_from(LocalRuleRow)) >= MAX_RULES:
                raise ValueError(f"maximum {MAX_RULES} rules; review offline retention")
            identifier = str(uuid4())
            session.add(LocalRuleRow(id=identifier, active=True, payload=json.dumps(specification)))
            session.add(audit_row("automation.rule.created"))
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
                "maximum_rules": MAX_RULES,
                "maximum_decisions": MAX_DECISIONS,
                "decision_capacity_reached": session.scalar(
                    select(func.count()).select_from(RuleDecisionRow)
                )
                >= MAX_DECISIONS,
            }

    def revoke_rule(self, identifier):
        with self.session.begin() as session:
            rule = session.get(LocalRuleRow, identifier)
            if rule is None:
                return False
            rule.active = False
            session.add(audit_row("automation.rule.revoked"))
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
