#!/usr/bin/env python3
"""Pin the installed project environment without local paths or editable packages.

Run only after an intentional dependency update, then validate Windows and Docker.
"""

from importlib.metadata import distribution, distributions
from pathlib import Path

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

root = Path(__file__).resolve().parents[2] / "apps/api"
excluded = {"pip", "setuptools", "wifi-spatial-api"}
installed = {canonicalize_name(d.metadata["Name"]): d.version for d in distributions()}
runtime = set()
pending = [
    "fastapi",
    "uvicorn",
    "websockets",
    "sqlalchemy",
    "alembic",
    "pydantic-settings",
]
while pending:
    name = canonicalize_name(pending.pop())
    if name in runtime:
        continue
    runtime.add(name)
    for specification in distribution(name).requires or []:
        requirement = Requirement(specification)
        if requirement.marker is None or requirement.marker.evaluate({"extra": ""}):
            pending.append(requirement.name)

for filename, names in [
    ("requirements.lock.txt", set(installed) - excluded),
    ("requirements.runtime.txt", runtime),
]:
    text = (
        "# Pinned dependencies; regenerate with scripts/verify/lock_dependencies.py.\n"
    )
    text += "\n".join(f"{name}=={installed[name]}" for name in sorted(names)) + "\n"
    (root / filename).write_text(text, encoding="utf-8")
