from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.application.network_health import degradation, trend
from app.main import create_app
from app.network_contracts import NetworkSample
from tests.conftest import TOKEN
from tests.test_network_diagnostics import sample

NOW = datetime(2026, 10, 17, 12, 0, tzinfo=UTC)
COLLECTOR = str(uuid4())


def series(start_minutes_ago, end_minutes_ago, step_seconds=30, **changes):
    """One collector sampling every `step_seconds` between two offsets from NOW."""
    rows = []
    offset = start_minutes_ago * 60
    while offset > end_minutes_ago * 60:
        rows.append(
            NetworkSample.model_validate(
                sample(
                    collector_id=COLLECTOR,
                    timestamp=(NOW - timedelta(seconds=offset)).isoformat(),
                    probe_rtt_ms=[1.0, 2.0, 1.5],
                )
                | changes
            )
        )
        offset -= step_seconds
    return rows


def codes(rows):
    return [alert.code for alert in degradation(rows, NOW)[0]]


def test_stable_link_raises_no_alert():
    rows = series(180, 0)
    alerts, abstentions, recent, baseline = degradation(rows, NOW)
    assert alerts == [] and abstentions == []
    assert recent.signal_mean_percent == baseline.signal_mean_percent == 80


def test_signal_drop_is_compared_with_the_same_series_baseline():
    rows = series(180, 60) + series(60, 0, signal_percent=60)
    assert codes(rows) == ["SIGNAL_DROP"]
    # 14 points is below the published threshold.
    assert codes(series(180, 60) + series(60, 0, signal_percent=66)) == []


def test_latency_must_double_and_exceed_margin():
    slow = series(180, 60) + series(60, 0, probe_rtt_ms=[40.0, 45.0, 42.0])
    assert codes(slow) == ["LATENCY_RISE"]
    # Doubling 2 ms is noise: the +20 ms margin keeps it quiet.
    assert codes(series(180, 60) + series(60, 0, probe_rtt_ms=[4.0, 5.0, 4.5])) == []


def test_packet_loss_and_disconnects():
    lossy = series(180, 60) + series(60, 0, probe_rtt_ms=[1.0, 2.0])
    alerts = degradation(lossy, NOW)[0]
    assert [alert.code for alert in alerts] == ["PACKET_LOSS"]
    assert alerts[0].recent == pytest.approx(100 / 3)
    flapping = series(180, 60)
    for minutes in (50, 40, 30):
        flapping += series(minutes + 1, minutes, step_seconds=30)
        flapping += series(minutes, minutes - 1, step_seconds=30, **DISCONNECTED)
    flapping += series(20, 0)
    assert "FREQUENT_DISCONNECTS" in codes(flapping)


DISCONNECTED = {
    "link_state": "DISCONNECTED",
    "signal_percent": None,
    "channel": None,
    "radio_type": None,
    "rx_mbps": None,
    "tx_mbps": None,
    "probe_sent": 0,
    "probe_rtt_ms": [],
    "probe_status": "NOT_RUN",
}


def test_insufficient_data_abstains_instead_of_alerting():
    alerts, abstentions, *_ = degradation(series(30, 0, signal_percent=20), NOW)
    assert alerts == []
    assert len(abstentions) == 2  # no baseline for signal or latency
    alerts, abstentions, *_ = degradation([], NOW)
    assert [alert.code for alert in alerts] == ["COLLECTOR_STALE"]
    assert len(abstentions) == 3


def test_trend_buckets_cover_the_window_without_gaps():
    start = NOW - timedelta(hours=3)
    buckets = trend(series(180, 0), start, NOW, timedelta(hours=1))
    assert [bucket.start for bucket in buckets] == [start + timedelta(hours=h) for h in range(3)]
    assert buckets[-1].end == NOW
    assert sum(bucket.summary.samples for bucket in buckets) == 360
    assert not any(bucket.summary.collector_stale for bucket in buckets)


def test_health_endpoint_is_authenticated_gated_and_advisory(client):
    now = datetime.now(UTC)
    for seconds in (90, 60, 30):
        payload = sample(timestamp=(now - timedelta(seconds=seconds)).isoformat())
        assert client.post("/api/v1/network/samples", json=payload).status_code == 200
    body = client.get("/api/v1/network/health?hours=2&bucket_minutes=30").json()
    assert body["mode"] == "ADVISORY"
    assert body["evidence_level"] == "L2_LIVE_UNVALIDATED"
    assert len(body["buckets"]) == 4
    assert body["recent"]["samples"] == 3
    assert body["abstentions"]  # no baseline yet
    assert client.get("/api/v1/network/health?bucket_minutes=45").status_code == 422
    assert client.get("/api/v1/network/health?location=Outro").json()["recent"]["samples"] == 0
    client.headers.clear()
    assert client.get("/api/v1/network/health").status_code == 401


def test_health_is_available_in_the_commercial_profile(settings):
    config = settings.model_copy(update={"capability_profile": "commercial-br"})
    with TestClient(create_app(config)) as client:
        client.headers["Authorization"] = f"Bearer {TOKEN}"
        assert client.get("/api/v1/network/health").status_code == 200


def test_erasure_by_location_is_confirmed_scoped_and_audited(client):
    now = datetime.now(UTC)
    for location in ("Sala", "Quarto"):
        stamp = (now - timedelta(seconds=30)).isoformat()
        client.post("/api/v1/network/samples", json=sample(location=location, timestamp=stamp))
    assert client.delete("/api/v1/network/history").status_code == 422
    assert client.delete("/api/v1/network/history?confirm=yes").status_code == 422
    body = client.delete("/api/v1/network/history?confirm=ERASE&location=Sala").json()
    assert body["erased"] == {"samples": 1, "surveys": 0}
    report = client.get("/api/v1/network/report").json()
    assert report["locations"] == ["Quarto"]
    assert client.delete("/api/v1/network/history?confirm=ERASE").json()["erased"]["samples"] == 1
    assert client.get("/api/v1/network/report").json()["total"] == 0
    actions = [item["action"] for item in client.get("/api/v1/governance/status").json()["audit"]]
    assert actions[:2] == ["network.history.erased", "network.location.erased"]
    client.headers.clear()
    assert client.delete("/api/v1/network/history?confirm=ERASE").status_code == 401
