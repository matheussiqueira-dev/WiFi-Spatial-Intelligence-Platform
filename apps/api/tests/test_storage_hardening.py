import os
import sqlite3
import time
from contextlib import closing
from pathlib import Path

import alembic.op
import pytest
from alembic import command
from alembic.config import Config

from app import maintenance

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
