"""Offline operator tools: consistent SQLite backup, verified restore and guarded retention."""

import argparse
import hashlib
import json
import shutil
import sqlite3
from contextlib import closing
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4


def integrity(path):
    with closing(sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)) as connection:
        if connection.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
            raise ValueError("SQLite integrity check failed")


def digest(path):
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def backup(source: Path, directory: Path):
    integrity(source)
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / f"snapshot-{datetime.now(UTC):%Y%m%dT%H%M%S}-{uuid4()}.db"
    # Copy and verify under a temporary name; only a verified copy becomes a snapshot.
    partial = directory / f".partial-{uuid4()}.db"
    try:
        with closing(sqlite3.connect(source.resolve().as_uri() + "?mode=ro", uri=True)) as original:
            with closing(sqlite3.connect(partial)) as snapshot:
                original.backup(snapshot)
        integrity(partial)
        partial.replace(target)
    finally:
        partial.unlink(missing_ok=True)
    target.with_suffix(".json").write_text(
        json.dumps(
            {
                "sha256": digest(target),
                "created_at": datetime.now(UTC).isoformat(),
                "kind": "sqlite-consistent-backup",
                "contains_secrets": False,
                "scope": "application database; keep private; not an anonymization guarantee",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return target


def restore(snapshot: Path, target: Path):
    manifest = json.loads(snapshot.with_suffix(".json").read_text(encoding="utf-8"))
    if digest(snapshot) != manifest["sha256"]:
        raise ValueError("backup checksum mismatch")
    integrity(snapshot)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        raise FileExistsError("destination already exists")
    # Exclusive create: never replace a running or existing database/WAL.
    if (
        target.with_name(target.name + "-wal").exists()
        or target.with_name(target.name + "-shm").exists()
    ):
        raise ValueError("destination has existing SQLite sidecars")
    with target.open("xb") as output, snapshot.open("rb") as original:
        shutil.copyfileobj(original, output)
    integrity(target)


def prune_snapshots(directory: Path, keep: int = 7, days: int = 30):
    if keep < 7 or days < 30:
        raise ValueError("keep at least seven snapshots and 30 days")
    candidates = sorted(
        directory.glob("snapshot-*.db"), key=lambda p: p.stat().st_mtime, reverse=True
    )
    cutoff = (datetime.now(UTC) - timedelta(days=days)).timestamp()
    removed = 0
    for path in candidates[keep:]:
        if path.stat().st_mtime >= cutoff:
            continue
        manifest = path.with_suffix(".json")
        if not manifest.exists():
            raise ValueError("unrecognized or altered snapshot; refusing deletion")
        data = json.loads(manifest.read_text(encoding="utf-8"))
        if data.get("kind") != "sqlite-consistent-backup" or data.get("sha256") != digest(path):
            raise ValueError("unrecognized or altered snapshot; refusing deletion")
        path.unlink()
        manifest.unlink()
        removed += 1
    return removed


def retain(source: Path, directory: Path, days: int = 90):
    """No HTTP route. Explicit offline action; preserve security events and legal holds."""
    if days < 90:
        raise ValueError("audit retention must be at least 90 days")
    if source.with_suffix(".hold").exists():
        raise ValueError("retention hold active")
    snapshot = backup(source, directory)
    cutoff = (datetime.now(UTC) - timedelta(days=days)).isoformat()
    with closing(sqlite3.connect(source)) as connection, connection:
        connection.execute("BEGIN IMMEDIATE")
        rows = connection.execute(
            "SELECT id,timestamp,action FROM audit_events WHERE timestamp < ? "
            "AND action NOT LIKE 'security.%' AND action NOT LIKE 'audit.%' ORDER BY id",
            (cutoff,),
        ).fetchall()
        archive = directory / f"audit-{uuid4()}.json"
        payload = json.dumps({"cutoff": cutoff, "rows": rows}, ensure_ascii=False).encode()
        with archive.open("xb") as output:
            output.write(payload)
        archive.with_suffix(".sha256").write_text(
            hashlib.sha256(payload).hexdigest(), encoding="ascii"
        )
        if (
            hashlib.sha256(archive.read_bytes()).hexdigest()
            != archive.with_suffix(".sha256").read_text()
        ):
            raise ValueError("archive verification failed")
        connection.execute(
            "DELETE FROM audit_events WHERE timestamp < ? "
            "AND action NOT LIKE 'security.%' AND action NOT LIKE 'audit.%'",
            (cutoff,),
        )
        connection.execute(
            "INSERT INTO audit_events(timestamp,action) VALUES(?,?)",
            (datetime.now(UTC).isoformat(), "audit.retention.archived"),
        )
    return {"archived": len(rows), "snapshot": snapshot.name, "archive": archive.name}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["backup", "restore", "retain", "prune"])
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--confirm-offline", action="store_true")
    args = parser.parse_args()
    if args.action == "backup":
        print(backup(args.source, args.destination).name)
    elif args.action == "restore":
        restore(args.source, args.destination)
        print("Restore verified")
    elif args.action == "prune" and args.confirm_offline:
        print(json.dumps({"removed_snapshots": prune_snapshots(args.destination)}))
    elif args.confirm_offline:
        print(json.dumps(retain(args.source, args.destination)))
    else:
        parser.error("retention requires --confirm-offline with the application stopped")


if __name__ == "__main__":
    main()
