import hashlib
import hmac
import json
import re
import sqlite3

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.api import stream
from app.api.deps import RoleCheck, authorize
from app.bootstrap import access_token_key
from app.domain.access import ROLES, allows
from app.main import create_app
from tests.conftest import ORIGIN, TOKEN

# Declared policy for every write surface; every GET is viewer unless listed here.
WRITE_POLICY = {
    ("POST", "/api/v1/simulation/start"): "operator",
    ("POST", "/api/v1/simulation/{action}"): "operator",
    ("POST", "/api/v1/sources/select"): "operator",
    ("DELETE", "/api/v1/events/synthetic"): "admin",
    ("POST", "/api/v1/analytics/reports"): "operator",
    ("POST", "/api/v1/model-lab/jobs"): "operator",
    ("POST", "/api/v1/model-lab/jobs/{identifier}/cancel"): "operator",
    ("POST", "/api/v1/model-lab/runs"): "operator",
    ("POST", "/api/v1/automation/rules"): "operator",
    ("POST", "/api/v1/automation/rules/{identifier}/revoke"): "operator",
    ("POST", "/api/v1/network/samples"): "operator",
    ("POST", "/api/v1/network/channel-surveys"): "operator",
    ("POST", "/api/v1/network/config"): "operator",
    ("DELETE", "/api/v1/network/history"): "admin",
    ("POST", "/api/v1/network/webhook/test"): "admin",
    ("POST", "/api/v1/access/tokens"): "admin",
    ("POST", "/api/v1/access/tokens/{identifier}/revoke"): "admin",
}
READ_EXCEPTIONS = {("GET", "/api/v1/access/tokens"): "admin"}
PUBLIC = {"/api/v1/health"}


def api_routes(routes):
    # FastAPI keeps included routers as nested branches; walk them down to the routes.
    for route in routes:
        nested = getattr(route, "original_router", None)
        if nested is not None:
            yield from api_routes(nested.routes)
        elif isinstance(route, APIRoute):
            yield route


def declared_routes(app):
    """(method, path, minimum role, dependency callables) for every authenticated route."""
    for route in api_routes(app.routes):
        if route.path in PUBLIC:
            continue
        calls = [item.call for item in route.dependant.dependencies]
        roles = [call.minimum for call in calls if isinstance(call, RoleCheck)]
        for method in route.methods:
            yield method, route.path, roles, calls


@pytest.fixture
def roomy(settings):
    # The matrix sends one request per route and role; keep the local limiter out of the way.
    return settings.model_copy(
        update={"rate_read": 100000, "rate_write": 10000, "rate_auth": 10000}
    )


def issue(client, role, label=None):
    response = client.post(
        "/api/v1/access/tokens", json={"label": label or f"{role} test", "role": role}
    )
    assert response.status_code == 201, response.text
    return response.json()


