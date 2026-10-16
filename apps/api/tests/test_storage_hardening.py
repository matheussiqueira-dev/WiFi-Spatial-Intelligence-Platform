import os
import sqlite3
import time
from contextlib import closing
from datetime import timedelta
from pathlib import Path

import alembic.op
import pytest
import sqlalchemy
from alembic import command
from alembic.config import Config

from app import analytics, maintenance
from tests.test_analytics import START, observation

API = Path(__file__).resolve().parents[1]


def migration_config(database: Path) -> Config:
    config = Config(str(API / "alembic.ini"))
    config.set_main_option("script_location", str(API / "migrations"))
    config.set_main_option("sqlalchemy.url", f"sqlite:///{database}")
    return config


def columns(database: Path, table: str) -> set[str]:
    with closing(sqlite3.connect(database)) as connection:
        return {row[1] for row in connection.execute(f"PRAGMA table_info({table})")}


def version(database: Path) -> str:
    with closing(sqlite3.connect(database)) as connection:
        return connection.execute("SELECT version_num FROM alembic_version").fetchone()[0]


def test_interrupted_migration_rolls_back_and_can_be_retried(tmp_path, monkeypatch):
    database = tmp_path / "spatial.db"
    config = migration_config(database)
    command.upgrade(config, "0001")
    original = alembic.op.create_table

    def interrupted(name, *args, **kwargs):
        if name == "analytics_reports":
            raise RuntimeError("injected failure between migration steps")
        return original(name, *args, **kwargs)

    monkeypatch.setattr(alembic.op, "create_table", interrupted)
    with pytest.raises(RuntimeError):
        command.upgrade(config, "head")
    assert version(database) == "0001"
    assert "segment_id" not in columns(database, "sensing_events")
    monkeypatch.setattr(alembic.op, "create_table", original)
    command.upgrade(config, "head")
    assert "segment_id" in columns(database, "sensing_events")
    os.replace(database, tmp_path / "moved.db")  # Windows refuses if a handle stayed open.


def test_failed_backup_leaves_no_orphan_snapshot(tmp_path, monkeypatch):
    source = tmp_path / "source.db"
    with closing(sqlite3.connect(source)) as connection:
        connection.execute("CREATE TABLE t (x INTEGER)")
        connection.commit()
    directory = tmp_path / "backups"
    verify = maintenance.integrity

    def failing_integrity(path):
        if path != source:
            raise ValueError("SQLite integrity check failed")
        verify(path)

    monkeypatch.setattr(maintenance, "integrity", failing_integrity)
    with pytest.raises(ValueError):
        maintenance.backup(source, directory)
    assert list(directory.iterdir()) == []


def test_prune_refuses_unmanifested_snapshot_with_stable_error(tmp_path):
    directory = tmp_path / "backups"
    directory.mkdir()
    old = time.time() - 40 * 86400
    for index in range(8):
        orphan = directory / f"snapshot-2026010{index}T000000-orphan{index}.db"
        orphan.write_bytes(b"")
        os.utime(orphan, (old, old))
    with pytest.raises(ValueError, match="refusing deletion"):
        maintenance.prune_snapshots(directory)


def capture_sql(engine):
    statements = []

    def record(conn, cursor, statement, parameters, context, executemany):
        statements.append((statement, parameters))

    sqlalchemy.event.listen(engine, "before_cursor_execute", record)
    return statements, lambda: sqlalchemy.event.remove(engine, "before_cursor_execute", record)


def test_history_window_query_uses_the_timestamp_index(client):
    store = client.app.state.store
    for tick in range(5):
        store.write(observation(tick, 1))
    statements, stop = capture_sql(store.engine)
    try:
        rows = store.observations(START, START + timedelta(seconds=3))
    finally:
        stop()
    assert len(rows) == 3
    statement, parameters = next(s for s in statements if "spatial_epoch_us" in s[0])
    with store.engine.connect() as connection:
        plan = connection.exec_driver_sql("EXPLAIN QUERY PLAN " + statement, parameters).all()
    assert any("ix_sensing_events_timestamp" in str(row) for row in plan), plan
    assert not any(str(row[-1]).startswith("SCAN sensing_events") for row in plan), plan


def test_retention_purge_avoids_offset_scans_and_tolerates_id_gaps(client):
    store = client.app.state.store
    store.retention = 3
    for tick in range(5):
        store.write(observation(tick, 1))
    with store.engine.begin() as connection:
        connection.exec_driver_sql(
            "DELETE FROM sensing_events WHERE id = (SELECT max(id) - 1 FROM sensing_events)"
        )
    statements, stop = capture_sql(store.engine)
    try:
        store.write(observation(5, 1))
        store.write(observation(6, 1))
    finally:
        stop()
    # SQLAlchemy renders LIMIT with "OFFSET ?"; only a non-zero offset walks the index.
    offsets = [params[-1] for statement, params in statements if "OFFSET ?" in statement]
    assert all(offset == 0 for offset in offsets), offsets
    ticks = [item["provenance"]["tick"] for item in store.history(10, 0)["items"]]
    assert ticks == [6, 5, 4]


