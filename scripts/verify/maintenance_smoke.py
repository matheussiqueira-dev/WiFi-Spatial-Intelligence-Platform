#!/usr/bin/env python3
"""Exercise Windows backup/restore wrappers using only a newly created fixture."""

import sqlite3
import subprocess
from contextlib import closing
from pathlib import Path
from uuid import uuid4


def main():
    root = Path(__file__).resolve().parents[2]
    directory = root / "artifacts" / f"maintenance-{uuid4()}"
    directory.mkdir(parents=True)
    source = directory / "source.db"
    with closing(sqlite3.connect(source)) as connection:
        connection.execute("CREATE TABLE events(payload TEXT)")
        connection.execute(
            "INSERT INTO events VALUES(?)", ('{"evidence_level":"L0_SYNTHETIC"}',)
        )
        connection.commit()
    for script, args in [
        (
            "backup.ps1",
            ["-Source", str(source), "-Destination", str(directory / "snapshots")],
        ),
        ("restore.ps1", None),
    ]:
        if args is None:
            snapshot = next((directory / "snapshots").glob("snapshot-*.db"))
            args = [
                "-Snapshot",
                str(snapshot),
                "-Destination",
                str(directory / "restored.db"),
            ]
        subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-File",
                str(root / "scripts/backup" / script),
                *args,
            ],
            check=True,
        )
    with closing(sqlite3.connect(directory / "restored.db")) as restored:
        assert restored.execute("SELECT payload FROM events").fetchall() == [
            ('{"evidence_level":"L0_SYNTHETIC"}',)
        ]
    print(
        "Windows wrappers: consistent backup and exact restore passed; usage database untouched"
    )


if __name__ == "__main__":
    main()
