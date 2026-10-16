from app.ports.history import HistoryRepository, HistorySelection


class ReadHistory:
    def __init__(self, repository: HistoryRepository):
        self.repository = repository

    def execute(self, selection: HistorySelection) -> list[dict]:
        return self.repository.read(selection)
