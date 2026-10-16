import asyncio
import json
import threading
import time
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from websockets.asyncio.server import serve

from app.config import Settings
from app.contracts import RuViewEvent
from app.main import create_app
from app.ruview import RuViewProvider, normalize_update

TOKEN = "ruview-test-only-" + "x" * 40
SAMPLE = json.loads((Path(__file__).parent / "fixtures/ruview-sensing-update.json").read_text())


def frame(**overrides):
    return {**SAMPLE, "timestamp": time.time(), **overrides}


def test_captured_official_contract(monkeypatch):
    monkeypatch.setattr("app.ruview.time.time", lambda: SAMPLE["timestamp"])
    event = normalize_update(SAMPLE)
    assert event.source_id == "ruview-01"
    assert event.evidence_level == "L0_SYNTHETIC"
    assert event.measurements.ground_truth_positions == []
    assert event.measurements.occupancy_estimate == SAMPLE["estimated_persons"]
    assert event.model.id is None and event.quality.confidence is None
    assert RuViewEvent.model_validate_json(event.model_dump_json()) == event
    assert normalize_update(SAMPLE).event_id == event.event_id


@pytest.mark.parametrize(
    "patch",
    [
        {"source": "esp32"},
        {"type": "pose_data"},
        {"timestamp": float("nan")},
        {"timestamp": 1},
        {"timestamp": time.time() + 3600},
        {"tick": -1},
        {"tick": True},
        {"estimated_persons": 21},
        {"estimated_persons": True},
        {"classification": {}},
        {"classification": {"presence": "true"}},
        {"classification": {"presence": False}, "estimated_persons": 1},
    ],
)
def test_rejects_untrusted_contract(patch):
    with pytest.raises((ValueError, ValidationError)):
        normalize_update(frame(**patch))


def test_no_fabricated_count_or_ground_truth():
    event = normalize_update(frame(estimated_persons=None))
    assert event.measurements.presence_detected
    assert event.measurements.occupancy_estimate is None
    assert event.measurements.ground_truth_positions == []
    empty = normalize_update(frame(classification={"presence": False}, estimated_persons=None))
    assert empty.measurements.occupancy_estimate == 0
    for changes in [
        {"evidence_level": "L3_VALIDATED"},
        {"quality": {"confidence": 0.9}},
        {"measurements": {"presence_detected": True, "ground_truth_positions": [[1, 1]]}},
    ]:
        with pytest.raises(ValidationError):
            RuViewEvent.model_validate({**event.model_dump(), **changes})


@pytest.mark.parametrize(
    "url",
    [
        "http://example.com:80",
        "http://127.0.0.1:80/path",
        "http://user:pass@localhost:80",
        "http://localhost:80?token=secret",
        "https://127.0.0.1:80",
        "http://127.0.0.1",
    ],
)
def test_restricts_service_urls(url):
    with pytest.raises(ValidationError):
        Settings(token=TOKEN, ruview_http_url=url, _env_file=None)


@contextmanager
def upstream():
    """Real local HTTP + WebSocket servers; mutable fault injection, never paid/hardware."""
    state = {
        "source": "simulated",
        "frame_source": "simulated",
        "freeze": False,
        "close_once": False,
        "connections": 0,
        "tick": 0,
        "bad": False,
        "duplicates": False,
        "oversize": False,
        "nested": False,
        "ignored": False,
        "http_redirect": False,
        "ws_redirect": False,
        "http_requests": 0,
        "ws_requests": 0,
    }

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            state["http_requests"] += 1
            if self.headers.get("Authorization") != f"Bearer {TOKEN}":
                self.send_response(401)
                self.end_headers()
                return
            if state["http_redirect"]:
                self.send_response(302)
                self.send_header("Location", "/redirected")
                self.end_headers()
                return
            self.send_response(200)
            self.end_headers()
            self.wfile.write(
                json.dumps(
                    {"source": state["source"], "source_state": "synthetic", "status": "ready"}
                ).encode()
            )

        def log_message(self, *args):
            pass

    http = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    http_thread = threading.Thread(target=http.serve_forever, daemon=True)
    http_thread.start()
    ready = threading.Event()
    loop = asyncio.new_event_loop()
    holder = {}

    async def handler(ws):
        if ws.request.headers.get("Authorization") != f"Bearer {TOKEN}":
            await ws.close(1008)
            return
        state["connections"] += 1
        last = None
        try:
            while ws.close_code is None:
                if not state["freeze"]:
                    state["tick"] += 1
                    data = frame(tick=state["tick"], source=state["frame_source"])
                    raw = json.dumps(data)
                    if state["bad"]:
                        raw = "invalid-json"
                    if state["oversize"]:
                        raw = "x" * 300000
                    if state["nested"]:
                        raw = "[" * 100000 + "]" * 100000  # under the frame cap, deeper than json
                    if state["ignored"]:
                        raw = json.dumps({"type": "pose_data"})
                    if state["duplicates"] and last is not None:
                        raw = last
                    last = raw
                    await ws.send(raw)
                    if state["close_once"]:
                        state["close_once"] = False
                        await ws.close()
                        return
                await asyncio.sleep(0.03)
        except Exception:
            return

    async def start():
        def process_request(connection, request):
            state["ws_requests"] += 1
            if state["ws_redirect"]:
                response = connection.respond(302, "redirect")
                response.headers["Location"] = "/redirected"
                return response

        holder["server"] = await serve(handler, "127.0.0.1", 0, process_request=process_request)
        holder["port"] = holder["server"].sockets[0].getsockname()[1]
        ready.set()

    def run():
        asyncio.set_event_loop(loop)
        loop.run_until_complete(start())
        loop.run_forever()

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    assert ready.wait(3)
    try:
        yield (
            state,
            f"http://127.0.0.1:{http.server_port}",
            (f"ws://127.0.0.1:{holder['port']}/ws/sensing"),
        )
    finally:

        async def close():
            holder["server"].close()
            await holder["server"].wait_closed()

        asyncio.run_coroutine_threadsafe(close(), loop).result(3)
        loop.call_soon_threadsafe(loop.stop)
        thread.join(3)
        loop.close()
        http.shutdown()
        http.server_close()
        http_thread.join(3)


