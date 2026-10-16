import csv
import io
from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from app.analytics import AnalyticsQuery, aggregate, ordered
from app.contracts import RuViewEvent, RuViewMeasurements, RuViewProvenance
from app.main import create_app
from app.maintenance import backup, digest, prune_snapshots, restore, retain

START = datetime(2026, 1, 1, tzinfo=UTC)
SEGMENT = "00000000-0000-4000-8000-000000000001"


def observation(tick, count, seconds=None):
    return RuViewEvent(
        event_id=UUID(int=tick + 1),
        timestamp=START + timedelta(seconds=tick if seconds is None else seconds),
        measurements=RuViewMeasurements(presence_detected=count != 0, occupancy_estimate=count),
        provenance=RuViewProvenance(tick=tick),
        processing_latency_ms=float(tick),
    )


def query(**changes):
    return AnalyticsQuery(start=START, end=START + timedelta(minutes=2), **changes)


def rows():
    return [
        {"event": observation(tick, count, seconds).model_dump(mode="json"), "segment_id": SEGMENT}
        for tick, count, seconds in [(0, 0, 0), (1, 2, 1), (2, None, 2), (3, 1, 3), (4, 0, 20)]
    ]


def test_aggregates_unknown_gaps_and_estimates_are_deterministic():
    result = aggregate(rows(), query())
    assert result == aggregate(list(reversed(rows())) + [rows()[0]], query())
    bucket = result["buckets"]["items"][0]
    assert bucket["occupancy_mean"] == 0.75
    assert bucket["presence_fraction"] == 0.6
    assert bucket["unknown_count_samples"] == 1
    assert result["summary"]["entries_estimate"] == 2
    assert result["summary"]["exits_estimate"] == 0
    assert result["summary"]["unknown_seconds"] == 17
    assert result["summary"]["queue_wait_p95_ms"] == 3
    assert result["summary"]["rf_drop_rate"] is None
    assert all(x["evidence_level"] == "L0_SYNTHETIC" for x in result["transitions"]["items"])


def test_no_transitions_across_segments_ticks_or_legacy():
    data = rows()[:2]
    data[1]["segment_id"] = None
    assert aggregate(data, query())["summary"]["entries_estimate"] == 0
    data[1]["segment_id"] = SEGMENT
    data[1]["event"]["provenance"]["tick"] = 0
    assert aggregate(data, query())["intervals"]["items"][0]["state"] == "unknown"


@pytest.mark.parametrize(
    "bucket,expected", [("minute", 2), ("five_minutes", 2), ("hour", 1), ("day", 1)]
)
def test_utc_window_boundaries(bucket, expected):
    data = [
        {"event": observation(tick, count, seconds).model_dump(mode="json"), "segment_id": SEGMENT}
        for tick, count, seconds in [(0, 0, 299), (1, 2, 300)]
    ]
    selection = AnalyticsQuery(start=START, end=START + timedelta(minutes=10), bucket=bucket)
    report = aggregate(data, selection)
    assert report["buckets"]["total"] == expected
    assert report["summary"]["entries_estimate"] == 2
    assert sum(item["samples"] for item in report["buckets"]["items"]) == 2


def test_utc_order_and_buckets_do_not_follow_daylight_saving_clock_jump():
    timestamps = [
        datetime.fromisoformat(value)
        for value in ("2026-03-08T06:59:59+00:00", "2026-03-08T07:00:00+00:00")
    ]
    data = [
        {
            "event": observation(index, index)
            .model_copy(update={"timestamp": timestamp})
            .model_dump(mode="json"),
            "segment_id": SEGMENT,
        }
        for index, timestamp in enumerate(timestamps)
    ]
    selection = AnalyticsQuery(
        start=timestamps[0], end=timestamps[-1] + timedelta(seconds=1), bucket="hour"
    )
    report = aggregate(data, selection)
    assert [item["timestamp"] for item in report["buckets"]["items"]] == [
        "2026-03-08T06:00:00+00:00",
        "2026-03-08T07:00:00+00:00",
    ]
    assert report["summary"]["entries_estimate"] == 1


