import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.config import Settings
from app.main import create_app
from tests.conftest import TOKEN


def test_interactive_docs_are_opt_in(settings):
    with TestClient(create_app(settings)) as client:
        assert client.get("/docs").status_code == 404
        assert client.get("/redoc").status_code == 404
        assert client.get("/openapi.json").status_code == 200
    enabled = settings.model_copy(update={"api_docs_enabled": True})
    with TestClient(create_app(enabled)) as client:
        assert client.get("/docs").status_code == 200


def test_host_header_allowlist_comes_from_settings(settings):
    with TestClient(create_app(settings)) as client:
        assert client.get("/api/v1/health").status_code == 200
        forged = client.get("/api/v1/health", headers={"Host": "attacker.example"})
        assert forged.status_code == 400
    assert "testserver" not in Settings(token=TOKEN, _env_file=None).allowed_hosts


@pytest.mark.parametrize(
    "field,url",
    [("ruview_http_url", "http://ruview:3000"), ("ruview_ws_url", "ws://ruview:3001/ws/sensing")],
)
def test_ruview_service_name_requires_the_container_network(field, url):
    with pytest.raises(ValidationError):
        Settings(token=TOKEN, _env_file=None, **{field: url})
    configured = Settings(token=TOKEN, _env_file=None, container_network=True, **{field: url})
    assert getattr(configured, field).startswith(url.split("/ws")[0])
