from app.ports.history import HistoryRepository, HistorySelection


class ReadHistory:
    def __init__(self, repository: HistoryRepository):
        self.repository = repository

    def execute(self, selection: HistorySelection) -> list[dict]:
        return self.repository.read(selection)

    def page(self, selection: HistorySelection, offset: int, limit: int):
        return self.repository.read_page(selection, offset, limit)