@pytest.mark.parametrize(
    "changes",
    [
        {"start": "2026-01-01T00:00:00"},
        {"end": "2026-03-01T00:00:00Z"},
        {"start": "2026-01-02T00:00:00Z"},
        {"limit": 201},
        {"offset": -1},
        {"source_id": "real"},
        {"room_id": "other"},
        {"gap_seconds": 0},
        {"end": "2099-01-01T00:00:00Z"},
        {"scenario": "=HYPERLINK(1)"},
    ],
)
def test_invalid_query_is_rejected(client, changes):
    params = {
        "start": START.isoformat(),
        "end": (START + timedelta(minutes=2)).isoformat(),
        **changes,
    }
    assert client.get("/api/v1/analytics", params=params).status_code == 422


def test_submillisecond_filter_is_exact_and_end_exclusive(client):
    store = client.app.state.store
    for tick, microseconds in enumerate((100, 300, 500)):
        store.write(
            observation(tick, 0).model_copy(
                update={"timestamp": START + timedelta(microseconds=microseconds)}
            )
        )
    params = {
        "start": (START + timedelta(microseconds=200)).isoformat(),
        "end": (START + timedelta(microseconds=400)).isoformat(),
    }
    result = client.get("/api/v1/analytics/replay", params=params).json()
    assert result["total"] == 1
    assert result["items"][0]["event"]["provenance"]["tick"] == 1


def test_replay_filters_pages_reports_restart_and_deletion(client, settings):
    store = client.app.state.store
    store.segment_id = SEGMENT
    for row in reversed(rows()):
        store.write(RuViewEvent.model_validate(row["event"]))
    assert store.write(observation(0, 0)) is False
    params = query(limit=2).model_dump(mode="json", exclude_none=True)
    response = client.get("/api/v1/analytics", params=params)
    assert response.status_code == 200, response.text
    report = response.json()
    assert report["summary"]["samples"] == 5
    assert (
        client.get("/api/v1/analytics", params={**params, "source_id": "simulator-01"}).json()[
            "summary"
        ]["samples"]
        == 0
    )
    first = client.get("/api/v1/analytics/replay", params=params).json()
    second = client.get("/api/v1/analytics/replay", params={**params, "offset": 2}).json()
    assert [x["event"]["provenance"]["tick"] for x in first["items"] + second["items"]] == [
        0,
        1,
        2,
        3,
    ]
    assert first["mode"] == "REPLAY" and first["total"] == 5
    exported = client.get("/api/v1/analytics/export.csv", params=params)
    parsed = list(csv.DictReader(io.StringIO(exported.text)))
    assert parsed[0]["evidence_level"] == "L0_SYNTHETIC"
    identifier = client.post("/api/v1/analytics/reports", json=params).json()["id"]
    with TestClient(create_app(settings)) as restarted:
        restarted.headers.update(client.headers)
        assert restarted.get(f"/api/v1/analytics/reports/{identifier}").json() == report
        assert restarted.get("/api/v1/analytics/reports").json()["total"] == 1
        assert restarted.get("/api/v1/analytics/replay", params=params).json() == first
    assert (
        client.get("/api/v1/analytics", params=params, headers={"Authorization": ""}).status_code
        == 401
    )
    assert (
        client.post(
            "/api/v1/analytics/reports", json=params, headers={"Authorization": ""}
        ).status_code
        == 401
    )
    client.delete("/api/v1/events/synthetic")
    assert client.get("/api/v1/analytics/reports").json()["total"] == 0


def test_equal_timestamps_use_event_id_tie_break_and_invalid_evidence():
    data = [
        {"event": observation(tick, 0, 0).model_dump(mode="json"), "segment_id": SEGMENT}
        for tick in [2, 1, 0]
    ]
    assert [event.provenance.tick for event, _ in ordered(data)] == [0, 1, 2]
    data[0]["event"]["evidence_level"] = "L3_VALIDATED"
    with pytest.raises(ValueError):
        aggregate(data, query())


