#!/usr/bin/env python3
"""Every uvicorn launcher must keep the real loopback peer for rate limiting (ADR-005)."""

import importlib
import json
import re

import pytest
from conftest import ROOT
from starlette.testclient import TestClient

# The package re-exports the click command as ``uvicorn.main``; fetch the module itself.
uvicorn_cli = importlib.import_module("uvicorn.main")


def start_ps1_args():
    text = (ROOT / "scripts/dev/start.ps1").read_text(encoding="utf-8")
    items = re.search(r"-ArgumentList @\(([^)]*)\)", text).group(1)
    tokens = [a or b for a, b in re.findall(r"'([^']*)'|\"([^\"]*)\"", items)]
    return [token.replace("$ApiPort", "8000") for token in tokens]


def playwright_args():
    text = (ROOT / "apps/web/playwright.config.ts").read_text(encoding="utf-8")
    command = re.search(r"(-m uvicorn [^`]*)`", text).group(1)
    return command.replace("${apiPort}", "4810").split()


def dockerfile_args():
    text = (ROOT / "apps/api/Dockerfile").read_text(encoding="utf-8")
    return json.loads(re.search(r"^CMD (\[.*\])$", text, re.MULTILINE).group(1))


LAUNCHERS = {
    "start.ps1": start_ps1_args,
    "playwright.config.ts": playwright_args,
    "Dockerfile": dockerfile_args,
}


def launcher_config(arguments, monkeypatch):
    """Build the uvicorn Config exactly as its CLI would, without binding a socket."""
    arguments = arguments[arguments.index("uvicorn") + 1 :]
    arguments[arguments.index("--app-dir") + 1] = str(ROOT / "apps/api")
    configs = []

    class CapturedServer:
        started = True

        def __init__(self, config):
            configs.append(config)

        def run(self):
            pass

    monkeypatch.setattr(uvicorn_cli, "Server", CapturedServer)
    uvicorn_cli.main.main(args=arguments, standalone_mode=False)
    return configs[0]


@pytest.mark.parametrize("launcher", LAUNCHERS)
def test_launcher_disables_proxy_headers(launcher, monkeypatch):
    config = launcher_config(LAUNCHERS[launcher](), monkeypatch)
    assert config.proxy_headers is False


@pytest.mark.parametrize("launcher", LAUNCHERS)
def test_forwarded_for_does_not_change_rate_limited_peer(
    launcher, monkeypatch, tmp_path
):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("SPATIAL_TOKEN", "test-only-" + "x" * 40)
    monkeypatch.setenv("SPATIAL_DATABASE_URL", f"sqlite:///{tmp_path / 'launcher.db'}")
    monkeypatch.setenv("SPATIAL_RATE_AUTH", "3")
    config = launcher_config(LAUNCHERS[launcher](), monkeypatch)
    config.load()
    application = config.loaded_app
    while not hasattr(application, "state"):
        application = application.app
    with TestClient(
        config.loaded_app, base_url="http://127.0.0.1:8000", client=("127.0.0.1", 50000)
    ) as client:
        statuses = [
            client.get(
                "/api/v1/events",
                headers={
                    "Authorization": "Bearer wrong-" + "x" * 32,
                    "X-Forwarded-For": f"10.0.0.{attempt}",
                },
            ).status_code
            for attempt in range(6)
        ]
    assert set(application.state.limiter.entries) <= {"127.0.0.1"}
    assert 401 not in statuses[3:], statuses
