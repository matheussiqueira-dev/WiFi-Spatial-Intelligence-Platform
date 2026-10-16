import time

from fastapi.testclient import TestClient

from app.main import create_app
from tests.conftest import ORIGIN, TOKEN


def open_stream(client):
    return client.websocket_connect("/api/v1/stream", headers={"origin": ORIGIN})


def close_and_drain(client, ws):
    # Release the server slot before TestClient cancels the session task on exit.
    ws.close()
    deadline = time.monotonic() + 3
    while client.app.state.pipeline.subscribers and time.monotonic() < deadline:
        time.sleep(0.01)
    assert not client.app.state.pipeline.subscribers


def test_reconnecting_dashboard_does_not_exhaust_the_auth_failure_budget(settings):
    with TestClient(create_app(settings)) as client:
        for _ in range(35):
            with open_stream(client) as ws:
                ws.send_json({"token": TOKEN})
                assert ws.receive_json()["type"] == "status"
                close_and_drain(client, ws)
        denied = client.get("/api/v1/events", headers={"Authorization": "Bearer wrong"})
        assert denied.status_code == 401


def test_stream_subscribes_only_after_authentication(client):
    pipeline = client.app.state.pipeline
    with open_stream(client) as ws:
        assert not pipeline.subscribers
        ws.send_json({"token": TOKEN})
        assert ws.receive_json()["type"] == "status"
        assert len(pipeline.subscribers) == 1
        close_and_drain(client, ws)


def test_oversized_body_is_rejected_before_authentication(settings):
    with TestClient(create_app(settings)) as client:
        response = client.post(
            "/api/v1/simulation/start",
            content=b"{" + b" " * (1024 * 1024) + b"}",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 413
        chunked = client.post(
            "/api/v1/simulation/start",
            content=iter([b" " * 40000, b" " * 40000]),
            headers={"Content-Type": "application/json"},
        )
        assert chunked.status_code == 413
