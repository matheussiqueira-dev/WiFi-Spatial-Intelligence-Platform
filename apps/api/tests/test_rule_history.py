import sqlite3
from contextlib import closing
from datetime import datetime

from alembic import command

from tests.test_storage_hardening import migration_config

RULE = {"name": "Sala ocupada", "field": "occupancy", "threshold": 2}


def audit_trail(client):
    return client.get("/api/v1/governance/status").json()["audit"]


def test_rule_lifecycle_is_timestamped_and_audited_with_its_id(client):
    created = client.post("/api/v1/automation/rules", json=RULE).json()
    assert datetime.fromisoformat(created["created_at"]).tzinfo is not None
    assert created["revoked_at"] is None
    rule_id = created["id"]
    assert client.post(f"/api/v1/automation/rules/{rule_id}/revoke").status_code == 200
    first = client.get("/api/v1/automation/rules").json()["items"][0]
    assert first["active"] is False
    assert first["revoked_at"] >= first["created_at"]
    # A second revocation keeps the original time and is not audited again.
    assert client.post(f"/api/v1/automation/rules/{rule_id}/revoke").status_code == 200
    assert client.get("/api/v1/automation/rules").json()["items"][0] == first
    trail = [item for item in audit_trail(client) if item["action"].startswith("automation.rule")]
    assert [(item["action"], item.get("subject_id")) for item in trail] == [
        ("automation.rule.revoked", rule_id),
        ("automation.rule.created", rule_id),
    ]
    assert all("subject_id" not in item for item in audit_trail(client) if item not in trail)


def test_migration_keeps_older_rules_without_fabricated_times(tmp_path):
    database = tmp_path / "rules.db"
    config = migration_config(database)
    command.upgrade(config, "0008")
    with closing(sqlite3.connect(database)) as connection, connection:
        connection.execute(
            "INSERT INTO local_rules (id, active, payload) VALUES (?, 1, ?)",
            (
                "00000000-0000-4000-8000-000000000001",
                '{"name":"x","field":"presence","threshold":1}',
            ),
        )
        connection.execute(
            "INSERT INTO audit_events (timestamp, action) VALUES ('2026-01-01T00:00:00+00:00', 'a')"
        )
    command.upgrade(config, "head")
    with closing(sqlite3.connect(database)) as connection:
        assert connection.execute(
            "SELECT active, created_at, revoked_at FROM local_rules"
        ).fetchall() == [(1, None, None)]
        assert connection.execute("SELECT action, subject_id FROM audit_events").fetchall() == [
            ("a", None)
        ]
