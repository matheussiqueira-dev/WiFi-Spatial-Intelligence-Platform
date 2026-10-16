from fastapi.testclient import TestClient

from app.main import create_app


def test_unexpected_http_error_is_sanitized_and_does_not_poison_app(settings):
    app = create_app(settings)

    @app.get("/test-failure")
    def failure():
        raise RuntimeError("private-token-and-database-path")

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/test-failure")
        assert response.status_code == 500
        assert response.json() == {"detail": "internal service error"}
        assert response.headers["cache-control"] == "no-store"
        assert "private" not in response.text
        assert client.get("/api/v1/health").status_code == 200
