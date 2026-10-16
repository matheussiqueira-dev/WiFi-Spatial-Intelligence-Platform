#!/usr/bin/env python3
import json
from importlib.metadata import distributions
from pathlib import Path

root = Path(__file__).resolve().parents[2]
entries = []
for distribution in distributions():
    metadata = distribution.metadata
    entries.append(
        {
            "name": metadata["Name"],
            "version": distribution.version,
            "license": metadata.get("License-Expression")
            or (metadata.get("License") or "UNVERIFIED").splitlines()[0][:160],
        }
    )
target = root / "artifacts/third-party-python-licenses.json"
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(
    json.dumps(sorted(entries, key=lambda entry: entry["name"].lower()), indent=2),
    encoding="utf-8",
)
print(
    json.dumps(
        [
            entry
            for entry in entries
            if entry["name"].lower()
            in {"fastapi", "starlette", "pydantic", "sqlalchemy", "httpx2"}
        ]
    )
)
