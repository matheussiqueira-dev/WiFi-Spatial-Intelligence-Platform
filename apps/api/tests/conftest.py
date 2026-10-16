import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app

TOKEN = "test-only-" + "x" * 40
ORIGIN = "http://127.0.0.1:3000"


@pytest.fixture
def settings(tmp_path):
    return Settings(token=TOKEN, database_url=f"sqlite:///{tmp_path / 'test.db'}", _env_file=None)


@pytest.fixture
def client(settings):
    with TestClient(create_app(settings)) as client:
        client.headers.update({"Authorization": f"Bearer {TOKEN}"})
        yield client
