#!/usr/bin/env python3
"""Opt-in host collector. No credentials/identity or raw command output in logs."""

import argparse
import json
import os
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "apps/api"))
from app.adapters.windows_wifi import probe_gateway, read_channel_survey, read_link
from app.config import Settings
from app.network_contracts import ChannelSurvey, NetworkConfiguration, NetworkSample


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, file, code, message, headers, new_url):
        return None


def local_endpoint(value: str) -> str:
    url = urlsplit(value)
    if (
        url.scheme != "http"
        or url.hostname not in {"127.0.0.1", "localhost", "::1"}
        or url.username
        or url.password
        or url.query
        or url.fragment
        or url.path not in {"", "/"}
        or not url.port
    ):
        raise ValueError("collector API must be an explicit loopback HTTP endpoint")
    return value.rstrip("/")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-url", default="http://127.0.0.1:8000")
    parser.add_argument("--interval", type=int, choices=range(15, 61), default=15)
    parser.add_argument("--gateway-probes", action="store_true")
    parser.add_argument(
        "--channel-survey",
        action="store_true",
        help="every 60 s, send per-channel aggregates of networks Windows already listed",
    )
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    if sys.platform != "win32":
        parser.error(
            "collector requires the Windows host; it cannot read the host radio from Docker"
        )
    endpoint = local_endpoint(args.api_url)
    token = Settings(_env_file=ROOT / ".env").token
    opener = build_opener(ProxyHandler({}), NoRedirect())
    session_id = uuid4()
    runtime = ROOT / "runtime"
    runtime.mkdir(exist_ok=True)
    lock = runtime / "wifi-monitor.lock"
    stop = runtime / "wifi-monitor.stop"
    if not args.once:
        try:
            with lock.open("x", encoding="utf-8") as handle:
                json.dump({"pid": os.getpid(), "collector_id": str(session_id)}, handle)
        except FileExistsError:
            print(
                "collector lock exists; verify its PID before restarting",
                file=sys.stderr,
            )
            return 1
    failures = 0
    delivered = 0
    surveyed_at = float("-inf")
    unavailable = False
    try:
        while args.once or not stop.exists():
            started = time.monotonic()
            try:
                config_request = Request(
                    endpoint + "/api/v1/network/config",
                    headers={"Authorization": "Bearer " + token},
                )
                with opener.open(config_request, timeout=5) as response:
                    config = NetworkConfiguration.model_validate_json(
                        response.read(2048)
                    )
                reading = read_link()
                probes = (
                    probe_gateway()
                    if args.gateway_probes and reading["link_state"] == "CONNECTED"
                    else {}
                )
                sample = NetworkSample(
                    sample_id=uuid4(),
                    collector_id=session_id,
                    timestamp=datetime.now(UTC),
                    location=config.location,
                    **reading,
                    **probes,
                )
                request = Request(
                    endpoint + "/api/v1/network/samples",
                    data=sample.model_dump_json().encode(),
                    headers={
                        "Authorization": "Bearer " + token,
                        "Content-Type": "application/json",
                    },
                    method="POST",
                )
                with opener.open(request, timeout=5) as response:
                    json.loads(response.read(1024))
                delivered += 1
                unavailable = False
                if args.channel_survey and time.monotonic() - surveyed_at >= 60:
                    surveyed_at = time.monotonic()
                    survey = ChannelSurvey(
                        survey_id=uuid4(),
                        collector_id=session_id,
                        timestamp=datetime.now(UTC),
                        location=config.location,
                        **read_channel_survey(),
                    )
                    survey_request = Request(
                        endpoint + "/api/v1/network/channel-surveys",
                        data=survey.model_dump_json().encode(),
                        headers={
                            "Authorization": "Bearer " + token,
                            "Content-Type": "application/json",
                        },
                        method="POST",
                    )
                    with opener.open(survey_request, timeout=5) as response:
                        json.loads(response.read(1024))
                if args.once:
                    print(
                        json.dumps(
                            {
                                "delivered": delivered,
                                "link_state": sample.link_state,
                                "signal_percent": sample.signal_percent,
                                "probe_sent": sample.probe_sent,
                                "probe_replies": len(sample.probe_rtt_ms),
                                "channel_survey": args.channel_survey,
                            }
                        )
                    )
            except (OSError, ValueError, TimeoutError, URLError):
                failures += 1
                if not unavailable:
                    print("local collection or delivery unavailable", file=sys.stderr)
                unavailable = True
                if args.once:
                    return 1
            if args.once:
                break
            (runtime / "wifi-monitor-status.json").write_text(
                json.dumps(
                    {
                        "pid": os.getpid(),
                        "delivered": delivered,
                        "failures": failures,
                        "updated_at": datetime.now(UTC).isoformat(),
                    }
                ),
                encoding="utf-8",
            )
            deadline = started + args.interval
            while time.monotonic() < deadline and not stop.exists():
                time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        if not args.once:
            lock.unlink(missing_ok=True)
            stop.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
