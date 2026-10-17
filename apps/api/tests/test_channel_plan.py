from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.adapters.windows_wifi import parse_networks
from app.application.channel_plan import aggregate, plan
from app.capabilities import CATALOG, catalog, is_enabled
from app.network_contracts import ChannelSurvey

PT = """Nome da interface: Wi-Fi
Há 2 redes visíveis no momento.

SSID 1 : VIZINHO-PRIVADO
    Tipo de rede            : Infraestrutura
    Autenticação            : WPA2-Personal
    BSSID 1                 : 11:22:33:44:55:66
         Sinal             : 90%
         Tipo de Rádio         : 802.11be
         Banda               : 5 GHz
         Canal            : 149
         Carga Bss:
             Estações Conectadas:         4
             Utilização do canal:        39 (15 %)
    BSSID 2                 : 11:22:33:44:55:67
         Sinal             : 40%
         Banda               : 2,4 GHz
         Canal            : 6

SSID 2 : OUTRO
    BSSID 1                 : aa:bb:cc:dd:ee:ff
         Sinal             : 70%
         Canal            : 149
"""
EN = """Interface name : Wi-Fi
There are 1 networks currently visible.

SSID 1 : SECRET
    BSSID 1                 : 66:55:44:33:22:11
         Signal             : 55%
         Radio type         : 802.11ax
         Band               : 6 GHz
         Channel            : 37
         Channel Utilization:        20 (8 %)
"""


def survey(channels, minutes_ago=0, **changes):
    return ChannelSurvey.model_validate(
        {
            "survey_id": str(uuid4()),
            "collector_id": str(uuid4()),
            "timestamp": (datetime.now(UTC) - timedelta(minutes=minutes_ago)).isoformat(),
            "location": "Escritorio",
            "channels": channels,
        }
        | changes
    )


def channel(band, number, count=1, signal=80, utilization=None):
    return {
        "band": band,
        "channel": number,
        "ap_count": count,
        "strongest_signal_percent": signal,
        "utilization_percent": utilization,
    }


def test_parser_reads_pt_en_and_drops_every_identifier():
    readings = parse_networks(PT)
    assert readings == [
        {"band": "5GHz", "channel": 149, "signal_percent": 90, "utilization_percent": 15},
        {"band": "2.4GHz", "channel": 6, "signal_percent": 40, "utilization_percent": None},
        {"band": "5GHz", "channel": 149, "signal_percent": 70, "utilization_percent": None},
    ]
    assert parse_networks(EN) == [
        {"band": "6GHz", "channel": 37, "signal_percent": 55, "utilization_percent": 8}
    ]
    for text in (PT, EN):
        exported = str(aggregate(parse_networks(text)))
        for secret in ("VIZINHO", "OUTRO", "SECRET", "11:22", "aa:bb", "66:55", "WPA2"):
            assert secret not in exported
    assert parse_networks("permission denied") is None


def test_aggregate_collapses_access_points_per_channel():
    rows = aggregate(parse_networks(PT))
    assert [(row.band, row.channel, row.ap_count) for row in rows] == [
        ("2.4GHz", 6, 1),
        ("5GHz", 149, 2),
    ]
    assert rows[1].strongest_signal_percent == 90
    assert rows[1].utilization_percent == 15


def test_contract_rejects_duplicates_errors_with_data_and_local_time():
    with pytest.raises(ValidationError):
        survey([channel("5GHz", 36), channel("5GHz", 36)])
    with pytest.raises(ValidationError):
        survey([channel("5GHz", 36)], collector_error="read_failed")
    with pytest.raises(ValidationError):
        survey([], timestamp="2026-10-15T10:00:00-03:00")
    with pytest.raises(ValidationError):
        survey([channel("5GHz", 36) | {"ssid": "x"}])


def test_24ghz_overlap_recommends_clean_non_overlapping_channel():
    now = datetime.now(UTC)
    rows = [survey([channel("2.4GHz", 1, 3, 90), channel("2.4GHz", 4, 1, 60)])]
    result = plan(rows, 1, now - timedelta(hours=1), now, None)
    band = result.bands[0]
    assert band.band == "2.4GHz"
    assert band.recommended_channel == 11
    assert band.advice == "CONSIDER_CHANGE"
    scores = {row.channel: row.interference_score for row in band.candidates}
    assert scores[11] == 0
    assert scores[1] > scores[6] > scores[11]


def test_own_access_point_is_discounted_and_small_differences_keep_channel():
    now = datetime.now(UTC)
    # Only our router on 149, one weak neighbour on 36: no reason to move.
    rows = [survey([channel("5GHz", 149, 1, 90), channel("5GHz", 36, 1, 20)])]
    band = plan(rows, 149, now - timedelta(hours=1), now, None).bands[0]
    assert band.current_score == 0
    assert band.advice == "KEEP"
    assert band.recommended_channel == 149


