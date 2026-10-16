"""Shared SQLite engine: WAL, busy timeout and the exact UTC microsecond UDF (ADR-003)."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker


def epoch_microseconds(timestamp: str) -> int:
    delta = datetime.fromisoformat(timestamp) - datetime(1970, 1, 1, tzinfo=UTC)
    return delta // timedelta(microseconds=1)


class Database:
    def __init__(self, url: str):
        self.engine = create_engine(url, connect_args={"check_same_thread": False, "timeout": 15})

        @event.listens_for(self.engine, "connect")
        def configure_sqlite(connection, _):
            connection.create_function(
                "spatial_epoch_us", 1, epoch_microseconds, deterministic=True
            )
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute("PRAGMA busy_timeout=15000")

        self.session = sessionmaker(self.engine)
