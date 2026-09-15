#!/usr/bin/env python3
"""Durably capture paid/non-reproducible research bytes before source cleanup.

This is a persistence-boundary utility, not canonical Nexus publication.
It preserves source bytes exactly in two independent roots, content-addressed by
SHA-256, and records an append-only SQLite manifest in each root. Success is
reported only after both copies are read-back verified and both manifests are
committed. Standard library only.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import sqlite3
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

DB_NAME = "durability_manifest.sqlite3"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def inside_git(path: Path) -> Path | None:
    path = path.resolve()
    for candidate in (path, *path.parents):
        if (candidate / ".git").exists():
            return candidate
    return None


def same_or_nested(a: Path, b: Path) -> bool:
    a, b = a.resolve(), b.resolve()
    return a == b or a in b.parents or b in a.parents


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS paid_artifact_captures (
            source_sha256 TEXT PRIMARY KEY,
            captured_at TEXT NOT NULL,
            object_relpath TEXT NOT NULL UNIQUE,
            source_name TEXT NOT NULL,
            source_size INTEGER NOT NULL
        )
    """)
    conn.commit()


def atomic_verified_copy(source: Path, dest: Path, digest: str) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        if not dest.is_file() or sha256_file(dest) != digest:
            raise RuntimeError(f"immutable object collision/corruption: {dest}")
        return
    fd, tmp_name = tempfile.mkstemp(prefix=".durability-", dir=str(dest.parent))
    os.close(fd)
    tmp = Path(tmp_name)
    try:
        shutil.copyfile(source, tmp)
        if sha256_file(tmp) != digest:
            raise RuntimeError(f"copy verification failed: {dest}")
        os.replace(tmp, dest)
    finally:
        tmp.unlink(missing_ok=True)
    if sha256_file(dest) != digest:
        dest.unlink(missing_ok=True)
        raise RuntimeError(f"post-write verification failed: {dest}")


def record(root: Path, source: Path, dest: Path, digest: str, captured_at: str) -> None:
    catalog = root / "catalog"
    catalog.mkdir(parents=True, exist_ok=True)
    db = catalog / DB_NAME
    rel = str(dest.relative_to(root))
    with sqlite3.connect(db) as conn:
        init_db(conn)
        row = conn.execute(
            "SELECT object_relpath, source_size FROM paid_artifact_captures WHERE source_sha256=?",
            (digest,),
        ).fetchone()
        if row:
            existing = root / row[0]
            if not existing.is_file() or sha256_file(existing) != digest or row[1] != source.stat().st_size:
                raise RuntimeError(f"manifest/object integrity mismatch: {root}")
            return
        conn.execute(
            "INSERT INTO paid_artifact_captures VALUES (?, ?, ?, ?, ?)",
            (digest, captured_at, rel, source.name, source.stat().st_size),
        )
        conn.commit()


def verify_manifest(root: Path, digest: str, expected_size: int) -> Path:
    db = root / "catalog" / DB_NAME
    with sqlite3.connect(db) as conn:
        row = conn.execute(
            "SELECT object_relpath, source_size FROM paid_artifact_captures WHERE source_sha256=?",
            (digest,),
        ).fetchone()
    if not row or row[1] != expected_size:
        raise RuntimeError(f"manifest verification failed: {root}")
    obj = root / row[0]
    if not obj.is_file() or sha256_file(obj) != digest:
        raise RuntimeError(f"object verification failed: {root}")
    return obj


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, type=Path)
    ap.add_argument("--primary-root", required=True, type=Path)
    ap.add_argument("--backup-root", required=True, type=Path)
    args = ap.parse_args()

    source = args.source.expanduser().resolve()
    primary = args.primary_root.expanduser().resolve()
    backup = args.backup_root.expanduser().resolve()
    if not source.is_file():
        raise SystemExit(f"FAIL: source not found: {source}")
    if same_or_nested(primary, backup):
        raise SystemExit("FAIL: primary and backup roots must be independent (not equal or nested)")
    for label, root in (("primary", primary), ("backup", backup)):
        git_root = inside_git(root)
        if git_root:
            raise SystemExit(f"FAIL: {label} root is inside Git working tree: {git_root}")

    digest = sha256_file(source)
    suffix = source.suffix if source.suffix else ".bin"
    rel = Path("objects") / "paid_research" / digest[:2] / f"{digest}{suffix}"
    captured_at = datetime.now(timezone.utc).isoformat()

    try:
        primary_obj = primary / rel
        backup_obj = backup / rel
        atomic_verified_copy(source, primary_obj, digest)
        atomic_verified_copy(source, backup_obj, digest)
        record(primary, source, primary_obj, digest, captured_at)
        record(backup, source, backup_obj, digest, captured_at)
        primary_verified = verify_manifest(primary, digest, source.stat().st_size)
        backup_verified = verify_manifest(backup, digest, source.stat().st_size)
    except Exception as exc:
        raise SystemExit(f"FAIL: durability capture incomplete: {exc}") from exc

    print(
        "DURABLE_VERIFIED "
        f"sha256={digest} bytes={source.stat().st_size} "
        f"primary={primary_verified} backup={backup_verified}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
