#!/usr/bin/env python3
"""Verify persistence across restart, only on the named local verification stack."""

import argparse
import json
import subprocess
import time
from pathlib import Path
from urllib.request import Request, urlopen

parser = argparse.ArgumentParser()
parser.add_argument("--docker", default="docker")
args = parser.parse_args()
root = Path(__file__).resolve().parents[2]
project = "wifi-spatial-verification"
compose = [args.docker, "compose", "--project-name", project]
container = subprocess.check_output(
    [*compose, "ps", "--quiet", "api"], text=True
).strip()
if not container:
    raise RuntimeError("Start the isolated verification stack first")
label = subprocess.check_output(
    [
        args.docker,
        "inspect",
        "--format",
        '{{ index .Config.Labels "com.docker.compose.project" }}',
        container,
    ],
    text=True,
).strip()
if label != project:
    raise RuntimeError("Refusing to mutate a stack outside the verification project")
token = next(
    line.split("=", 1)[1].strip()
    for line in (root / ".env").read_text().splitlines()
    if line.startswith("SPATIAL_TOKEN=")
)


def request(path, method="GET", data=None):
    body = json.dumps(data).encode() if data is not None else None
    query = Request(
        f"http://127.0.0.1:8000/api/v1{path}",
        data=body,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    with urlopen(query, timeout=5) as response:
        return json.load(response)


request("/simulation/stop", "POST")
baseline = request("/events")["total"]
request(
    "/simulation/start", "POST", {"scenario": "walking", "occupants": 2, "speed": 4}
)
deadline = time.monotonic() + 5
while request("/events")["total"] < baseline + 4:
    if time.monotonic() > deadline:
        raise RuntimeError("No events persisted")
    time.sleep(0.1)
request("/simulation/stop", "POST")
before = request("/events")
subprocess.run([*compose, "restart", "api"], check=True)
deadline = time.monotonic() + 20
while True:
    try:
        after = request("/events")
        break
    except OSError:
        if time.monotonic() > deadline:
            raise
        time.sleep(0.2)
assert after == before, "History changed across container restart"
assert request("/system/status")["state"] == "stopped"
assert all(event["evidence_level"] == "L0_SYNTHETIC" for event in after["items"])
print(
    json.dumps(
        {
            "container_restart": "passed",
            "persisted_events": after["total"],
            "evidence_level": "L0_SYNTHETIC",
            "project": project,
        }
    )
)