def configured(settings, urls):
    return settings.model_copy(
        update={
            "ruview_http_url": urls[0],
            "ruview_ws_url": urls[1],
            "ruview_token": TOKEN,
            "ruview_stale_seconds": 1,
            "legacy_lab_enabled": True,
        }
    )


def wait_for(client, predicate, seconds=5):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        state = client.get("/api/v1/system/status").json()
        if predicate(state):
            return state
        time.sleep(0.03)
    raise AssertionError(f"condition timed out: {state}")


def ruview_start(client):
    assert (
        client.post("/api/v1/sources/select", json={"source": "RUVIEW_STREAM"}).status_code == 200
    )
    assert client.post("/api/v1/simulation/start", json={}).status_code == 200


def test_real_transport_persistence_controls_and_source_switch(settings):
    with upstream() as (faults, *urls):
        config = configured(settings, urls)
        with TestClient(create_app(config)) as client:
            client.headers.update({"Authorization": f"Bearer {settings.token}"})
            with client.websocket_connect(
                "/api/v1/stream", headers={"Origin": settings.origins[0]}
            ) as ws:
                ws.send_json({"token": settings.token})
                assert ws.receive_json()["type"] == "status"
                ruview_start(client)
                packet = ws.receive_json()
                assert packet["type"] == "event"
                RuViewEvent.model_validate(packet["data"])
                assert any(
                    e["event_id"] == packet["data"]["event_id"]
                    for e in client.get("/api/v1/events").json()["items"]
                )
                ws.close()
                deadline = time.monotonic() + 3
                while client.app.state.pipeline.subscribers and time.monotonic() < deadline:
                    client.get("/api/v1/system/status")
                    time.sleep(0.01)
                assert not client.app.state.pipeline.subscribers
            assert (
                client.post("/api/v1/sources/select", json={"source": "SIMULATED"}).status_code
                == 409
            )
            client.post("/api/v1/simulation/pause")
            count = client.get("/api/v1/events").json()["total"]
            time.sleep(0.2)
            assert client.get("/api/v1/events").json()["total"] == count
            client.post("/api/v1/simulation/resume")
            wait_for(client, lambda s: s["produced_events"] > count)
            client.post("/api/v1/simulation/stop")
            saved = client.get("/api/v1/events").json()
            time.sleep(0.1)
            assert client.get("/api/v1/events").json() == saved
            stopped = client.get("/api/v1/system/status").json()["source_diagnostics"]
            assert stopped["service_status"] == "stopped" and stopped["last_error"] is None
            assert (
                client.post("/api/v1/sources/select", json={"source": "SIMULATED"}).status_code
                == 200
            )
            client.post("/api/v1/simulation/start", json={"speed": 4})
            wait_for(client, lambda s: s["produced_events"] >= 1)
            client.post("/api/v1/simulation/stop")
            mixed = client.get("/api/v1/events").json()
            assert {e["source_id"] for e in mixed["items"]} == {"native-01", "ruview-01"}
        with TestClient(create_app(config)) as restarted:
            restarted.headers.update({"Authorization": f"Bearer {settings.token}"})
            assert restarted.get("/api/v1/events").json() == mixed
            assert restarted.get("/api/v1/system/status").json()["state"] == "stopped"


def test_reconnect_after_disconnect_and_stale_stream(settings):
    with upstream() as (faults, *urls):
        faults["close_once"] = True
        with TestClient(create_app(configured(settings, urls))) as client:
            client.headers.update({"Authorization": f"Bearer {settings.token}"})
            ruview_start(client)
            wait_for(
                client,
                lambda s: (
                    s["source_diagnostics"]["reconnections"] >= 1 and s["produced_events"] >= 2
                ),
            )
            faults["freeze"] = True
            state = wait_for(
                client, lambda s: s["source_diagnostics"]["stale"] and not s["connected"]
            )
            assert state["provider"] == "RUVIEW_STREAM"
            assert state["source_diagnostics"]["last_error"]
            count = state["produced_events"]
            faults["freeze"] = False
            wait_for(client, lambda s: s["produced_events"] > count and s["connected"])


