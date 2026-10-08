"""Append-only, atomic GA4 candidate evidence store with stable deduplication."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

from .ga4_horizon_contract import validate_horizons


def _canonical(record):
    return json.dumps(record, sort_keys=True, separators=(",", ":"), allow_nan=False)


def append_record(path, record):
    """Write one candidate/fold/side/context observation; reject conflicting replays.

    One JSON file per observation avoids partial JSONL lines and allows restart.
    Existing content is never overwritten. Caller must serialize concurrent writes.
    """
    validate_horizons(p["horizon"] for p in record["daily_horizon_evidence"])
    for key in ("candidate_id", "fold", "side", "data_provenance"):
        if not record.get(key):
            raise ValueError(f"Missing {key}")
    root = Path(path)
    root.mkdir(parents=True, exist_ok=True)
    identity = {key: record[key] for key in ("candidate_id", "fold", "side", "data_provenance")}
    name = hashlib.sha256(_canonical(identity).encode()).hexdigest() + ".json"
    destination = root / name
    payload = _canonical(record).encode("utf-8") + b"\n"
    if destination.exists():
        if destination.read_bytes() != payload:
            raise ValueError("Conflicting evidence for existing candidate identity")
        return destination, False
    fd = os.open(destination, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
    try:
        with os.fdopen(fd, "wb") as output:
            output.write(payload)
            output.flush()
            os.fsync(output.fileno())
    except BaseException:
        destination.unlink(missing_ok=True)
        raise
    return destination, True


def read_records(path):
    root = Path(path)
    if not root.exists():
        return []
    records = []
    for file in sorted(root.glob("*.json")):
        record = json.loads(file.read_text())
        validate_horizons(p["horizon"] for p in record["daily_horizon_evidence"])
        records.append(record)
    return records
