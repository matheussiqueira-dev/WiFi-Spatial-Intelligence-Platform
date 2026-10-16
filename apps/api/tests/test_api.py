import asyncio
import time
from contextlib import ExitStack

import pytest
from conftest import ORIGIN, TOKEN
from fastapi.testclient import TestClient
from pydantic import TypeAdapter
from starlette.websockets import WebSocketDisconnect

from app.contracts import Event, SimulationConfig
from app.main import create_app
from app.simulator import SimulationProvider


def wait_events(client, count=1):
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        result = client.get("/api/v1/events").json()
        if result["total"] >= count:
            return result
        time.sleep(0.03)
    raise AssertionError("Simulation did not persist events in time")


def test_auth_origin_and_validation(client):
    assert client.get("/api/v1/health").json()["mode"] == "simulation-only"
    assert client.get("/api/v1/events", headers={"Authorization": ""}).status_code == 401
    assert (
        client.get("/api/v1/events", headers={"Origin": "https://untrusted.example"}).status_code
        == 403
    )
    assert client.post("/api/v1/simulation/start", json={"occupants": 21}).status_code == 422
    assert client.get("/api/v1/events?limit=201").status_code == 422
    assert client.get("/api/v1/events?offset=-1").status_code == 422
    assert client.post("/api/v1/simulation/unknown").status_code == 404
    assert client.post("/api/v1/simulation/resume").status_code == 409
    assert len(client.get("/api/v1/sensors").json()) == 6
    assert client.get("/api/v1/validation").json()["real_data_validated"] is False
    assert client.get("/api/v1/models").json()["items"] == []


def test_control_pause_stop_history_and_audit(client, settings):
    assert client.post("/api/v1/simulation/start", json={"speed": 4}).status_code == 200
    assert client.post("/api/v1/simulation/start", json={}).status_code == 409
    assert client.delete("/api/v1/events/synthetic").status_code == 409
    wait_events(client, 3)
    assert client.post("/api/v1/simulation/pause").json()["state"] == "paused"
    paused = client.get("/api/v1/events").json()["total"]
    time.sleep(0.35)
    assert client.get("/api/v1/events").json()["total"] == paused
    assert client.post("/api/v1/simulation/resume").json()["state"] == "running"
    wait_events(client, paused + 1)
    assert client.post("/api/v1/simulation/stop").json()["state"] == "stopped"
    history = client.get("/api/v1/events?limit=2&offset=1").json()
    assert len(history["items"]) == 2
    time.sleep(0.3)
    assert client.get("/api/v1/events").json()["total"] == history["total"]
    with TestClient(create_app(settings)) as restarted:
        restarted.headers.update({"Authorization": f"Bearer {TOKEN}"})
        assert restarted.get("/api/v1/events").json()["total"] == history["total"]
        assert restarted.get("/api/v1/system/status").json()["state"] == "stopped"
    assert client.delete("/api/v1/events/synthetic").status_code == 200
    assert client.get("/api/v1/events").json()["total"] == 0
    assert len(client.get("/api/v1/governance/status").json()["audit"]) == 5


def test_retention_keeps_newest_and_unique_events(client):
    store = client.app.state.store
    store.retention = 3
    provider = SimulationProvider(SimulationConfig())
    for _ in range(8):
        store.write(provider.sample())
    history = store.history(20, 0)
    assert history["total"] == 3
    assert [e["provenance"]["tick"] for e in history["items"]] == [7, 6, 5]
    assert len({e["event_id"] for e in history["items"]}) == 3


def test_websocket_stream_auth_and_persistence(client):
    with client.websocket_connect("/api/v1/stream", headers={"Origin": ORIGIN}) as ws:
        ws.send_json({"token": TOKEN})
        assert ws.receive_json()["data"]["state"] == "stopped"
        assert client.post("/api/v1/simulation/start", json={"speed": 4}).status_code == 200
        packet = ws.receive_json()
        assert packet["type"] == "event"
        event = TypeAdapter(Event).validate_python(packet["data"])
        assert event.evidence_level == "L0_SYNTHETIC"
        assert any(e["event_id"] == str(event.event_id) for e in wait_events(client)["items"])
        assert client.post("/api/v1/simulation/stop").status_code == 200

        ws.close()
        deadline = time.monotonic() + 3
        while client.app.state.pipeline.subscribers and time.monotonic() < deadline:
            client.get("/api/v1/system/status")
            time.sleep(0.01)
        assert not client.app.state.pipeline.subscribers


