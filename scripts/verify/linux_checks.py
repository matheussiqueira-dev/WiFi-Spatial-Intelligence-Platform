#!/usr/bin/env python3
"""Run real backend checks and dependency audits in an isolated Linux container."""

import subprocess
import sys

commands = [
    ["ruff", "check", "apps/api", "scripts/verify", "scripts/network"],
    ["ruff", "format", "--check", "apps/api", "scripts/verify", "scripts/network"],
    ["mypy", "--config-file", "apps/api/pyproject.toml", "apps/api/app"],
    ["pytest", "apps/api/tests", "-q"],
    ["pytest", "scripts/verify/tests", "-q"],
    ["pip_audit", "-r", "apps/api/requirements.runtime.txt"],
    ["pip_audit", "-r", "apps/api/requirements.lock.txt"],
]
for arguments in commands:
    print(f"Checking: {' '.join(arguments)}", flush=True)
    subprocess.run([sys.executable, "-m", *arguments], check=True)
