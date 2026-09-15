from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

from MTS_V4.cache import TemporaryResearchCache
from MTS_V4.intake import IntakeEngine
from MTS_V4.research_scope import universe_scope
from MTS_V4.universe_sources import CurrentSp500CalibrationUniverseSource


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Acquire and freeze current S&P 500 universe evidence through the MTS v4 Intake Engine.")
    parser.add_argument("--universe-id", required=True)
    parser.add_argument("--as-of-date", required=True)
    parser.add_argument("--acquisition-floor", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)

    subject = universe_scope(args.universe_id).to_subject_metadata(display_ticker=args.universe_id.upper())
    cache = TemporaryResearchCache()
    intake = IntakeEngine(cache)
    descriptors = intake.ingest(
        subject=subject,
        source=CurrentSp500CalibrationUniverseSource(
            as_of_date=args.as_of_date,
            acquisition_floor=args.acquisition_floor,
        ),
    )
    if len(descriptors) != 1:
        raise RuntimeError(f"expected one universe membership artifact; received {len(descriptors)}")
    descriptor = descriptors[0]
    rows = cache.get(descriptor.cache_key)

    output = Path(args.output).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise RuntimeError(f"refusing to replace frozen Intake evidence: {output}")
    fields = ["security_id", "ticker", "start_date", "end_date", "sector_id", "industry_id", "source_identity"]
    temporary = output.with_suffix(output.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(output)
    payload = output.read_bytes()
    audit = {
        "format": "MTS_V4_INTAKE_UNIVERSE_ACQUISITION_V1",
        "universe_id": args.universe_id,
        "evidence_id": descriptor.evidence_id,
        "evidence_type": descriptor.evidence_type,
        "source_identity": descriptor.source_identity,
        "content_identity": descriptor.content_identity,
        "coverage_start": descriptor.coverage_start,
        "coverage_end": descriptor.coverage_end,
        "row_count": descriptor.row_count,
        "schema": list(descriptor.schema),
        "provenance": dict(descriptor.provenance),
        "neutral_semantics": descriptor.neutral_semantics,
        "membership_csv": str(output),
        "membership_csv_sha256": hashlib.sha256(payload).hexdigest(),
    }
    audit_path = output.with_suffix(".audit.json")
    audit_path.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    cache.release(descriptor.cache_key)
    cache.purge_released()
    print(json.dumps(audit, indent=2, sort_keys=True))
    print("INTAKE_ENGINE_USED=True")
    print("MARKET_DOWNLOADS=0")
    print("SOL_CALLS=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