@pytest.mark.parametrize(
    "origin,token",
    [("https://untrusted.example", TOKEN), (ORIGIN, "invalid"), (ORIGIN, "não-ascii")],
)
def test_websocket_rejects_untrusted_access(client, origin, token):
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/api/v1/stream", headers={"Origin": origin}) as ws:
            ws.send_json({"token": token})
            ws.receive_json()


def test_disconnect_stops_with_honest_error(client):
    client.post("/api/v1/simulation/start", json={"scenario": "disconnect", "speed": 4})
    wait_events(client, 5)
    deadline = time.monotonic() + 3
    while time.monotonic() < deadline:
        state = client.get("/api/v1/system/status").json()
        if state["state"] == "stopped":
            assert state["error"]
            assert not state["connected"]
            return
        time.sleep(0.05)
    raise AssertionError("disconnect did not stop")


def test_websocket_connection_limit(client):
    with ExitStack() as stack:
        sockets = []
        for _ in range(8):
            ws = stack.enter_context(
                client.websocket_connect("/api/v1/stream", headers={"Origin": ORIGIN})
            )
            ws.send_json({"token": TOKEN})
            assert ws.receive_json()["type"] == "status"
            sockets.append(ws)
        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect("/api/v1/stream", headers={"Origin": ORIGIN}):
                pass
        # Close the transport and verify application cleanup before TestClient
        # cancels its session tasks during ExitStack teardown.
        for ws in sockets:
            ws.close()
        deadline = time.monotonic() + 3
        while client.app.state.pipeline.subscribers and time.monotonic() < deadline:
            client.get("/api/v1/system/status")
            time.sleep(0.01)
        assert not client.app.state.pipeline.subscribers
    with client.websocket_connect("/api/v1/stream", headers={"Origin": ORIGIN}) as ws:
        ws.send_json({"token": TOKEN})
        assert ws.receive_json()["type"] == "status"
        ws.close()
        deadline = time.monotonic() + 3
        while client.app.state.pipeline.subscribers and time.monotonic() < deadline:
            client.get("/api/v1/system/status")
            time.sleep(0.01)
        assert not client.app.state.pipeline.subscribers


@pytest.mark.parametrize("frame", [[], {}, {"token": 42}, {"token": None}])
def test_websocket_rejects_malformed_auth(client, frame):
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/api/v1/stream", headers={"Origin": ORIGIN}) as ws:
            ws.send_json(frame)
            ws.receive_json()


def test_storage_failure_stops_without_publishing_fake_success(client, monkeypatch):
    def fail_write(event, segment_id=None):
        raise OSError("injected storage failure")

    monkeypatch.setattr(client.app.state.store, "write", fail_write)
    client.post("/api/v1/simulation/start", json={"speed": 4})
    deadline = time.monotonic() + 3
    while time.monotonic() < deadline:
        state = client.get("/api/v1/system/status").json()
        if state["error"]:
            assert state["state"] == "stopped"
            assert not state["connected"]
            assert state["latest"] is None
            assert client.get("/api/v1/events").json()["total"] == 0
            return
        time.sleep(0.02)
    raise AssertionError("storage failure was not reported")


def test_slow_visualization_drops_frames_but_keeps_persistent_events(client):
    slow_subscriber = asyncio.Queue(maxsize=1)
    pipeline = client.app.state.pipeline
    pipeline.subscribers.add(slow_subscriber)
    client.post("/api/v1/simulation/start", json={"speed": 4})
    wait_events(client, 8)
    client.post("/api/v1/simulation/stop")
    state = client.get("/api/v1/system/status").json()
    assert slow_subscriber.qsize() == 1
    assert state["dropped_visualization_events"] >= 7
    assert state["produced_events"] == client.get("/api/v1/events").json()["total"]
    pipeline.subscribers.discard(slow_subscriber)
