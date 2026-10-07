"""Dependency preflight for certified Stage-2 V3 sources.

No fallback to alternate families or cost semantics is permitted.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FROZEN = ROOT / "Research/Design/MTS_STAGE2_V3_PROVENANCE_20261007.json"
RECOVERED = ROOT / "Reconstruction/Certified-Stage2-Source-20261007"
SOURCES = {
    "computational_search": RECOVERED / "MTS_V4/computational_search.py",
    "search_families": RECOVERED / "MTS_V4/search_families.py",
    "derived_feature_factory": RECOVERED / "MTS_V4/derived_feature_factory.py",
}


def verify_recovered_sources():
    manifest = json.loads(FROZEN.read_text())
    expected = manifest["recovered_sources"]
    checks = {}
    for key, path in SOURCES.items():
        if not path.is_file():
            checks[key] = {"status": "MISSING", "path": str(path.relative_to(ROOT))}
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        checks[key] = {
            "status": "VERIFIED" if actual == expected.get(key + "_sha256") else "HASH_MISMATCH",
            "sha256": actual,
            "path": str(path.relative_to(ROOT)),
        }
    return {"decision": "PASS" if all(x["status"] == "VERIFIED" for x in checks.values()) else "BLOCK",
            "checks": checks}


if __name__ == "__main__":
    print(json.dumps(verify_recovered_sources(), indent=2))
