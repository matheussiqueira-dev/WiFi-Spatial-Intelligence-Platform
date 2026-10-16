from uuid import uuid4

import pytest
from alembic import command

from tests.test_storage_hardening import migration_config


def denials(client):
    audits = client.get("/api/v1/governance/status").json()["security_audit"]
    return {item["action"]: item["count"] for item in audits}


def test_only_protective_refusals_are_audited_as_operation_denied(client):
    assert client.post("/api/v1/simulation/pause").status_code == 409
    assert client.post("/api/v1/model-lab/jobs/absent/cancel").status_code == 409
    assert "operation.denied" not in denials(client)
    assert client.post("/api/v1/simulation/start", json={"speed": 4}).status_code == 200
    assert client.delete("/api/v1/events/synthetic").status_code == 409
    assert denials(client)["operation.denied"] == 1
    client.post("/api/v1/simulation/stop")


def test_job_queue_refuses_when_run_history_is_full(client):
    store = client.app.state.store
    with store.engine.begin() as connection:
        for index in range(100):
            connection.exec_driver_sql(
                "INSERT INTO model_lab_runs (id, created_at, payload) VALUES (?, ?, '{}')",
                (str(uuid4()), f"2026-01-01T00:00:{index:02d}+00:00"),
            )
    response = client.post("/api/v1/model-lab/jobs", json={"seed": 7})
    assert response.status_code == 409
    assert store.job_count() == 0


@pytest.mark.parametrize("target", ["0001", "base"])
def test_early_migrations_refuse_destructive_downgrade(tmp_path, target):
    config = migration_config(tmp_path / "downgrade.db")
    command.upgrade(config, "0002")
    with pytest.raises(RuntimeError, match="destructive downgrade"):
        command.downgrade(config, target)
