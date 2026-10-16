import threading
from datetime import datetime

from sqlalchemy import Engine, String, Text, func, select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import Mapped, mapped_column, sessionmaker

from app.network_contracts import NetworkSample
from app.storage import Base


class NetworkSampleRow(Base):
    __tablename__ = "network_samples"
    sample_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    timestamp: Mapped[str] = mapped_column(String(40), index=True)
    location: Mapped[str] = mapped_column(String(48), index=True)
    payload: Mapped[str] = mapped_column(Text)


class NetworkConfigurationRow(Base):
    __tablename__ = "network_configuration"
    id: Mapped[int] = mapped_column(primary_key=True)
    location: Mapped[str] = mapped_column(String(48))


class NetworkStore:
    def __init__(self, engine: Engine, capacity: int = 100000):
        self.session = sessionmaker(engine)
        self.capacity = capacity
        self.lock = threading.Lock()

    def save(self, sample: NetworkSample) -> bool:
        with self.lock, self.session.begin() as session:
            existing = session.get(NetworkSampleRow, str(sample.sample_id))
            if existing:
                if existing.payload != sample.model_dump_json():
                    raise ValueError("sample ID already belongs to another payload")
                return False
            if session.scalar(select(func.count()).select_from(NetworkSampleRow)) >= self.capacity:
                raise ValueError(
                    "network history capacity reached; export/archive before continuing"
                )
            known = list(session.scalars(select(NetworkSampleRow.location).distinct().limit(21)))
            if sample.location not in known and len(known) >= 20:
                raise ValueError("location capacity reached")
            session.add(
                NetworkSampleRow(
                    sample_id=str(sample.sample_id),
                    timestamp=sample.timestamp.isoformat(timespec="microseconds"),
                    location=sample.location,
                    payload=sample.model_dump_json(),
                )
            )
            return True

    def read(self, start: datetime, end: datetime) -> list[NetworkSample]:
        with self.session() as session:
            rows = session.scalars(
                select(NetworkSampleRow)
                .where(
                    NetworkSampleRow.timestamp >= start.isoformat(timespec="microseconds"),
                    NetworkSampleRow.timestamp <= end.isoformat(timespec="microseconds"),
                )
                .order_by(NetworkSampleRow.timestamp, NetworkSampleRow.sample_id)
                .limit(10001)
            ).all()
            if len(rows) > 10000:
                raise ValueError("query exceeds 10000 samples; shorten the period")
            return [NetworkSample.model_validate_json(row.payload) for row in rows]

    def locations(self) -> list[str]:
        with self.session() as session:
            return list(
                session.scalars(
                    select(NetworkSampleRow.location)
                    .distinct()
                    .order_by(NetworkSampleRow.location)
                    .limit(20)
                )
            )

    def configure(self, location: str) -> None:
        with self.lock, self.session.begin() as session:
            known = list(session.scalars(select(NetworkSampleRow.location).distinct().limit(21)))
            if location not in known and len(known) >= 20:
                raise ValueError("location capacity reached")
            session.execute(
                insert(NetworkConfigurationRow)
                .values(id=1, location=location)
                .on_conflict_do_update(index_elements=["id"], set_={"location": location})
            )

    def configuration(self) -> str:
        with self.session() as session:
            row = session.get(NetworkConfigurationRow, 1)
            return row.location if row else "Computador"
