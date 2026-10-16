import ast
from pathlib import Path
from typing import get_args

import pytest
from fastapi.testclient import TestClient

from app.contracts import Scenario
from app.domain.acquisition import SCENARIOS, VIRTUAL_SENSOR_POSITIONS
from app.main import create_app

APP = Path(__file__).parents[1] / "app"


@pytest.mark.parametrize("legacy", [False, True])
def test_providers_declare_honest_status(settings, legacy):
    config = settings.model_copy(update={"legacy_lab_enabled": legacy})
    with TestClient(create_app(config)) as client:
        client.headers["Authorization"] = f"Bearer {settings.token}"
        statuses = {item["id"]: item["status"] for item in client.get("/api/v1/providers").json()}
    assert statuses == {
        "synthetic-native": "IMPLEMENTED_SYNTHETIC",
        "RUVIEW_STREAM": "INTEGRATED_LEGACY" if legacy else "BLOCKED",
        "ESP32_CSI": "BLOCKED",
        "MULTIMODAL": "PLANNED",
    }


def test_features_list_only_synthetic_implementations(client):
    statuses = {item["id"]: item["status"] for item in client.get("/api/v1/features").json()}
    assert statuses["analytics"] == "IMPLEMENTED_SYNTHETIC"
    assert statuses["automation_dry_run"] == "IMPLEMENTED_SYNTHETIC"
    assert {statuses[name] for name in ("vitals", "pose", "sleep")} == {"PLANNED"}
    assert set(statuses.values()) <= {"IMPLEMENTED_SYNTHETIC", "PLANNED"}


def test_start_reset_start_cycle_is_audited(client):
    assert client.post("/api/v1/simulation/start", json={"speed": 4}).status_code == 200
    reset = client.post("/api/v1/simulation/reset")
    assert reset.status_code == 200
    assert reset.json()["state"] == "stopped"
    assert reset.json()["latest"] is None
    assert client.post("/api/v1/simulation/start", json={"speed": 4}).status_code == 200
    assert client.post("/api/v1/simulation/stop").status_code == 200
    actions = [item["action"] for item in client.get("/api/v1/governance/status").json()["audit"]]
    assert actions[:4] == [
        "simulation.stop",
        "simulation.start",
        "simulation.reset",
        "simulation.start",
    ]


def test_catalog_constants_match_contracts_and_routes(client):
    assert tuple(get_args(Scenario)) == SCENARIOS
    assert tuple(client.get("/api/v1/simulation/scenarios").json()) == SCENARIOS
    positions = [tuple(item["position_m"]) for item in client.get("/api/v1/sensors").json()]
    assert positions == list(VIRTUAL_SENSOR_POSITIONS)


def test_routes_are_modules_not_closures_in_the_composition_root():
    tree = ast.parse((APP / "main.py").read_text(encoding="utf-8"))
    decorated = [
        node.name
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
        and any(
            isinstance(d, ast.Call) and getattr(d.func, "attr", "") in {"get", "post", "delete"}
            for d in node.decorator_list
        )
    ]
    assert decorated == []
