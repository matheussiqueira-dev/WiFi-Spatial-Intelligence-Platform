import os

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app

TOKEN = "test-only-" + "x" * 40
ORIGIN = "http://127.0.0.1:3000"


@pytest.fixture(autouse=True)
def isolated_environment(monkeypatch):
    # A shell with SPATIAL_LEGACY_LAB_ENABLED=true (or E2E_*) must not change results.
    for name in list(os.environ):
        if name.startswith(("SPATIAL_", "E2E_")) or name == "FORWARDED_ALLOW_IPS":
            monkeypatch.delenv(name, raising=False)


@pytest.fixture
def settings(tmp_path):
    return Settings(
        token=TOKEN,
        database_url=f"sqlite:///{tmp_path / 'test.db'}",
        allowed_hosts=["127.0.0.1", "localhost", "testserver"],
        _env_file=None,
    )


@pytest.fixture
def client(settings):
    with TestClient(create_app(settings)) as client:
        client.headers.update({"Authorization": f"Bearer {TOKEN}"})
        yield client
