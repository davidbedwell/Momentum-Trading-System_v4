from __future__ import annotations

import argparse
import json
from pathlib import Path

from .adapters import CSVAdapter
from .engine import IntakeEngine
from .filesystem_stage import stage_for_publication
from .models import IntakeRequest, MaterializationMode, MaterializationPolicy


def main() -> int:
    parser = argparse.ArgumentParser(description="MTS v2 Intake Engine")
    parser.add_argument("csv", type=Path)
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--timeframe", default="1D")
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument(
        "--mode",
        choices=[x.value for x in MaterializationMode],
        default=MaterializationMode.ACTIVE_FAMILIES.value,
    )
    args = parser.parse_args()

    policy = MaterializationPolicy(mode=MaterializationMode(args.mode))
    request = IntakeRequest(
        symbol=args.symbol,
        timeframe=args.timeframe,
        policy=policy,
        requested_by="CLI",
    )
    artifact = IntakeEngine().process(
        CSVAdapter(args.csv, source_id=args.source_id),
        request,
    )
    stage_for_publication(artifact, args.stage)
    print(json.dumps(artifact.manifest, indent=2, default=str))
    print("Transient package staged. Nexus publication still required.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
