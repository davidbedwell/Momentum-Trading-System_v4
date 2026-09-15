from __future__ import annotations

import argparse
import os
from pathlib import Path

from MTS_V4.market_reading_calibration import (
    calibration_messages,
    load_calibration_transport,
    write_calibration_assessment,
)
from MTS_V4.research_package_store import JsonResearchPackageStore
from MTS_V4.sol_provider import SolResearchPackageAwareResearchDirector


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"required environment variable is not set: {name}")
    return value


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Make exactly one bounded Sol call to assess a predictor-only Stage 2A market representation."
    )
    parser.add_argument("--stage2a-transport", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--state-dir", required=True)
    parser.add_argument("--sol-spend-limit-usd", required=True, type=float)
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.sol_spend_limit_usd <= 0:
        raise RuntimeError("--sol-spend-limit-usd must be positive")
    source = Path(args.stage2a_transport).expanduser().resolve()
    output = Path(args.output).expanduser().resolve()
    state_dir = Path(args.state_dir).expanduser().resolve()
    document = load_calibration_transport(source)
    if output.exists():
        raise RuntimeError(f"refusing to replace frozen calibration assessment: {output}")
    if args.dry_run:
        print(f"STAGE2A_TRANSPORT={source}")
        print(f"SOURCE_SHA256={document['artifact_sha256']}")
        print(f"OUTPUT={output}")
        print(f"SOL_SPEND_LIMIT_USD={args.sol_spend_limit_usd:.2f}")
        print("CALIBRATION_CLASS=DESCRIPTIVE_NON_SCIENTIFIC_MARKET_READING")
        print("HISTORICAL_OUTCOMES_CONSUMED=False")
        print("HYPOTHESES_CREATED=False")
        print("FINDINGS_PROMOTED=False")
        print("SOL_CALLS=0")
        print("MARKET_READING_CALIBRATION_PREFLIGHT=PASS")
        return 0

    state_dir.mkdir(parents=True, exist_ok=False)
    os.environ.setdefault("MTS_SOL_TELEMETRY_PATH", str(state_dir / "sol_transport_telemetry.jsonl"))
    model = _required_env("MTS_SOL_MODEL")
    provider = SolResearchPackageAwareResearchDirector(
        research_package_store=JsonResearchPackageStore(state_dir / "unused_research_packages"),
        base_url=_required_env("MTS_SOL_BASE_URL"),
        model=model,
        api_key=_required_env("MTS_SOL_API_KEY"),
        timeout_seconds=int(os.getenv("MTS_SOL_TIMEOUT_SECONDS", "600")),
    )
    provider.configure_sol_spend_guard(authorized_spend_usd=args.sol_spend_limit_usd)
    response = provider._chat_completion(calibration_messages(document))
    snapshot = provider.sol_spend_snapshot()
    estimated_spend = snapshot.actual_spend_usd if snapshot is not None else None
    result = write_calibration_assessment(
        output=output,
        source_path=source,
        source_document=document,
        model=model,
        response=response,
        authorized_spend_usd=args.sol_spend_limit_usd,
        estimated_spend_usd=estimated_spend,
    )
    print(f"MARKET_READING_CALIBRATION_OUTPUT={output}")
    print(f"ARTIFACT_SHA256={result['artifact_sha256']}")
    print("SOL_CALLS=1")
    print(f"ESTIMATED_SOL_SPEND_USD={estimated_spend if estimated_spend is not None else 'UNKNOWN'}")
    print("HISTORICAL_OUTCOMES_CONSUMED=False")
    print("HYPOTHESES_CREATED=False")
    print("FINDINGS_PROMOTED=False")
    print("MARKET_READING_CALIBRATION_STATUS=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
