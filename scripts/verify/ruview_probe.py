#!/usr/bin/env python3
"""Probe the actual official service; credentials and raw frames never go to stdout."""

import argparse
import asyncio
import sys
from pathlib import Path

from dotenv import dotenv_values

root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root / "apps/api"))
from app.config import Settings
from app.ruview import RuViewProvider


async def run(args):
    settings = Settings(
        token="verification-only-" + "x" * 40,
        ruview_token=dotenv_values(args.env_file).get("SPATIAL_RUVIEW_TOKEN") or "",
        ruview_http_url=f"http://127.0.0.1:{args.http_port}",
        ruview_ws_url=f"ws://127.0.0.1:{args.ws_port}/ws/sensing",
        _env_file=None,
    )
    provider = RuViewProvider(settings)
    await provider.connect()
    try:
        for _ in range(100):
            event = await provider.next_event()
            if event:
                print("Official REST + WebSocket verified: simulated / L0_SYNTHETIC")
                return
            await asyncio.sleep(0.1)
        raise RuntimeError(
            "Official RuView readiness failed: " + str(provider.last_error)
        )
    finally:
        await provider.disconnect()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", required=True)
    parser.add_argument("--http-port", type=int, default=4860)
    parser.add_argument("--ws-port", type=int, default=4861)
    asyncio.run(run(parser.parse_args()))
