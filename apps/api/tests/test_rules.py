import pytest

from app.contracts import SimulationConfig
from app.domain.rules import RuleSpec, matches
from app.simulator import SimulationProvider


def test_rule_dsl_is_bounded_and_never_executes_code():
    rule = RuleSpec(name="Presence preview", field="presence", threshold=1)
    assert matches(rule, {"presence_detected": True, "occupancy_estimate": 2})
    assert not matches(rule, {"presence_detected": False, "occupancy_estimate": 0})
    assert not matches(
        RuleSpec(name="Count", field="occupancy", threshold=2),
        {"presence_detected": True, "occupancy_estimate": None},
    )
    with pytest.raises(ValueError):
        RuleSpec(name="bad", field="__import__('os')", threshold=1)
    with pytest.raises(ValueError):
        RuleSpec(name="bad", field="presence", threshold=2)


def test_rules_persist_decide_and_revoke(client):
    body = {"name": "Preview", "field": "occupancy", "threshold": 2}
    created = client.post("/api/v1/automation/rules", json=body)
    assert created.status_code == 200
    rule = created.json()
    store = client.app.state.store
    provider = SimulationProvider(SimulationConfig(occupants=3))
    event = provider.sample()
    assert store.write(event)
    assert not store.write(event)
    decisions = client.get("/api/v1/automation/decisions").json()
    assert decisions["total"] == 1
    assert decisions["items"][0]["mode"] == "DRY_RUN"
    assert decisions["items"][0]["evidence_level"] == "L0_SYNTHETIC"
    assert client.post(f"/api/v1/automation/rules/{rule['id']}/revoke").status_code == 200
    store.write(provider.sample())
    assert client.get("/api/v1/automation/decisions").json()["total"] == 1
    assert client.get("/api/v1/automation/rules").json()["items"][0]["active"] is False
    assert (
        client.post("/api/v1/automation/rules", json={**body, "webhook": "http://evil"}).status_code
        == 422
    )
    assert client.get("/api/v1/automation/decisions?limit=201").status_code == 422
