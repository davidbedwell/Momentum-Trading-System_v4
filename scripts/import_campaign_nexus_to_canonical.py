#!/usr/bin/env python3
"""Import durable MTS v4 campaign research state into a canonical local Nexus archive.

This is a durability bridge for the existing MTS_V4_RESEARCH_NEXUS_V1 campaign
format. It does not make Git the home of Class-II assets. The destination is an
independent persistent Nexus root outside the repository.

The import is append-only by content hash. A source file is copied into an
immutable object store, indexed in a local SQLite manifest, then read back and
hash-verified before success is reported. Existing identical objects are
idempotent; an identity collision with different content fails closed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sqlite3
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

FORMAT = "MTS_V4_RESEARCH_NEXUS_V1"
DB_NAME = "durability_manifest.sqlite3"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_source(path: Path) -> dict:
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValueError(f"source is not valid JSON: {exc}") from exc
    if not isinstance(doc, dict) or doc.get("format") != FORMAT:
        raise ValueError(f"source must be {FORMAT}")
    return doc


def subject_keys(doc: dict) -> list[str]:
    out: list[str] = []
    for item in doc.get("subjects", []):
        if isinstance(item, dict):
            key = item.get("subject_id") or item.get("ticker") or item.get("symbol")
            if key:
                out.append(str(key))
    return sorted(set(out))


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS campaign_nexus_imports (
            source_sha256 TEXT PRIMARY KEY,
            imported_at TEXT NOT NULL,
            object_relpath TEXT NOT NULL UNIQUE,
            source_name TEXT NOT NULL,
            source_size INTEGER NOT NULL,
            nexus_format TEXT NOT NULL,
            subjects_json TEXT NOT NULL,
            findings_count INTEGER NOT NULL,
            evidence_metadata_count INTEGER NOT NULL,
            analysis_result_metadata_count INTEGER NOT NULL,
            finding_retractions_count INTEGER NOT NULL
        )
    """)
    conn.commit()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, type=Path)
    ap.add_argument("--canonical-root", required=True, type=Path)
    args = ap.parse_args()

    source = args.source.expanduser().resolve()
    root = args.canonical_root.expanduser().resolve()
    if not source.is_file():
        raise SystemExit(f"FAIL: source not found: {source}")

    # Class-II state must not accidentally be placed in a Git working tree.
    for parent in [root, *root.parents]:
        if (parent / ".git").exists():
            raise SystemExit(f"FAIL: canonical root is inside Git working tree: {parent}")

    doc = validate_source(source)
    digest = sha256_file(source)
    objects = root / "objects" / "campaign_nexus"
    catalog = root / "catalog"
    objects.mkdir(parents=True, exist_ok=True)
    catalog.mkdir(parents=True, exist_ok=True)
    dest = objects / f"{digest}.json"
    db = catalog / DB_NAME

    with sqlite3.connect(db) as conn:
        init_db(conn)
        row = conn.execute(
            "SELECT object_relpath FROM campaign_nexus_imports WHERE source_sha256=?",
            (digest,),
        ).fetchone()
        if row:
            existing = root / row[0]
            if not existing.is_file() or sha256_file(existing) != digest:
                raise SystemExit("FAIL: manifest/object integrity mismatch")
            print(f"ALREADY_PRESENT sha256={digest} object={existing}")
            return 0

        if dest.exists() and sha256_file(dest) != digest:
            raise SystemExit(f"FAIL: immutable object collision: {dest}")

        fd, tmp_name = tempfile.mkstemp(prefix=".nexus-import-", dir=str(objects))
        os.close(fd)
        tmp = Path(tmp_name)
        try:
            shutil.copyfile(source, tmp)
            if sha256_file(tmp) != digest:
                raise SystemExit("FAIL: copy verification failed")
            os.replace(tmp, dest)
        finally:
            tmp.unlink(missing_ok=True)

        if sha256_file(dest) != digest:
            dest.unlink(missing_ok=True)
            raise SystemExit("FAIL: post-write verification failed")

        rel = str(dest.relative_to(root))
        conn.execute(
            """INSERT INTO campaign_nexus_imports VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                digest,
                datetime.now(timezone.utc).isoformat(),
                rel,
                source.name,
                source.stat().st_size,
                FORMAT,
                json.dumps(subject_keys(doc), separators=(",", ":")),
                len(doc.get("findings", [])),
                len(doc.get("evidence_metadata", [])),
                len(doc.get("analysis_result_metadata", [])),
                len(doc.get("finding_retractions", [])),
            ),
        )
        conn.commit()

    print(
        "IMPORTED "
        f"sha256={digest} subjects={subject_keys(doc)} "
        f"findings={len(doc.get('findings', []))} "
        f"evidence={len(doc.get('evidence_metadata', []))} "
        f"analysis_metadata={len(doc.get('analysis_result_metadata', []))} "
        f"object={dest}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