def test_busy_current_channel_and_80mhz_block_sharing():
    now = datetime.now(UTC)
    rows = [survey([channel("5GHz", 149, 4, 90, 60)])]
    band = plan(rows, 149, now - timedelta(hours=1), now, None).bands[0]
    scores = {row.channel: row.interference_score for row in band.candidates}
    assert scores[153] == pytest.approx(scores[149] / 2)
    assert scores[36] == 0
    assert band.advice == "CONSIDER_CHANGE"
    assert band.recommended_channel == 36


def test_window_average_counts_absence_and_failures_are_reported():
    now = datetime.now(UTC)
    rows = [
        survey([channel("5GHz", 36, 2, 100)], minutes_ago=3),
        survey([], minutes_ago=2),
        survey([], minutes_ago=1, collector_error="read_failed"),
    ]
    result = plan(rows, None, now - timedelta(hours=1), now, None)
    assert result.surveys == 2
    assert result.failed_surveys == 1
    band = result.bands[0]
    assert band.advice == "NO_CURRENT"
    by_channel = {row.channel: row for row in band.candidates}
    assert by_channel[36].observed_ap_count == 1
    assert by_channel[36].interference_score == 1


def test_6ghz_is_reported_but_not_modelled_and_empty_window_abstains():
    now = datetime.now(UTC)
    rows = [survey([channel("6GHz", 37, 1, 55)])]
    band = plan(rows, None, now - timedelta(hours=1), now, None).bands[0]
    assert band.advice == "NOT_MODELED"
    assert band.recommended_channel is None
    empty = plan([], 149, now - timedelta(hours=1), now, None)
    assert empty.surveys == 0
    assert empty.bands[0].candidates == []
    assert empty.bands[0].recommended_channel is None


def test_channel_plan_api_is_authenticated_idempotent_and_separate(client):
    payload = survey([channel("5GHz", 149, 3, 90, 50)]).model_dump(mode="json")
    response = client.post("/api/v1/network/channel-surveys", json=payload)
    assert response.status_code == 200 and response.json()["inserted"] is True
    assert client.post("/api/v1/network/channel-surveys", json=payload).json()["inserted"] is False
    changed = payload | {"location": "Sala"}
    assert client.post("/api/v1/network/channel-surveys", json=changed).status_code == 409
    stale = survey([], minutes_ago=10).model_dump(mode="json")
    assert client.post("/api/v1/network/channel-surveys", json=stale).status_code == 422
    result = client.get("/api/v1/network/channel-plan").json()
    assert result["surveys"] == 1
    assert result["evidence_level"] == "L2_LIVE_UNVALIDATED"
    assert result["bands"][0]["advice"] == "NO_CURRENT"
    assert client.get("/api/v1/network/channel-plan?location=Outro").json()["surveys"] == 0
    assert client.get("/api/v1/network/channel-plan?hours=25").status_code == 422
    assert client.get("/api/v1/events").json()["total"] == 0
    client.headers.clear()
    assert client.get("/api/v1/network/channel-plan").status_code == 401
    assert client.post("/api/v1/network/channel-surveys", json=payload).status_code == 401


def test_catalog_profiles_never_enable_blocked_or_medical_commercially():
    ids = [item.id for item in CATALOG]
    assert len(ids) == len(set(ids))
    commercial = catalog("commercial-br").capabilities
    for item in commercial:
        if item.enabled:
            assert "ANVISA_SAMD" not in item.regulatory
            assert item.group != "D"
            assert item.status not in {"PLANNED", "BLOCKED"}
    assert is_enabled("network.channel_plan", "commercial-br")
    assert not is_enabled("spatial.presence", "commercial-br")
    assert is_enabled("spatial.presence", "lab")
    assert not is_enabled("identity.rf_reidentification", "lab")
    synthetic = [item for item in CATALOG if item.status == "IMPLEMENTED_SYNTHETIC"]
    assert all(item.evidence_ceiling == "L0_SYNTHETIC" for item in synthetic)


def test_capabilities_endpoint_follows_configured_profile(settings, tmp_path):
    from fastapi.testclient import TestClient

    from app.main import create_app
    from tests.conftest import TOKEN

    commercial = settings.model_copy(
        update={
            "database_url": f"sqlite:///{tmp_path / 'commercial.db'}",
            "capability_profile": "commercial-br",
        }
    )
    for config, profile in ((settings, "lab"), (commercial, "commercial-br")):
        with TestClient(create_app(config)) as client:
            assert client.get("/api/v1/capabilities").status_code == 401
            client.headers.update({"Authorization": f"Bearer {TOKEN}"})
            body = client.get("/api/v1/capabilities").json()
            assert body["profile"] == profile
            assert "parecer" in body["disclaimer"]
            states = {item["id"]: item["enabled"] for item in body["capabilities"]}
            assert states["spatial.presence"] is (profile == "lab")
