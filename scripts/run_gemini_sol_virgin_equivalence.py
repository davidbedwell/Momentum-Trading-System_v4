#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from MTS_V4.virgin_equivalence import (
    EquivalenceProtocolError,
    VirginCandidate,
    deterministic_select_virgins,
    write_frozen_json,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Fail-closed MTS V4 Gemini-Sol virgin equivalence harness.")
    parser.add_argument("--candidate-manifest", required=True, help="JSON array of machine-derived virginity candidates")
    parser.add_argument("--experiment-root", required=True)
    parser.add_argument("--protocol-seed", default="MTS_V4_GEMINI_SOL_EQUIVALENCE_20260920_V1")
    parser.add_argument("--select-only", action="store_true", help="Freeze the deterministic three-ticker selection only")
    args = parser.parse_args()

    source = Path(args.candidate_manifest)
    rows = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise EquivalenceProtocolError("candidate manifest must be a JSON array")
    candidates = [VirginCandidate(**row) for row in rows]
    selection = deterministic_select_virgins(candidates, protocol_seed=args.protocol_seed)
    root = Path(args.experiment_root)
    write_frozen_json(root / "00_VIRGIN_SELECTION.json", selection)
    print(json.dumps(selection, indent=2, sort_keys=True))
    if args.select_only:
        return 0
    raise EquivalenceProtocolError(
        "selection is implemented and frozen; paid arm execution is intentionally blocked until "
        "repository-specific candidate-manifest derivation and frozen-workflow adapters are bound and tested"
    )


if __name__ == "__main__":
    raise SystemExit(main())
