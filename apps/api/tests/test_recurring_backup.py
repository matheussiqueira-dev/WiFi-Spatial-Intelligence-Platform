import asyncio
import json
import shutil
import sqlite3
import threading
import time
from pathlib import Path
from uuid import uuid4

import pytest

from app.recurring_backup import RecurringBackup


def database(path):
    with sqlite3.connect(path) as db:
        db.execute("CREATE TABLE samples(id INTEGER PRIMARY KEY, payload TEXT)")
        db.execute("INSERT INTO samples(payload) VALUES ('L0_SYNTHETIC')")


def test_recurring_backup_runs_cancels_and_restores(tmp_path):
    from app.maintenance import restore

    source = tmp_path / "source.db"
    database(source)
    worker = RecurringBackup(source, tmp_path / "backups", tmp_path, 0.01)

    async def exercise():
        task = asyncio.create_task(worker.run())
        async with asyncio.timeout(3):
            while worker.status()["successes"] < 2:
                await asyncio.sleep(0.005)
        worker.stop.set()
        await task

    asyncio.run(exercise())
    assert worker.status()["last_success"]
    assert not worker.status()["running"]
    assert not (tmp_path / "backups/.recurring.lock").exists()
    snapshot = next((tmp_path / "backups").glob("snapshot-*.db"))
    restore(snapshot, tmp_path / "restored.db")
    with sqlite3.connect(tmp_path / "restored.db") as db:
        assert db.execute("SELECT payload FROM samples").fetchone() == ("L0_SYNTHETIC",)


def test_exclusion_failure_and_destination_bounds(tmp_path):
    source = tmp_path / "source.db"
    database(source)
    with pytest.raises(ValueError):
        RecurringBackup(source, tmp_path.parent / "outside", tmp_path, 1)
    worker = RecurringBackup(source, tmp_path / "backups", tmp_path, 1)
    worker.destination.mkdir()
    lock = worker.destination / ".recurring.lock"
    lock.write_text("external-owner")
    assert not worker.cycle()
    assert lock.read_text() == "external-owner"
    assert worker.status()["last_error"] == "backup_busy"
    lock.unlink()  # Fixture owned by this test only.
    worker.source = tmp_path / "missing-secret-sentinel.db"
    assert not worker.cycle()
    assert "sentinel" not in json.dumps(worker.status())
    assert worker.status()["last_error"] == "backup_failed"


def test_backup_during_writing_is_consistent(tmp_path):
    source = tmp_path / "source.db"
    database(source)
    done = threading.Event()

    def write():
        with sqlite3.connect(source) as db:
            db.execute("PRAGMA journal_mode=WAL")
            while not done.is_set():
                db.execute("INSERT INTO samples(payload) VALUES ('L0_SYNTHETIC')")
                db.commit()

    thread = threading.Thread(target=write)
    thread.start()
    try:
        worker = RecurringBackup(source, tmp_path / "backups", tmp_path, 1)
        assert worker.cycle()
        snapshot = next(worker.destination.glob("snapshot-*.db"))
        with sqlite3.connect(snapshot) as db:
            assert db.execute("PRAGMA integrity_check").fetchone() == ("ok",)
            assert set(db.execute("SELECT payload FROM samples")) == {("L0_SYNTHETIC",)}
    finally:
        done.set()
        thread.join(timeout=3)
    assert not thread.is_alive()


def test_opt_in_lifespan_reports_actual_success(settings, tmp_path):
    from fastapi.testclient import TestClient

    from app.main import create_app

    destination = tmp_path / "backups"
    config = settings.model_copy(
        update={"backup_enabled": True, "backup_destination": str(destination)}
    )
    # The application boundary deliberately refuses backups outside its workspace.
    with pytest.raises(ValueError):
        create_app(config)
    with TestClient(create_app(settings)) as client:
        client.headers["Authorization"] = f"Bearer {settings.token}"
        assert client.get("/api/v1/governance/status").json()["backup"] == {"enabled": False}
    # The workspace boundary requires a destination inside the repository.
    destination = Path(__file__).parents[3] / "artifacts" / f"backup-test-{uuid4()}"
    config = settings.model_copy(
        update={"backup_enabled": True, "backup_destination": str(destination)}
    )
    try:
        with TestClient(create_app(config)) as client:
            client.headers["Authorization"] = f"Bearer {settings.token}"
            deadline = time.monotonic() + 3
            while time.monotonic() < deadline:
                response = client.get("/api/v1/governance/status")
                assert response.status_code == 200, response.text
                status = response.json()["backup"]
                if status["successes"] >= 1:
                    break
                time.sleep(0.02)
            assert status["last_success"] and status["last_error"] is None
    finally:
        shutil.rmtree(destination, ignore_errors=True)


def test_hold_is_preserved_by_backup(tmp_path):
    source = tmp_path / "source.db"
    database(source)
    hold = source.with_suffix(".hold")
    hold.write_text("preserve")
    worker = RecurringBackup(source, tmp_path / "backups", tmp_path, 1)
    assert worker.cycle()
    assert hold.read_text() == "preserve"