def bearer(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def app_client(roomy):
    with TestClient(create_app(roomy)) as client:
        client.headers.update(bearer(TOKEN))
        yield client


@pytest.fixture
def tokens(app_client):
    return {role: issue(app_client, role)["token"] for role in ROLES}


def concrete(path):
    return re.sub(r"\{[^}]+\}", "00000000-0000-4000-8000-000000000000", path)


def test_every_authenticated_route_declares_one_role_after_authentication(app_client):
    routes = list(declared_routes(app_client.app))
    # Guard against a vacuous pass if route discovery ever breaks.
    assert len(routes) >= 45
    for method, path, roles, calls in routes:
        assert len(roles) == 1, f"{method} {path} must declare exactly one role"
        # 401 (authorize) before the role, and the role before any capability check.
        role_index = next(i for i, call in enumerate(calls) if isinstance(call, RoleCheck))
        assert calls.index(authorize) < role_index, f"{method} {path}"
        capability_checks = [
            i for i, call in enumerate(calls) if getattr(call, "__name__", "") == "check"
        ]
        assert all(role_index < i for i in capability_checks), f"{method} {path}"


def test_route_policy_matches_the_declared_matrix(app_client):
    actual = {
        (method, path): roles[0] for method, path, roles, _ in declared_routes(app_client.app)
    }
    writes = {key: role for key, role in actual.items() if key[0] != "GET"}
    assert writes == WRITE_POLICY
    for key, role in actual.items():
        if key[0] == "GET":
            assert role == READ_EXCEPTIONS.get(key, "viewer"), key


def test_role_matrix_refuses_below_minimum_and_admits_at_or_above(app_client, tokens):
    for method, path, roles, _ in declared_routes(app_client.app):
        minimum = roles[0]
        for role, token in tokens.items():
            response = app_client.request(method, concrete(path), headers=bearer(token))
            denied = response.status_code == 403 and "role" in response.json().get("detail", "")
            assert denied == (not allows(role, minimum)), (role, method, path, response.text)
            if denied:
                assert response.json()["detail"] == f"role {minimum} required"


def test_authentication_comes_before_the_role(app_client):
    for method, path, _, _ in declared_routes(app_client.app):
        response = app_client.request(method, concrete(path), headers=bearer("wsp_" + "z" * 43))
        assert response.status_code == 401, (method, path)


def test_role_is_checked_before_the_capability_profile(roomy):
    config = roomy.model_copy(update={"capability_profile": "commercial-br"})
    with TestClient(create_app(config)) as client:
        client.headers.update(bearer(TOKEN))
        viewer = issue(client, "viewer")["token"]
        operator = issue(client, "operator")["token"]
        # Lab-only write: the viewer learns about the role, not about the profile.
        refused = client.post("/api/v1/simulation/stop", headers=bearer(viewer))
        assert refused.status_code == 403 and refused.json()["detail"] == "role operator required"
        disabled = client.post("/api/v1/simulation/stop", headers=bearer(operator))
        assert disabled.status_code == 403 and "capability" in disabled.json()["detail"]
        # Reads: viewer passes the role and meets the profile.
        assert client.get("/api/v1/events", headers=bearer(viewer)).status_code == 403
        assert client.get("/api/v1/network/report", headers=bearer(viewer)).status_code == 200


def test_identity_reports_role_without_the_token(app_client, tokens):
    me = app_client.get("/api/v1/access/me").json()
    assert me == {
        "subject_id": "bootstrap",
        "label": "SPATIAL_TOKEN",
        "role": "admin",
        "bootstrap": True,
    }
    viewer = app_client.get("/api/v1/access/me", headers=bearer(tokens["viewer"])).json()
    assert viewer["role"] == "viewer" and viewer["bootstrap"] is False
    assert tokens["viewer"] not in json.dumps(viewer)


def test_token_is_shown_once_and_stored_only_as_a_keyed_hash(app_client, roomy):
    created = app_client.post(
        "/api/v1/access/tokens", json={"label": "Ana — notebook", "role": "operator"}
    )
    assert created.status_code == 201
    assert created.headers["Cache-Control"] == "no-store"
    body = created.json()
    token = body["token"]
    assert token.startswith("wsp_") and len(token) >= 40
    listing = app_client.get("/api/v1/access/tokens")
    assert token not in listing.text and "hash" not in listing.text
    item = next(i for i in listing.json()["items"] if i["id"] == body["id"])
    assert item["label"] == "Ana — notebook" and item["role"] == "operator" and item["active"]
    expected = hmac.new(access_token_key(roomy), token.encode(), hashlib.sha256).hexdigest()
    database = roomy.database_url.removeprefix("sqlite:///")
    with sqlite3.connect(database) as connection:
        stored = connection.execute(
            "select token_hash from access_tokens where id = ?", (body["id"],)
        ).fetchone()[0]
        dump = "\n".join(connection.iterdump())
    assert stored == expected and stored != hashlib.sha256(token.encode()).hexdigest()
    assert token not in dump
    governance = app_client.get("/api/v1/governance/status").text
    assert token not in governance and TOKEN not in governance


def test_revocation_takes_effect_on_the_next_request(app_client):
    issued = issue(app_client, "operator")
    assert app_client.get("/api/v1/events", headers=bearer(issued["token"])).status_code == 200
    revoked = app_client.post(f"/api/v1/access/tokens/{issued['id']}/revoke")
    assert revoked.status_code == 200 and revoked.json() == {"revoked": True}
    assert app_client.get("/api/v1/events", headers=bearer(issued["token"])).status_code == 401
    # Revocation keeps the record, is idempotent and unknown identifiers are 404.
    item = next(i for i in app_client.get("/api/v1/access/tokens").json()["items"])
    assert item["active"] is False and item["revoked_at"] and item["last_used_at"]
    assert app_client.post(f"/api/v1/access/tokens/{issued['id']}/revoke").status_code == 200
    assert app_client.post("/api/v1/access/tokens/nope/revoke").status_code == 404
    actions = [a["action"] for a in app_client.get("/api/v1/governance/status").json()["audit"]]
    assert actions.count("access.token.revoked") == 1


def test_audit_records_actor_and_subject(app_client, tokens):
    operator = app_client.get("/api/v1/access/me", headers=bearer(tokens["operator"])).json()
    rule = app_client.post(
        "/api/v1/automation/rules",
        json={"name": "presença", "field": "presence", "threshold": 1},
        headers=bearer(tokens["operator"]),
    ).json()
    audit = app_client.get("/api/v1/governance/status").json()["audit"]
    created = next(a for a in audit if a["action"] == "automation.rule.created")
    assert created["subject_id"] == rule["id"]
    assert created["actor_id"] == operator["subject_id"]
    issued = next(a for a in audit if a["action"] == "access.token.created")
    assert issued["actor_id"] == "bootstrap"


def test_role_denials_are_aggregated_without_token(app_client, tokens):
    assert (
        app_client.post("/api/v1/simulation/stop", headers=bearer(tokens["viewer"])).status_code
        == 403
    )
    audits = app_client.get("/api/v1/governance/status").json()["security_audit"]
    assert any(a["action"] == "role.denied" and a["count"] == 1 for a in audits)
    assert tokens["viewer"] not in json.dumps(audits)


@pytest.mark.parametrize(
    "body",
    [
        {"label": "", "role": "viewer"},
        {"label": "x" * 49, "role": "viewer"},
        {"label": "linha\nquebrada", "role": "viewer"},
        {"label": "ok", "role": "root"},
        {"label": "ok", "role": "viewer", "token": "chosen"},
    ],
)
def test_token_requests_are_validated(app_client, body):
    assert app_client.post("/api/v1/access/tokens", json=body).status_code == 422


def test_active_tokens_are_bounded(app_client, monkeypatch):
    from app.adapters.sqlite import access

    monkeypatch.setattr(access, "MAX_ACTIVE_TOKENS", 2)
    issue(app_client, "viewer")
    second = issue(app_client, "viewer")
    assert (
        app_client.post(
            "/api/v1/access/tokens", json={"label": "extra", "role": "viewer"}
        ).status_code
        == 409
    )
    app_client.post(f"/api/v1/access/tokens/{second['id']}/revoke")
    issue(app_client, "viewer")


def test_viewer_watches_the_stream_and_revocation_closes_it(app_client, tokens, monkeypatch):
    monkeypatch.setattr(stream, "REVALIDATE_SECONDS", 0)
    viewer = app_client.get("/api/v1/access/me", headers=bearer(tokens["viewer"])).json()
    with pytest.raises(WebSocketDisconnect) as closed:
        with app_client.websocket_connect("/api/v1/stream", headers={"Origin": ORIGIN}) as ws:
            ws.send_json({"token": tokens["viewer"]})
            assert ws.receive_json()["type"] == "status"
            app_client.post(f"/api/v1/access/tokens/{viewer['subject_id']}/revoke")
            for _ in range(5):
                ws.receive_json()
    assert closed.value.code == 1008


def test_stream_refuses_a_revoked_token(app_client):
    issued = issue(app_client, "viewer")
    app_client.post(f"/api/v1/access/tokens/{issued['id']}/revoke")
    with pytest.raises(WebSocketDisconnect) as closed:
        with app_client.websocket_connect("/api/v1/stream", headers={"Origin": ORIGIN}) as ws:
            ws.send_json({"token": issued["token"]})
            ws.receive_json()
    assert closed.value.code == 1008


def test_rotating_the_bootstrap_token_invalidates_derived_personal_tokens(roomy):
    with TestClient(create_app(roomy)) as client:
        client.headers.update(bearer(TOKEN))
        token = issue(client, "viewer")["token"]
    rotated = roomy.model_copy(update={"token": "rotated-" + "y" * 40})
    with TestClient(create_app(rotated)) as client:
        assert client.get("/api/v1/access/me", headers=bearer(token)).status_code == 401


def test_explicit_access_key_survives_bootstrap_rotation(roomy):
    keyed = roomy.model_copy(update={"access_token_key": "k" * 40})
    with TestClient(create_app(keyed)) as client:
        client.headers.update(bearer(TOKEN))
        token = issue(client, "viewer")["token"]
    rotated = keyed.model_copy(update={"token": "rotated-" + "y" * 40})
    with TestClient(create_app(rotated)) as client:
        assert client.get("/api/v1/access/me", headers=bearer(token)).status_code == 200


def test_short_access_key_is_rejected(settings):
    from pydantic import ValidationError

    from app.config import Settings

    with pytest.raises(ValidationError):
        Settings(token=TOKEN, access_token_key="short", _env_file=None)
