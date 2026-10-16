"""Opt-in, process-lifetime backup. Never prunes or expunges application data."""

import asyncio
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from app.maintenance import backup


class RecurringBackup:
    def __init__(self, source: Path, destination: Path, root: Path, interval: float):
        self.source = source.resolve()
        self.destination = destination.resolve()
        if (
            not self.destination.is_relative_to(root.resolve())
            or self.destination == root.resolve()
        ):
            raise ValueError("backup destination must be inside workspace")
        if interval <= 0:
            raise ValueError("positive backup interval required")
        self.interval = interval
        self.stop = asyncio.Event()
        self.running = False
        self.successes = 0
        self.last_success: str | None = None
        self.last_error: str | None = None

    def status(self):
        return {
            "enabled": True,
            "running": self.running,
            "successes": self.successes,
            "last_success": self.last_success,
            "last_error": self.last_error,
        }

    def cycle(self):
        lock = self.destination / ".recurring.lock"
        acquired = False
        try:
            self.destination.mkdir(parents=True, exist_ok=True)
            # Exclusive across instances sharing a destination; do not steal stale locks.
            with lock.open("x", encoding="ascii") as handle:
                acquired = True
                handle.write("recurring-backup")
            backup(self.source, self.destination)
            self.successes += 1
            self.last_success = datetime.now(UTC).isoformat()
            self.last_error = None
            return True
        except FileExistsError:
            self.last_error = "backup_busy"
        except (OSError, ValueError, sqlite3.Error):
            # sqlite driver exceptions are deliberately not exposed to status/logs.
            self.last_error = "backup_failed"
        finally:
            if acquired:
                lock.unlink(missing_ok=True)
        return False

    async def run(self):
        self.running = True
        try:
            while not self.stop.is_set():
                await asyncio.to_thread(self.cycle)
                try:
                    await asyncio.wait_for(self.stop.wait(), self.interval)
                except TimeoutError:
                    continue
        finally:
            self.running = False