def test_replay_validates_only_the_requested_page(monkeypatch):
    calls = []
    original = analytics.adapter.validate_python

    def counting(value, *args, **kwargs):
        calls.append(value)
        return original(value, *args, **kwargs)

    monkeypatch.setattr(analytics.adapter, "validate_python", counting)
    data = [
        {"event": observation(tick, 1).model_dump(mode="json"), "segment_id": None}
        for tick in reversed(range(60))
    ]
    data.append(dict(data[0]))  # duplicate UUID must still be counted once
    query = analytics.AnalyticsQuery(
        start=START, end=START + timedelta(minutes=2), limit=10, offset=20
    )
    result = analytics.replay(data, query)
    assert result["total"] == 60
    assert [item["event"]["provenance"]["tick"] for item in result["items"]] == list(range(20, 30))
    assert len(calls) <= 10


def test_retention_never_purges_non_synthetic_evidence(client):
    store = client.app.state.store
    store.retention = 3
    store.write(observation(0, 1))
    with store.engine.begin() as connection:
        connection.exec_driver_sql(
            "UPDATE sensing_events SET evidence_level = 'L1_RECORDED_UNVALIDATED'"
        )
    for tick in range(1, 8):
        store.write(observation(tick, 1))
    with store.engine.connect() as connection:
        levels = [
            row[0]
            for row in connection.exec_driver_sql("SELECT evidence_level FROM sensing_events")
        ]
    assert levels.count("L1_RECORDED_UNVALIDATED") == 1


def test_saved_report_and_run_share_the_audit_transaction(client):
    store = client.app.state.store

    def refuse_audit(conn, cursor, statement, parameters, context, executemany):
        if statement.startswith("INSERT INTO audit_events"):
            raise RuntimeError("audit storage unavailable")

    sqlalchemy.event.listen(store.engine, "before_cursor_execute", refuse_audit)
    try:
        with pytest.raises(RuntimeError):
            store.save_report({"evidence_level": "L0_SYNTHETIC"})
    finally:
        sqlalchemy.event.remove(store.engine, "before_cursor_execute", refuse_audit)
    assert store.reports(10, 0)["total"] == 0


def test_corrupt_stored_payload_is_excluded_and_reported(client):
    store = client.app.state.store
    for tick in range(3):
        store.write(observation(tick, 1))
    with store.engine.begin() as connection:
        connection.exec_driver_sql(
            "UPDATE sensing_events SET payload = json_set(payload, '$.evidence_level', 'L3')"
            " WHERE id = (SELECT min(id) FROM sensing_events)"
        )
    params = {"start": START.isoformat(), "end": (START + timedelta(minutes=1)).isoformat()}
    report = client.get("/api/v1/analytics", params=params)
    assert report.status_code == 200
    assert report.json()["summary"]["samples"] == 2
    assert any("1 stored record" in item for item in report.json()["limitations"])
    replay = client.get("/api/v1/analytics/replay", params=params)
    assert replay.status_code == 200
    assert replay.json()["total"] == 3


def test_replay_route_reads_only_the_requested_page(client, monkeypatch):
    store = client.app.state.store
    for tick in range(40):
        store.write(observation(tick, 1))
    import json

    calls = []
    original = json.loads

    def counting(value, *args, **kwargs):
        calls.append(1)
        return original(value, *args, **kwargs)

    monkeypatch.setattr(json, "loads", counting)
    params = {
        "start": START.isoformat(),
        "end": (START + timedelta(minutes=2)).isoformat(),
        "limit": 5,
        "offset": 10,
    }
    page = client.get("/api/v1/analytics/replay", params=params).json()
    assert page["total"] == 40
    assert [item["event"]["provenance"]["tick"] for item in page["items"]] == list(range(10, 15))
    # json is patched globally (the client decodes the response too); 40 would mean a full scan.
    assert len(calls) < 10


def test_migrations_at_head_match_the_orm_models(tmp_path):
    from alembic.autogenerate import compare_metadata
    from alembic.migration import MigrationContext

    import app.adapters.network_store  # noqa: F401  (registers network tables on Base)
    from app.storage import Base

    database = tmp_path / "drift.db"
    command.upgrade(migration_config(database), "head")
    engine = sqlalchemy.create_engine(f"sqlite:///{database}")
    try:
        with engine.connect() as connection:
            context = MigrationContext.configure(connection)
            differences = compare_metadata(context, Base.metadata)
    finally:
        engine.dispose()
    assert differences == [], differences
