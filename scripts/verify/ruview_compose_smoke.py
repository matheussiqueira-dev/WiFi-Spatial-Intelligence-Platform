#!/usr/bin/env python3
"""Official streaming + restart proof, restricted to the isolated F2 Compose project."""

import asyncio
import json
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import ProxyHandler, Request, build_opener

from dotenv import dotenv_values
from websockets.asyncio.client import connect

root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root / "apps/api"))
from app.contracts import RuViewEvent

PROJECT = "wifi-spatial-f2-compose-verification"
files = ["compose.yaml", "compose.ruview.yaml", "compose.ruview.verify.yaml"]
command = ["docker", "compose", "--env-file", "artifacts/f2-compose.env", "-p", PROJECT]
for filename in files:
    command.extend(["-f", filename])
token = dotenv_values(root / "artifacts/f2-compose.env")["SPATIAL_TOKEN"]


def request(path, body=None):
    headers = {"Authorization": f"Bearer {token}"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    req = Request(
        "http://127.0.0.1:4880/api/v1" + path,
        headers=headers,
        data=None if body is None else json.dumps(body).encode(),
    )
    # The bearer token must never travel through an environment proxy.
    with build_opener(ProxyHandler({})).open(req, timeout=3) as response:
        return json.load(response)


async def receive():
    async with connect(
        "ws://127.0.0.1:4880/api/v1/stream", origin="http://127.0.0.1:4380", proxy=None
    ) as ws:
        await ws.send(json.dumps({"token": token}))
        assert json.loads(await ws.recv())["type"] == "status"
        request("/sources/select", {"source": "RUVIEW_STREAM"})
        request("/simulation/start", {})
        while True:
            packet = json.loads(await asyncio.wait_for(ws.recv(), timeout=10))
            if packet["type"] == "event":
                event = RuViewEvent.model_validate(packet["data"])
                assert any(
                    item["event_id"] == str(event.event_id)
                    for item in request("/events")["items"]
                )
                return


async def receive_with_timeout():
    await asyncio.wait_for(receive(), timeout=15)


def main():
    container = subprocess.check_output(
        [*command, "ps", "-q", "api"], cwd=root, text=True
    ).strip()
    label = subprocess.check_output(
        [
            "docker",
            "inspect",
            container,
            "--format",
            '{{index .Config.Labels "com.docker.compose.project"}}',
        ],
        text=True,
    ).strip()
    if label != PROJECT:
        raise RuntimeError(
            "Refusing to restart a container outside the F2 verification project"
        )
    request("/simulation/stop", {})
    asyncio.run(receive_with_timeout())
    deadline = time.monotonic() + 5
    while request("/events")["total"] < 5 and time.monotonic() < deadline:
        time.sleep(0.1)
    request("/simulation/stop", {})
    before = request("/events")
    assert before["total"] >= 5
    subprocess.run(
        [*command, "restart", "api"], cwd=root, check=True, capture_output=True
    )
    for _ in range(50):
        try:
            state = request("/system/status")
            break
        except OSError:
            time.sleep(0.2)
    else:
        raise RuntimeError("API did not restart in time")
    after = request("/events")
    assert after == before
    assert state["state"] == "stopped" and state["latest"] is None
    receipt = {
        "project": PROJECT,
        "official_stream_persisted": True,
        "events": before["total"],
        "payloads_identical_after_restart": True,
        "api_stopped_after_restart": True,
    }
    (root / "artifacts/f2-compose-receipt.json").write_text(
        json.dumps(receipt, indent=2)
    )
    print(json.dumps(receipt))


if __name__ == "__main__":
    main()
