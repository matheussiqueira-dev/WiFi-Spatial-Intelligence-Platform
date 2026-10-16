#!/usr/bin/env python3
import os
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts/verify"))
sys.path.insert(0, str(ROOT / "apps/api"))

POWERSHELL = shutil.which("powershell.exe")


@pytest.fixture(autouse=True)
def isolated_environment(monkeypatch):
    for name in list(os.environ):
        if name.startswith(("SPATIAL_", "E2E_")) or name == "FORWARDED_ALLOW_IPS":
            monkeypatch.delenv(name, raising=False)