def test_sqlite_backup_restore_integrity_and_guarded_retention(client, settings, tmp_path):
    import sqlite3

    store = client.app.state.store
    store.write(observation(0, 0))
    source = tmp_path / "test.db"
    snapshot = backup(source, tmp_path / "snapshots")
    target = tmp_path / "restored.db"
    restore(snapshot, target)
    with sqlite3.connect(target) as restored:
        assert (
            restored.execute("SELECT payload FROM sensing_events").fetchone()[0]
            == observation(0, 0).model_dump_json()
        )
    with pytest.raises(FileExistsError):
        restore(snapshot, target)
    with sqlite3.connect(source) as connection:
        connection.executemany(
            "INSERT INTO audit_events(timestamp,action) VALUES(?,?)",
            [
                ("2020-01-01T00:00:00+00:00", "simulation.start"),
                ("2020-01-01T00:00:00+00:00", "security.denied"),
            ],
        )
    with pytest.raises(ValueError):
        retain(source, tmp_path / "snapshots", days=1)
    source.with_suffix(".hold").touch()
    with pytest.raises(ValueError):
        retain(source, tmp_path / "snapshots")
    source.with_suffix(".hold").unlink()
    result = retain(source, tmp_path / "snapshots")
    assert result["archived"] == 1
    assert any(x["action"] == "security.denied" for x in store.audits())
    assert any(x["action"] == "audit.retention.archived" for x in store.audits())
    assert len(digest(snapshot)) == 64
    snapshot.write_bytes(b"tampered")
    with pytest.raises(ValueError):
        restore(snapshot, tmp_path / "tampered.db")


def test_snapshot_retention_and_rotating_logs(client, tmp_path):
    import logging
    import os

    directory = tmp_path / "backups"
    for _ in range(8):
        snapshot = backup(tmp_path / "test.db", directory)
        os.utime(snapshot, (1, 1))
    with pytest.raises(ValueError):
        prune_snapshots(directory, keep=1)
    assert prune_snapshots(directory) == 1
    assert len(list(directory.glob("snapshot-*.db"))) == 7
    handler = logging.getLogger("spatial").handlers[0]
    handler.maxBytes = 100
    for _ in range(20):
        logging.getLogger("spatial.test").warning("synthetic diagnostic")
    logs = list((tmp_path / "logs").glob("application.log*"))
    assert 1 < len(logs) <= 6


def test_legacy_migration_preserves_payload_and_does_not_invent_sessions(settings, tmp_path):
    import sqlite3
    from contextlib import closing

    source = tmp_path / "legacy.db"
    event = observation(0, 0)
    with closing(sqlite3.connect(source)) as connection:
        connection.executescript("""
            CREATE TABLE alembic_version (version_num VARCHAR(32) PRIMARY KEY);
            INSERT INTO alembic_version VALUES ('0001');
            CREATE TABLE sensing_events (id INTEGER PRIMARY KEY,
                event_id VARCHAR(36) UNIQUE NOT NULL, timestamp VARCHAR(40) NOT NULL,
                evidence_level VARCHAR(32) NOT NULL, payload TEXT NOT NULL);
            CREATE TABLE audit_events (id INTEGER PRIMARY KEY, timestamp VARCHAR(40) NOT NULL,
                action VARCHAR(64) NOT NULL);
        """)
        connection.execute(
            "INSERT INTO sensing_events VALUES(1,?,?,?,?)",
            (
                str(event.event_id),
                event.timestamp.isoformat(),
                event.evidence_level,
                event.model_dump_json(),
            ),
        )
        connection.commit()
    config = settings.model_copy(update={"database_url": f"sqlite:///{source}"})
    with TestClient(create_app(config)) as client:
        client.headers.update({"Authorization": f"Bearer {settings.token}"})
        assert client.get("/api/v1/events").json()["items"] == [event.model_dump(mode="json")]
        result = client.get(
            "/api/v1/analytics/replay", params=query().model_dump(mode="json", exclude_none=True)
        ).json()
        assert result["items"][0]["segment_id"] is None
