import hashlib
import hmac
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.adapters import webhook
from app.adapters.webhook import DeliveryResult
from app.application.alert_webhook import AlertWebhook
from app.config import Settings
from app.main import create_app
from tests.conftest import TOKEN
from tests.test_network_health import NOW, series

SECRET = "s" * 40


class Receiver(BaseHTTPRequestHandler):
    received: list[tuple[dict, bytes]] = []
    status = 200

    def do_POST(self):
        body = self.rfile.read(int(self.headers["Content-Length"]))
        Receiver.received.append((dict(self.headers), body))
        self.send_response(Receiver.status)
        if Receiver.status == 302:
            self.send_header("Location", "http://127.0.0.1:1/elsewhere")
        self.end_headers()

    def log_message(self, *args):
        pass


@pytest.fixture
def receiver():
    Receiver.received = []
    Receiver.status = 200
    server = HTTPServer(("127.0.0.1", 0), Receiver)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}/hook"
    server.shutdown()
    server.server_close()


def test_post_is_signed_and_verifiable(receiver):
    result = webhook.post(receiver, SECRET, b'{"event":"x"}')
    assert result == DeliveryResult(True, 200, None)
    headers, body = Receiver.received[0]
    expected = hmac.new(
        SECRET.encode(), headers["X-Spatial-Timestamp"].encode() + b"." + body, hashlib.sha256
    ).hexdigest()
    assert headers["X-Spatial-Signature"] == f"sha256={expected}"


def test_redirects_errors_and_unreachable_hosts_are_reported_not_followed(receiver):
    Receiver.status = 302
    assert webhook.post(receiver, SECRET, b"{}") == DeliveryResult(False, 302, "redirect_refused")
    assert len(Receiver.received) == 1  # the redirect target was never contacted
    Receiver.status = 500
    assert webhook.post(receiver, SECRET, b"{}").error == "http_error"
    unreachable = webhook.post("http://127.0.0.1:1/hook", SECRET, b"{}")
    assert unreachable == DeliveryResult(False, None, "connection_failed")


@pytest.mark.parametrize(
    "url",
    [
        "http://example.com/hook",
        "http://8.8.8.8/hook",
        "http://169.254.169.254/latest",
        "http://0.0.0.0:80/",
        "ftp://192.168.0.10/hook",
        "http://user:pass@192.168.0.10/hook",
        "http://homeassistant.local:8123/api/webhook/x",
    ],
)
def test_settings_refuse_public_dns_metadata_and_credentialed_targets(url):
    with pytest.raises(ValidationError):
        Settings(token=TOKEN, _env_file=None, alert_webhook_url=url, alert_webhook_secret=SECRET)


def test_settings_require_a_strong_secret_and_accept_private_ips():
    with pytest.raises(ValidationError):
        Settings(token=TOKEN, _env_file=None, alert_webhook_url="http://192.168.1.5:8123/x")
    for url in ("http://192.168.1.5:8123/api/webhook/abc", "https://10.0.0.2/x", "http://[::1]:9/"):
        assert (
            Settings(
                token=TOKEN, _env_file=None, alert_webhook_url=url, alert_webhook_secret=SECRET
            ).alert_webhook_url
            == url
        )


class Fake:
    def __init__(self, rows, delivered=True):
        self.rows = rows
        self.delivered = delivered
        self.sent: list[dict] = []
        self.log: list[dict] = []

    def read(self, start, end):
        return [row for row in self.rows if start <= row.timestamp <= end]

    def send(self, body):
        self.sent.append(json.loads(body))
        return DeliveryResult(self.delivered, 200 if self.delivered else None, None)


def worker(fake):
    return AlertWebhook(fake.read, fake.send, fake.log.append, 60)


def test_only_transitions_are_sent_per_location():
    degraded = series(180, 60) + series(60, 0, signal_percent=50)
    fake = Fake(degraded)
    alerts = worker(fake)
    alerts.cycle(NOW)
    alerts.cycle(NOW)  # still active: nothing new is sent
    assert [(m["event"], m["location"], m["alert"]["code"]) for m in fake.sent] == [
        ("alert.raised", "Escritorio", "SIGNAL_DROP")
    ]
    assert fake.sent[0]["evidence_level"] == "L2_LIVE_UNVALIDATED"
    fake.rows = series(180, 0)
    alerts.cycle(NOW)
    assert fake.sent[-1]["event"] == "alert.cleared"
    assert alerts.active == {}
    assert [entry["event"] for entry in fake.log] == ["alert.raised", "alert.cleared"]


def test_moving_the_computer_to_another_room_is_not_a_degradation():
    office = series(180, 60)
    bedroom = series(60, 0, signal_percent=40, location="Quarto")
    fake = Fake(office + bedroom)
    worker(fake).cycle(NOW)
    assert fake.sent == []


def test_failed_delivery_is_retried_on_the_next_cycle():
    fake = Fake(series(180, 60) + series(60, 0, signal_percent=50), delivered=False)
    alerts = worker(fake)
    alerts.cycle(NOW)
    assert alerts.active == {}
    fake.delivered = True
    alerts.cycle(NOW)
    assert [m["event"] for m in fake.sent] == ["alert.raised", "alert.raised"]
    assert len(alerts.active) == 1


def test_global_collector_silence_is_reported_once():
    fake = Fake(series(180, 10))
    worker(fake).cycle(NOW)
    assert [(m["location"], m["alert"]["code"]) for m in fake.sent] == [(None, "COLLECTOR_STALE")]


def test_webhook_routes_mask_the_receiver_path_and_send_a_test(settings, receiver):
    config = settings.model_copy(
        update={
            "alert_webhook_url": receiver,
            "alert_webhook_secret": SECRET,
            "alert_webhook_interval_seconds": 3600,
        }
    )
    with TestClient(create_app(config)) as client:
        client.headers["Authorization"] = f"Bearer {TOKEN}"
        status = client.get("/api/v1/network/webhook").json()
        assert status["configured"] is True
        assert status["destination"] == receiver.removesuffix("/hook")
        assert "/hook" not in json.dumps(status) and SECRET not in json.dumps(status)
        sent = client.post("/api/v1/network/webhook/test").json()
        assert sent["delivered"] is True
        assert sent["delivery"]["event"] == "webhook.test"
        assert json.loads(Receiver.received[-1][1])["event"] == "webhook.test"
        client.headers.clear()
        assert client.post("/api/v1/network/webhook/test").status_code == 401


def test_webhook_test_refuses_when_not_configured(client):
    assert client.get("/api/v1/network/webhook").json()["configured"] is False
    assert client.post("/api/v1/network/webhook/test").status_code == 409


def test_delivery_log_is_bounded(client):
    store = client.app.state.container.network_store
    for index in range(1005):
        store.record_delivery(
            {
                "id": f"00000000-0000-4000-8000-{index:012d}",
                "created_at": f"2026-10-17T00:{index // 60:02d}:{index % 60:02d}+00:00",
                "event": "webhook.test",
                "alert_code": None,
                "location": None,
                "delivered": True,
                "http_status": 200,
                "error": None,
            }
        )
    with store.session() as session:
        from app.adapters.network_store import WebhookDeliveryRow
        from app.adapters.sqlite.database import row_count

        assert row_count(session, WebhookDeliveryRow) == 1000
    assert store.deliveries(1)[0]["id"].endswith("000000001004")
