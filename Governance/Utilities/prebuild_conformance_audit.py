#!/usr/bin/env python3

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = (
    "Architecture/SYSTEM_ARCHITECTURE.md",
    "Architecture/ENGINE_ARCHITECTURE.md",
    "Architecture/Engines/RESEARCH_DIRECTOR_ARCHITECTURE.md",
    "Architecture/Technical-Design/RESEARCH_DIRECTOR_TECHNICAL_DESIGN.md",
    "Governance/Standards/RESEARCH_STANDARD.md",
    "Governance/Standards/ENGINE_INTERFACE_STANDARD.md",
    "Governance/Standards/ARTIFACT_GOVERNANCE_STANDARD.md",
    "Governance/Standards/SECURITY_AND_AUTHORITY_STANDARD.md",
    "Core/research_nexus/schema_registry.py",
)

PROHIBITED_RUNTIME_TERMS = (
    "10-AI-Research-Director",
    "Research/10-",
    "Research/09-",
    "A09-",
    "Engine10",
    "engine10",
)

def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)

def check_required_files() -> None:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).exists()]
    if missing:
        fail(f"missing governing file(s): {missing}")
    print("PASS: governing architecture/standards present")

def check_schema_contract() -> None:
    schema_root = ROOT / "Governance/Schemas"
    examples = 0

    for path in sorted(schema_root.glob("*.json")):
        try:
            doc = json.loads(path.read_text())
        except Exception:
            continue

        if all(k in doc for k in ("schema_id", "schema_version", "status")):
            examples += 1

    if examples == 0:
        fail("no governed schema examples found")

    print(f"PASS: governed schema pattern available ({examples} schemas)")

def check_research_director_legacy_coupling() -> None:
    targets = (
        ROOT / "Engines/ResearchDirector",
        ROOT / "Architecture/Engines/RESEARCH_DIRECTOR_ARCHITECTURE.md",
        ROOT / "Architecture/Technical-Design/RESEARCH_DIRECTOR_TECHNICAL_DESIGN.md",
    )

    violations = []

    for target in targets:
        if not target.exists():
            continue

        files = [target] if target.is_file() else list(target.rglob("*.py"))

        for path in files:
            text = path.read_text(errors="ignore")
            for term in PROHIBITED_RUNTIME_TERMS:
                if term in text:
                    violations.append((str(path.relative_to(ROOT)), term))

    if violations:
        print("Legacy/runtime coupling violations:")
        for path, term in violations:
            print(f"  {path}: {term}")
        fail("Research Director contains prohibited legacy runtime references")

    print("PASS: zero prohibited Research Director legacy runtime coupling")

def check_private_storage_coupling() -> None:
    rd_root = ROOT / "Engines/ResearchDirector"
    if not rd_root.exists():
        print("PASS: Research Director package not yet implemented")
        return

    prohibited = (
        "Warehouse/",
        "Sources/01_Raw",
        "sqlite3",
        "payload_root",
        "parquet_path",
    )

    violations = []

    for path in rd_root.rglob("*.py"):
        text = path.read_text(errors="ignore")
        for term in prohibited:
            if term in text:
                violations.append((str(path.relative_to(ROOT)), term))

    if violations:
        print("Private-storage coupling violations:")
        for path, term in violations:
            print(f"  {path}: {term}")
        fail("Research Director contains prohibited private-storage coupling")

    print("PASS: no prohibited Research Director private-storage coupling")

def main() -> None:
    print("===== MTS PRE-BUILD CONFORMANCE AUDIT =====")
    check_required_files()
    check_schema_contract()
    check_research_director_legacy_coupling()
    check_private_storage_coupling()
    print("PASS: PRE-BUILD CONFORMANCE AUDIT")

if __name__ == "__main__":
    main()
