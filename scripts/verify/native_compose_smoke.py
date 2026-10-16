#!/usr/bin/env python3
"""Restart proof restricted to the independent verification stack, never a usage database."""

import hashlib
import json
import subprocess
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from uuid import uuid4

from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[2]
PROJECT = "wifi-spatial-native-e2e"
COMMAND = [
    "docker",
    "compose",
    "--env-file",
    "artifacts/native-e2e.env",
    "-f",
    "compose.yaml",
    "-f",
    "compose.native.verify.yaml",
    "-p",
    PROJECT,
]


def main():
    container = subprocess.check_output(
        [*COMMAND, "ps", "-q", "api"], cwd=ROOT, text=True
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
        raise RuntimeError("Refusing to restart an unrelated container")
    token = dotenv_values(ROOT / "artifacts/native-e2e.env")["SPATIAL_TOKEN"]

    def request(path, body=None):
        req = Request(
            "http://127.0.0.1:4900/api/v1" + path,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            data=None if body is None else json.dumps(body).encode(),
        )
        with urlopen(req, timeout=5) as response:
            return json.load(response)

    request("/simulation/stop", {})
    request("/sources/select", {"source": "synthetic-native"})
    request("/simulation/start", {"scenario": "entering", "occupants": 3, "speed": 4})
    deadline = time.monotonic() + 8
    while request("/system/status")["produced_events"] < 12:
        if time.monotonic() > deadline:
            raise RuntimeError("native observations not persisted in time")
        time.sleep(0.1)
    request("/simulation/stop", {})
    before = request("/events?limit=200")
    query = {
        "start": (datetime.now(UTC) - timedelta(days=1)).isoformat(),
        "end": datetime.now(UTC).isoformat(),
        "bucket": "five_minutes",
        "source_id": "native-01",
    }
    suffix = "?" + urlencode(query)
    replay = request("/analytics/replay" + suffix)
    identifier = request("/analytics/reports", query)["id"]
    report = request(f"/analytics/reports/{identifier}")
    experiment = request("/model-lab/runs", {"seed": 42})
    experiment_id = experiment["id"]
    assert report["summary"]["samples"] >= 12
    request(
        "/network/samples",
        {
            "sample_id": str(uuid4()),
            "collector_id": str(uuid4()),
            "timestamp": datetime.now(UTC).isoformat(),
            "location": "Fixture Restart",
            "link_state": "UNAVAILABLE",
            "collector_error": "read_failed",
        },
    )
    network_before = request("/network/report?limit=200")["items"]
    network_config = request("/network/config")
    subprocess.run(
        [*COMMAND, "restart", "api"], cwd=ROOT, capture_output=True, check=True
    )
    for _ in range(60):
        try:
            state = request("/system/status")
            break
        except OSError:
            time.sleep(0.2)
    else:
        raise RuntimeError("API did not restart")
    assert request("/events?limit=200") == before
    assert request("/analytics/replay" + suffix) == replay
    assert request(f"/analytics/reports/{identifier}") == report
    assert request(f"/model-lab/runs/{experiment_id}") == experiment
    assert request("/network/report?limit=200")["items"] == network_before
    assert request("/network/config") == network_config
    assert state["provider"] == "synthetic-native" and state["state"] == "stopped"
    receipt = {
        "project": PROJECT,
        "events_total": before["total"],
        "compared_event_payloads": len(before["items"]),
        "events_sha256": hashlib.sha256(
            json.dumps(before, sort_keys=True).encode()
        ).hexdigest(),
        "saved_report_preserved": True,
        "replay_preserved": True,
        "experiment_preserved": True,
        "network_samples_preserved": len(network_before),
        "network_configuration_preserved": True,
        "native_default_after_restart": True,
        "legacy_enabled": state["legacy_lab_enabled"],
        "recorded_at": datetime.now(UTC).isoformat(),
    }
    (ROOT / "artifacts/native-compose-receipt.json").write_text(
        json.dumps(receipt, indent=2), encoding="utf-8"
    )
    print(json.dumps(receipt))


if __name__ == "__main__":
    main()