@pytest.mark.parametrize(
    "fault", ["source", "frame_source", "bad", "oversize", "nested", "ignored"]
)
def test_service_and_stream_failures_fail_closed(settings, fault):
    with upstream() as (faults, *urls):
        faults[fault] = "esp32" if fault in {"source", "frame_source"} else True
        with TestClient(create_app(configured(settings, urls))) as client:
            client.headers.update({"Authorization": f"Bearer {settings.token}"})
            ruview_start(client)
            state = wait_for(client, lambda s: s["source_diagnostics"]["last_error"])
            assert state["provider"] == "RUVIEW_STREAM" and not state["connected"]
            assert client.get("/api/v1/events").json()["total"] == 0
            started = time.monotonic()
            assert client.post("/api/v1/simulation/stop").status_code == 200
            assert time.monotonic() - started < 2
            faults[fault] = "simulated" if fault in {"source", "frame_source"} else False
            client.post("/api/v1/simulation/start", json={})
            wait_for(client, lambda s: s["produced_events"] >= 1)


def test_wrong_service_token(settings):
    with upstream() as (_, *urls):
        config = configured(settings, urls).model_copy(update={"ruview_token": "wrong"})
        with TestClient(create_app(config)) as client:
            client.headers.update({"Authorization": f"Bearer {settings.token}"})
            ruview_start(client)
            state = wait_for(client, lambda s: s["source_diagnostics"]["last_error"])
            assert "401" in state["source_diagnostics"]["last_error"]
            assert "wrong" not in json.dumps(state)
            assert state["produced_events"] == 0


def test_service_unavailable_and_cancel_during_probe(settings):
    with upstream() as (_, *urls):
        config = configured(settings, urls)
    with TestClient(create_app(config)) as client:
        client.headers.update({"Authorization": f"Bearer {settings.token}"})
        ruview_start(client)
        state = wait_for(client, lambda s: s["source_diagnostics"]["last_error"])
        assert not state["connected"] and state["produced_events"] == 0
        assert client.post("/api/v1/simulation/stop").status_code == 200


def test_duplicate_frames_are_not_persisted(settings):
    with upstream() as (faults, *urls):
        faults["duplicates"] = True
        with TestClient(create_app(configured(settings, urls))) as client:
            client.headers.update({"Authorization": f"Bearer {settings.token}"})
            ruview_start(client)
            wait_for(client, lambda s: s["source_diagnostics"]["duplicate_frames"] >= 2)
            client.post("/api/v1/simulation/stop")
            assert client.get("/api/v1/events").json()["total"] == 1


def test_stopping_during_connect_does_not_leave_socket_active(settings, monkeypatch):
    async def run():
        provider = RuViewProvider(settings)
        ready = threading.Event()
        release = threading.Event()

        def probe():
            ready.set()
            release.wait(2)

        monkeypatch.setattr(provider, "_probe", probe)
        await provider.connect()
        pending = asyncio.create_task(provider.next_event())
        await asyncio.to_thread(ready.wait, 2)
        await provider.disconnect()
        release.set()
        assert await pending is None
        assert not provider.active and provider.socket is None

    asyncio.run(run())


def test_source_selection_authorization_and_validation(client):
    assert (
        client.post(
            "/api/v1/sources/select",
            json={"source": "RUVIEW_STREAM"},
            headers={"Authorization": ""},
        ).status_code
        == 401
    )
    assert client.post("/api/v1/sources/select", json={"source": "ESP32_CSI"}).status_code == 422
    assert (
        client.post(
            "/api/v1/sources/select", json={"source": "RUVIEW_STREAM", "url": "http://evil"}
        ).status_code
        == 422
    )


def test_replay_is_idempotent_after_database_reopen(settings):
    event = normalize_update(frame())
    with TestClient(create_app(settings)) as client:
        assert client.app.state.store.write(event)
    with TestClient(create_app(settings)) as client:
        assert client.app.state.store.write(event) is False
        assert client.app.state.store.history(20, 0)["total"] == 1


@pytest.mark.parametrize("kind", ["http", "ws"])
def test_redirects_are_not_followed(settings, kind):
    with upstream() as (faults, *urls):
        faults[kind + "_redirect"] = True
        with TestClient(create_app(configured(settings, urls))) as client:
            client.headers.update({"Authorization": f"Bearer {settings.token}"})
            ruview_start(client)
            state = wait_for(client, lambda s: s["source_diagnostics"]["last_error"])
            client.post("/api/v1/simulation/stop")
            assert state["produced_events"] == 0
            assert faults[kind + "_requests"] == 1
