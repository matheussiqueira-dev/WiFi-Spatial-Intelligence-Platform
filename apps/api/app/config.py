from typing import Literal
from urllib.parse import urlsplit

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SPATIAL_",
        env_file=(".env", ".env.ruview"),
        extra="ignore",
        hide_input_in_errors=True,
    )
    token: str = Field(min_length=32, max_length=512, repr=False)
    database_url: str = "sqlite:///./runtime/spatial.db"
    retention_events: int = Field(default=10000, ge=100, le=100000)
    origins: list[str] = ["http://127.0.0.1:3000", "http://localhost:3000"]
    # Host header allowlist; tests add "testserver" explicitly instead of shipping it.
    allowed_hosts: list[str] = ["127.0.0.1", "localhost", "api"]
    # Swagger/ReDoc pages load third-party CDN scripts; off unless explicitly enabled.
    api_docs_enabled: bool = False
    # Only Compose sets this: the "ruview" service name resolves on its private network.
    container_network: bool = False
    ruview_http_url: str = "http://127.0.0.1:4860"
    ruview_ws_url: str = "ws://127.0.0.1:4861/ws/sensing"
    ruview_token: str = Field(default="", max_length=512, repr=False)
    ruview_stale_seconds: float = Field(default=5, ge=1, le=60)
    legacy_lab_enabled: bool = False
    capability_profile: Literal["lab", "commercial-br"] = "lab"
    backup_enabled: bool = False
    backup_interval_seconds: float = Field(default=86400, ge=60, le=604800)
    backup_destination: str = "runtime/backups"
    rate_auth: int = Field(default=30, ge=1, le=10000)
    rate_write: int = Field(default=60, ge=1, le=10000)
    rate_read: int = Field(default=600, ge=1, le=100000)
    rate_stream: int = Field(default=120, ge=1, le=10000)
    ws_auth_timeout_seconds: float = Field(default=5, ge=0.05, le=10)

    @field_validator("ruview_http_url", "ruview_ws_url")
    @classmethod
    def local_ruview_only(cls, value: str, info):
        url = urlsplit(value)
        scheme = "http" if info.field_name == "ruview_http_url" else "ws"
        hosts = {"127.0.0.1", "localhost", "::1"}
        if info.data.get("container_network"):
            hosts.add("ruview")
        # Deliberately no arbitrary URL supplied through the dashboard (SSRF).
        if (
            url.scheme != scheme
            or url.hostname not in hosts
            or url.username is not None
            or url.password is not None
            or url.query
            or url.fragment
            or url.port is None
            or url.path not in ({"", "/"} if scheme == "http" else {"/ws/sensing"})
        ):
            raise ValueError("RuView URL must use a local host and the supported API path")
        return value.rstrip("/") if scheme == "http" else value
