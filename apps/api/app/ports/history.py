from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True)
class HistorySelection:
    start: datetime
    end: datetime
    source_id: str | None = None
    scenario: str | None = None
    segment_id: str | None = None


class HistoryRepository(Protocol):
    def read(self, selection: HistorySelection) -> list[dict]: ...
