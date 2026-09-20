#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from MTS_V4.virgin_candidate_derivation import candidate_manifest, derive_virgin_candidates
from MTS_V4.virgin_equivalence import (
    EquivalenceProtocolError,
    VirginCandidate,
    deterministic_select_virgins,
    write_frozen_json,
)


def _load_candidates(path: str | Path) -> list[VirginCandidate]:
    source = Path(path).expanduser().resolve()
    rows = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise EquivalenceProtocolError("candidate manifest must be a JSON array")
    return [VirginCandidate(**row) for row in rows]


def main() -> int:
    parser = argparse.ArgumentParser(description="Fail-closed MTS V4 Gemini-Sol virgin equivalence harness.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--candidate-manifest", help="Previously machine-derived virginity candidate JSON")
    source.add_argument("--derive-candidates", action="store_true", help="Derive candidates from authoritative MTS state")
    parser.add_argument("--partition")
    parser.add_argument("--membership-csv")
    parser.add_argument("--prior-sol-audit", action="append", default=[])
    parser.add_argument("--exposure-ledger", action="append", default=[])
    parser.add_argument("--research-root", action="append", default=[])
    parser.add_argument("--derived-market-root")
    parser.add_argument("--experiment-root", required=True)
    parser.add_argument("--protocol-seed", default="MTS_V4_GEMINI_SOL_EQUIVALENCE_20260920_V1")
    parser.add_argument("--select-only", action="store_true", help="Freeze deterministic candidate manifest and three-ticker selection only")
    args = parser.parse_args()

    root = Path(args.experiment_root).expanduser().resolve()
    if args.derive_candidates:
        required = {
            "--partition": args.partition,
            "--membership-csv": args.membership_csv,
            "--derived-market-root": args.derived_market_root,
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise EquivalenceProtocolError(f"candidate derivation missing required arguments: {missing}")
        if not args.prior_sol_audit:
            raise EquivalenceProtocolError("candidate derivation requires at least one --prior-sol-audit")
        if not args.exposure_ledger:
            raise EquivalenceProtocolError("candidate derivation requires at least one --exposure-ledger")
        if not args.research_root:
            raise EquivalenceProtocolError("candidate derivation requires at least one --research-root")
        candidates = list(derive_virgin_candidates(
            partition_path=args.partition,
            membership_csv=args.membership_csv,
            prior_sol_audits=args.prior_sol_audit,
            exposure_ledgers=args.exposure_ledger,
            research_roots=args.research_root,
            derived_market_root=args.derived_market_root,
        ))
        write_frozen_json(root / "00_CANDIDATE_MANIFEST.json", {"candidates": candidate_manifest(candidates)})
    else:
        candidates = _load_candidates(args.candidate_manifest)

    selection = deterministic_select_virgins(candidates, protocol_seed=args.protocol_seed)
    write_frozen_json(root / "01_VIRGIN_SELECTION.json", selection)
    print(json.dumps(selection, indent=2, sort_keys=True))
    if args.select_only:
        return 0
    raise EquivalenceProtocolError(
        "virgin derivation and selection are implemented and frozen; paid arm execution remains blocked until "
        "the frozen Direct-Sol and Gemini+bounded-Sol workflow adapters are bound and tested"
    )


if __name__ == "__main__":
    raise SystemExit(main())
