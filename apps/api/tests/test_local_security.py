import json
import time

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.security import LocalLimiter


def test_limiter_classes_recovery_and_bounded_keys():
    now = [0.0]
    limiter = LocalLimiter({"auth": 2, "read": 3, "write": 1}, 10, 2, lambda: now[0])
    assert limiter.check("auth", "a") == 0
    assert limiter.check("auth", "a") == 0
    assert limiter.check("auth", "a") == 10
    assert limiter.check("write", "a") == 0
    assert limiter.check("read", "a") == 0
    for key in range(100):
        limiter.check("auth", str(key))
    assert len(limiter.entries) <= 2
    # Capacity rejects new identities instead of evicting the exhausted identity.
    assert limiter.check("auth", "a") == 10
    now[0] = 11
    assert limiter.check("auth", "a") == 0


def test_api_limits_audits_and_no_secret(settings):
    settings = settings.model_copy(update={"rate_auth": 2, "rate_write": 1, "rate_read": 5})
    sentinel = "secret-sentinel-never-log"
    with TestClient(create_app(settings)) as client:
        for _ in range(2):
            assert (
                client.get(
                    "/api/v1/events", headers={"Authorization": f"Bearer {sentinel}"}
                ).status_code
                == 401
            )
        denied = client.get("/api/v1/events", headers={"Authorization": f"Bearer {sentinel}"})
        assert denied.status_code == 429 and int(denied.headers["Retry-After"]) > 0
        client.headers["Authorization"] = f"Bearer {settings.token}"
        assert client.get("/api/v1/events").status_code == 200
        assert client.post("/api/v1/simulation/stop").status_code == 200
        assert client.post("/api/v1/simulation/stop").status_code == 429
        assert (
            client.get("/api/v1/events", headers={"Origin": "http://evil.invalid"}).status_code
            == 403
        )
        data = client.get("/api/v1/governance/status").json()["security_audit"]
        assert any(item["action"] == "auth.denied" and item["count"] == 2 for item in data)
        assert sentinel not in json.dumps(data) and settings.token not in json.dumps(data)
        assert all(item["correlation_id"] and item["result"] == "denied" for item in data)


def test_ws_denials_audited_without_payload(settings):
    from starlette.websockets import WebSocketDisconnect

    with TestClient(create_app(settings)) as client:
        try:
            with client.websocket_connect(
                "/api/v1/stream", headers={"Origin": settings.origins[0]}
            ) as ws:
                ws.send_json({"token": "secret-sentinel"})
                ws.receive_json()
        except WebSocketDisconnect:
            pass
        data = client.app.state.store.security_audits()
        assert any(item["action"] == "ws.auth_denied" for item in data)
        assert "secret-sentinel" not in json.dumps(data)


@pytest.mark.parametrize("mode", ["timeout", "malformed", "origin", "capacity"])
def test_ws_denial_categories(settings, mode):
    from starlette.websockets import WebSocketDisconnect

    settings = settings.model_copy(update={"ws_auth_timeout_seconds": 0.05})
    with TestClient(create_app(settings)) as client:
        if mode == "capacity":
            client.app.state.pipeline.subscribers.update(object() for _ in range(8))
        try:
            with client.websocket_connect(
                "/api/v1/stream",
                headers={
                    "Origin": "http://evil.invalid" if mode == "origin" else settings.origins[0]
                },
            ) as ws:
                if mode == "malformed":
                    ws.send_text("not-json-secret-sentinel")
                ws.receive_json()
        except WebSocketDisconnect:
            pass
        finally:
            if mode == "capacity":
                client.app.state.pipeline.subscribers.clear()
        expected = {
            "timeout": "ws.timeout",
            "malformed": "ws.auth_denied",
            "origin": "ws.origin_denied",
            "capacity": "ws.limit",
        }[mode]
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            data = client.app.state.store.security_audits()
            if any(item["action"] == expected for item in data):
                break
        assert any(item["action"] == expected for item in data)
        assert "secret-sentinel" not in json.dumps(data)


def test_audit_bounded_and_survives_reopen(client):
    store = client.app.state.store
    for _ in range(100):
        store.security_denial("auth.denied")
    assert len(store.security_audits()) == 1
    assert store.security_audits()[0]["count"] == 100
    with pytest.raises(ValueError):
        store.security_denial("arbitrary-secret-action")
