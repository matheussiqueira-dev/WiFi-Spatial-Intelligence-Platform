from app.ports.history import HistorySelection
from app.storage import Store


class SqliteHistoryRepository:
    def __init__(self, store: Store):
        self.store = store

    def read(self, selection: HistorySelection) -> list[dict]:
        return self.store.observations(
            selection.start,
            selection.end,
            selection.source_id,
            selection.scenario,
            selection.segment_id,
        )

    def read_page(self, selection: HistorySelection, offset: int, limit: int):
        return self.store.observation_page(
            selection.start,
            selection.end,
            offset,
            limit,
            selection.source_id,
            selection.scenario,
            selection.segment_id,
        )
