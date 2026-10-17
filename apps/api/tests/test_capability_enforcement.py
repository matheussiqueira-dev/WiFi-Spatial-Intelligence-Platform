from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.capabilities import CATALOG
from app.main import create_app
from tests.conftest import ORIGIN, TOKEN

NOW = datetime.now(UTC)
WINDOW = {"start": (NOW - timedelta(hours=1)).isoformat(), "end": NOW.isoformat()}
# (method, path, body, params, capability) for every capability-gated surface.
GATED = [
    ("get", "/api/v1/events", None, None, "spatial.presence"),
    ("post", "/api/v1/simulation/start", {"speed": 1}, None, "spatial.presence"),
    ("post", "/api/v1/simulation/stop", None, None, "spatial.presence"),
    ("get", "/api/v1/sensors", None, None, "spatial.presence"),
    ("get", "/api/v1/occupancy", None, None, "spatial.presence"),
    ("get", "/api/v1/analytics", None, WINDOW, "spatial.occupancy_analytics"),
    ("get", "/api/v1/analytics/replay", None, WINDOW, "spatial.occupancy_analytics"),
    ("get", "/api/v1/model-lab/runs", None, None, "spatial.activity_baseline"),
    ("get", "/api/v1/automation/rules", None, None, "automation.dry_run_rules"),
]
OPEN = ["/api/v1/system/status", "/api/v1/capabilities", "/api/v1/governance/status"]
NETWORK = ["/api/v1/network/report", "/api/v1/network/channel-plan", "/api/v1/network/config"]


def call(client, method, path, body, params):
    return getattr(client, method)(path, params=params, **({"json": body} if body else {}))


@pytest.fixture
def commercial(settings):
    config = settings.model_copy(update={"capability_profile": "commercial-br"})
    with TestClient(create_app(config)) as client:
        client.headers["Authorization"] = f"Bearer {TOKEN}"
        yield client


@pytest.mark.parametrize(("method", "path", "body", "params", "capability"), GATED)
def test_commercial_profile_refuses_lab_only_capabilities(
    commercial, method, path, body, params, capability
):
    response = call(commercial, method, path, body, params)
    assert response.status_code == 403
    assert capability in response.json()["detail"]


@pytest.mark.parametrize(("method", "path", "body", "params", "capability"), GATED)
def test_lab_profile_keeps_every_capability_available(
    client, method, path, body, params, capability
):
    assert call(client, method, path, body, params).status_code != 403


@pytest.mark.parametrize("path", OPEN + NETWORK)
def test_operational_and_network_surfaces_stay_open_in_commercial(commercial, path):
    assert commercial.get(path).status_code == 200


def test_authentication_is_checked_before_the_profile(commercial):
    assert (
        commercial.get("/api/v1/events", headers={"Authorization": "Bearer x"}).status_code == 401
    )


def test_commercial_profile_closes_the_live_stream(commercial):
    with pytest.raises(WebSocketDisconnect) as closed:
        with commercial.websocket_connect("/api/v1/stream", headers={"origin": ORIGIN}) as ws:
            ws.send_json({"token": TOKEN})
            ws.receive_json()
    assert closed.value.code == 1008


def test_every_gated_capability_is_declared_in_the_catalog():
    declared = {item.id for item in CATALOG}
    assert {capability for *_, capability in GATED} <= declared
