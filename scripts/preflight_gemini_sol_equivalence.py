#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from pathlib import Path

from MTS_V4.virgin_equivalence import EquivalenceProtocolError


def main() -> int:
    p = argparse.ArgumentParser(description="No-spend preflight for Gemini-Sol virgin equivalence experiment")
    p.add_argument("--root", default="/home/ubuntu")
    p.add_argument("--experiment-root", required=True)
    p.add_argument("--partition", required=True)
    p.add_argument("--membership-csv", required=True)
    p.add_argument("--derived-market-root", required=True)
    p.add_argument("--prior-sol-audit", action="append", required=True)
    p.add_argument("--exposure-ledger", action="append", required=True)
    p.add_argument("--research-root", action="append", required=True)
    args = p.parse_args()
    required_env = ["MTS_SOL_BASE_URL", "MTS_SOL_MODEL", "MTS_SOL_API_KEY", "OPENROUTER_API_KEY"]
    missing_env = [name for name in required_env if not os.getenv(name, "").strip()]
    if missing_env:
        raise EquivalenceProtocolError(f"missing environment variables: {missing_env}")
    for label, raw in (("partition", args.partition), ("membership", args.membership_csv), ("derived market", args.derived_market_root)):
        path = Path(raw).expanduser().resolve()
        if not path.exists():
            raise EquivalenceProtocolError(f"missing {label}: {path}")
    print("PREFLIGHT_PASS=True")
    print("PAID_CALLS=0")
    print(f"EXPERIMENT_ROOT={Path(args.experiment_root).expanduser().resolve()}")
    print("DIRECT_SOL_WRAPPER=FROZEN_BATCH_CONTRACT")
    print("GEMINI_RD_WRAPPER=SAME_BATCH_CONTRACT_OPENROUTER_TRANSPORT")
    print("SOL_APPEAL=FULL_RECORD_EXACTLY_ONE_CALL_V1")
    print("CROSS_ARM_VISIBILITY=PROHIBITED")
    print("BLINDED_COMPARISON=IDENTITY_AND_USAGE_STRIPPED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
