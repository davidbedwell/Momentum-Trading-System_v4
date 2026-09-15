#!/usr/bin/env python3
"""Publish an existing Research Package JSON into the canonical Research Nexus.

This migration/import utility preserves the source bytes exactly and registers
those bytes through the existing canonical Research Nexus publication API.
Scientific meaning is not inferred or modified.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

# Executing a script by pathname puts scripts/ rather than the repository root
# on sys.path. Resolve the repo root from this file so the documented standalone
# invocation works without requiring callers to set PYTHONPATH.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Core.research_nexus import (  # noqa: E402
    Producer,
    Provenance,
    ResearchNexusConfig,
    build_research_nexus,
    create_artifact_envelope,
)


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _inside_git(path: Path) -> Path | None:
    probe = path.resolve()
    for candidate in (probe, *probe.parents):
        if (candidate / ".git").exists():
            return candidate
    return None


def _first_string(doc: dict, *keys: str) -> str | None:
    for key in keys:
        value = doc.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, type=Path)
    ap.add_argument("--canonical-root", required=True, type=Path)
    args = ap.parse_args()

    source = args.source.expanduser().resolve()
    root = args.canonical_root.expanduser().resolve()
    if not source.is_file():
        raise SystemExit(f"FAIL: source not found: {source}")
    git_root = _inside_git(root)
    if git_root is not None:
        raise SystemExit(f"FAIL: canonical root is inside Git working tree: {git_root}")

    payload = source.read_bytes()
    try:
        doc = json.loads(payload.decode("utf-8"))
    except Exception as exc:
        raise SystemExit(f"FAIL: Research Package is not UTF-8 JSON: {exc}") from exc
    if not isinstance(doc, dict):
        raise SystemExit("FAIL: Research Package root must be a JSON object")

    package_id = _first_string(doc, "research_package_id", "package_id", "id")
    if package_id is None:
        if source.stem.startswith("RP-"):
            package_id = source.stem
        else:
            raise SystemExit("FAIL: no Research Package identity found")
    if not package_id.startswith("RP-"):
        raise SystemExit(f"FAIL: unexpected Research Package identity: {package_id}")

    ticker = _first_string(doc, "ticker", "symbol", "subject")
    digest = _sha256(payload)
    artifact_id = f"legacy-research-package:{package_id}"

    root.mkdir(parents=True, exist_ok=True)
    nexus = build_research_nexus(ResearchNexusConfig(runtime_root=root))
    envelope = create_artifact_envelope(
        artifact_id=artifact_id,
        artifact_version=1,
        artifact_type="research_package",
        schema_id="mts.legacy-research-package-json",
        schema_version=1,
        producer=Producer(producer_type="migration", producer_id="campaign-rp-importer-v1"),
        provenance=Provenance(
            method_id="migration.import-existing-research-package",
            parameters={
                "source_filename": source.name,
                "source_sha256": digest,
                "source_package_id": package_id,
            },
        ),
        lifecycle_state="ACTIVE",
        persistence_class="CLASS_II",
        retention_class="PERMANENT",
        backup_requirement="INDEPENDENT_BACKUP_REQUIRED",
        tags=tuple(x for x in ("research-package", package_id, ticker) if x),
    )

    result = nexus.publish(
        envelope=envelope,
        payload=payload,
        media_type="application/json",
        index_fields={
            "artifact_type": "research_package",
            "research_package_id": package_id,
            "ticker": ticker or "",
            "source_sha256": digest,
        },
    )
    nexus.verify(result.artifact_ref)
    recovered = nexus.get(result.artifact_ref, verify=True)
    recovered_payload = recovered.payload
    if recovered_payload != payload:
        raise SystemExit("FAIL: canonical round-trip bytes differ from source")

    print(
        f"PUBLISHED package_id={package_id} artifact_id={artifact_id} "
        f"sha256={digest} reconciled={result.reconciled} verified=true"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
