from datetime import UTC, datetime, timedelta
from uuid import uuid4

from app.adapters.network_store import NetworkStore
from app.adapters.windows_wifi import parse_interfaces, private_gateway
from app.application.network_diagnostics import summarize
from app.network_contracts import NetworkSample


def sample(**changes):
    return {
        "sample_id": str(uuid4()),
        "collector_id": str(uuid4()),
        "timestamp": datetime.now(UTC).isoformat(),
        "location": "Escritorio",
        "link_state": "CONNECTED",
        "signal_percent": 80,
        "channel": 149,
        "radio_type": "802.11ac",
        "rx_mbps": 433.3,
        "tx_mbps": 433.3,
        "probe_sent": 3,
        "probe_rtt_ms": [1.0, 2.0],
        "probe_status": "COMPLETED",
    } | changes


def test_pt_en_collector_whitelists_fields_and_never_exports_identity():
    for text in (
        "Nome : Wi-Fi\nEstado : conectado\nSSID : PRIVATE\nBSSID : aa:bb\n"
        "Sinal : 88%\nCanal : 149\nTipo de rádio : 802.11ac\nTaxa de recepção (Mbps) : 433,3",
        "Name : Wi-Fi\nState : connected\nSSID : PRIVATE\nBSSID : aa:bb\n"
        "Signal : 88%\nChannel : 149\nRadio type : 802.11ac\nReceive rate (Mbps) : 433.3",
    ):
        result = parse_interfaces(text)
        assert result["signal_percent"] == 88
        assert result["channel"] == 149
        assert result["rx_mbps"] == 433.3
        assert "PRIVATE" not in str(result) and "aa:bb" not in str(result)
        assert "ssid" not in str(result).lower()
    assert parse_interfaces("State : disconnected")["link_state"] == "DISCONNECTED"
    assert parse_interfaces("permission required")["link_state"] == "UNAVAILABLE"
    assert parse_interfaces("State : connected\nSignal : 101%")["signal_percent"] is None


def test_metrics_distinguish_packet_loss_unknown_and_actual_disconnects():
    now = datetime.now(UTC)
    collector = str(uuid4())
    rows = [
        NetworkSample.model_validate(
            sample(collector_id=collector, timestamp=now - timedelta(seconds=30))
        ),
        NetworkSample.model_validate(
            sample(
                collector_id=collector,
                timestamp=now - timedelta(seconds=15),
                link_state="DISCONNECTED",
                signal_percent=None,
                channel=None,
                radio_type=None,
                rx_mbps=None,
                tx_mbps=None,
                probe_sent=0,
                probe_rtt_ms=[],
                probe_status="NOT_RUN",
            )
        ),
    ]
    summary = summarize(rows, now)
    assert summary.disconnect_events == 1
    assert summary.gateway_loss_percent == 100 / 3
    assert summary.connected_percent == 50
    assert summary.collector_stale is False
    empty = summarize([], now)
    assert empty.connected_percent is None and empty.signal_mean_percent is None
    assert empty.gateway_loss_percent is None and empty.collector_stale


def test_api_keeps_measured_network_data_separate_and_idempotent(client):
    payload = sample()
    response = client.post("/api/v1/network/samples", json=payload)
    assert response.status_code == 200
    assert response.json()["inserted"] is True
    assert client.post("/api/v1/network/samples", json=payload).json()["inserted"] is False
    report = client.get("/api/v1/network/report").json()
    assert report["summary"]["samples"] == 1
    assert report["items"][0]["data_class"] == "HOST_NETWORK_TELEMETRY"
    assert report["items"][0]["evidence_level"] == "L2_LIVE_UNVALIDATED"
    assert client.get("/api/v1/events").json()["total"] == 0
    assert "SSID" not in client.get("/api/v1/network/export.csv").text
    assert (
        client.post("/api/v1/network/samples", json=sample(signal_percent=101)).status_code == 422
    )
    assert (
        client.post(
            "/api/v1/network/samples",
            json=sample(timestamp=(datetime.now(UTC) - timedelta(days=2)).isoformat()),
        ).status_code
        == 422
    )
    client.headers.clear()
    assert client.get("/api/v1/network/report").status_code == 401
    assert client.post("/api/v1/network/samples", json=sample()).status_code == 401


def test_location_configuration_and_filters(client):
    assert client.get("/api/v1/network/config").json()["location"] == "Computador"
    assert client.post("/api/v1/network/config", json={"location": "Sala"}).status_code == 200
    assert client.get("/api/v1/network/config").json()["location"] == "Sala"
    assert client.post("/api/v1/network/config", json={"location": "=formula"}).status_code == 422
    client.post("/api/v1/network/samples", json=sample(location="Sala"))
    client.post("/api/v1/network/samples", json=sample(location="Quarto"))
    report = client.get("/api/v1/network/report?location=Sala").json()
    assert report["total"] == 1 and report["items"][0]["location"] == "Sala"
    assert client.get("/api/v1/network/report?hours=25").status_code == 422


def test_capacity_and_duplicate_conflicts_preserve_existing_measurements(client):
    from app.storage import Store

    store = client.app.state.store
    assert isinstance(store, Store)
    repository = NetworkStore(store.engine, capacity=1)
    first = NetworkSample.model_validate(sample())
    assert repository.save(first)
    assert repository.save(first) is False
    import pytest

    with pytest.raises(ValueError, match="another payload"):
        repository.save(first.model_copy(update={"signal_percent": 20}))
    with pytest.raises(ValueError, match="capacity"):
        repository.save(NetworkSample.model_validate(sample()))
    rows = repository.read(datetime.now(UTC) - timedelta(hours=1), datetime.now(UTC))
    assert len(rows) == 1 and rows[0].signal_percent == first.signal_percent


def test_gap_or_collector_change_does_not_fabricate_a_disconnect():
    now = datetime.now(UTC)
    before = NetworkSample.model_validate(sample(timestamp=now - timedelta(minutes=5)))
    after = NetworkSample.model_validate(
        sample(
            collector_id=before.collector_id,
            timestamp=now,
            link_state="DISCONNECTED",
            signal_percent=None,
            channel=None,
            radio_type=None,
            rx_mbps=None,
            tx_mbps=None,
            probe_sent=0,
            probe_rtt_ms=[],
            probe_status="NOT_RUN",
        )
    )
    result = summarize([before, after], now)
    assert result.disconnect_events == 0 and result.missing_seconds == 300
    assert summarize([before], now).collector_stale
    changed = after.model_copy(update={"collector_id": uuid4()})
    assert summarize([before, changed], now).disconnect_events == 0


def test_only_one_current_adapter_is_used_and_gateway_is_never_public():
    assert (
        parse_interfaces(
            "Name : A\nState : connected\nSignal : 88%\nName : B\nState : connected\nSignal : 50%"
        )["collector_error"]
        == "multiple_adapters"
    )
    assert (
        parse_interfaces(
            "Name : A\nState : disconnected\nName : B\nState : connected\nSignal : 80%"
        )["signal_percent"]
        == 80
    )
    for address in (
        "8.8.8.8",
        "127.0.0.1",
        "::1",
        "0.0.0.0",
        "192.168.0.1;whoami",
        "255.255.255.255",
    ):
        assert not private_gateway(address)
    assert private_gateway("192.168.3.1")
