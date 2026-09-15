from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path

from MTS_V4.analysis import ExactMethodAnalysisExecutor
from MTS_V4.cache import TemporaryResearchCache
from MTS_V4.derived_market_evidence import derived_market_evidence_descriptor, universe_subject
from MTS_V4.derived_market_store import DerivedMarketQuery, ParquetDerivedMarketStore
from MTS_V4.universe_market_structure_substrate import (
    analysis_method,
    build_for_universe,
    required_feature_columns,
)
from MTS_V4.universe_membership import load_membership_csv


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build predictor-only neutral full-universe market-structure Analysis output."
    )
    parser.add_argument("--derived-market-root", required=True)
    parser.add_argument("--universe-id", required=True)
    parser.add_argument("--membership-csv", required=True)
    parser.add_argument("--feature-set-id", default="mts_market_predictors")
    parser.add_argument("--feature-set-version", default="v1")
    parser.add_argument("--start-date", default=None)
    parser.add_argument("--as-of-date", default=None)
    parser.add_argument("--output", required=True)
    return parser


def _write_new(path: Path, payload: object) -> None:
    if path.exists():
        raise RuntimeError(f"refusing to replace frozen Stage 2A artifact: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n"
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(encoded, encoding="utf-8")
    temporary.replace(path)


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    output = Path(args.output).expanduser().resolve()
    if output.exists():
        raise RuntimeError(f"refusing to replace frozen Stage 2A artifact: {output}")
    store = ParquetDerivedMarketStore(Path(args.derived_market_root).expanduser().resolve())
    universe = store.get_universe(args.universe_id)
    if universe is None:
        raise RuntimeError(f"derived market store does not contain universe: {args.universe_id}")
    feature_set = store.get_feature_set(args.feature_set_id, args.feature_set_version)
    if feature_set is None:
        raise RuntimeError(f"unknown feature set: {args.feature_set_id}:{args.feature_set_version}")
    required = required_feature_columns()
    missing = sorted(set(required).difference(feature_set.feature_columns))
    if missing:
        raise RuntimeError(f"predictor feature set cannot supply comprehensive Stage 2A input: {missing}")

    membership = load_membership_csv(args.membership_csv)
    attributes: dict[str, dict[str, object]] = {}
    for interval in membership.intervals():
        attributes[interval.security_id] = {
            "ticker": interval.ticker,
            "sector_id": interval.sector_id,
            "industry_id": interval.industry_id,
        }

    query = DerivedMarketQuery(
        universe_id=args.universe_id,
        feature_set_id=args.feature_set_id,
        feature_set_version=args.feature_set_version,
        start_date=args.start_date,
        end_date=args.as_of_date,
        feature_columns=required,
    )
    print("STAGE2A_PHASE=READ_PREDICTOR_PANEL", flush=True)
    cache = TemporaryResearchCache()
    subject = universe_subject(universe_id=args.universe_id, display_ticker=args.universe_id.upper())
    descriptor = derived_market_evidence_descriptor(
        store=store, cache=cache, subject=subject, query=query, allow_future_outcomes=False
    )
    print(f"STAGE2A_INPUT_ROWS={descriptor.row_count}", flush=True)
    print("STAGE2A_PHASE=COMPUTE_NEUTRAL_MARKET_STRUCTURE", flush=True)
    analysis = ExactMethodAnalysisExecutor()
    analysis.register(analysis_method())
    result = next(iter(build_for_universe(
        subject=subject,
        evidence=(descriptor,),
        cache=cache,
        analysis=analysis,
        as_of_date=args.as_of_date,
        security_attributes=attributes,
    ).values()))
    compact_outputs = dict(result.outputs)
    reusable = compact_outputs.pop("derived_datasets", {})
    coverage = compact_outputs["coverage"]
    if coverage["current_attribute_labels_available"] != coverage["latest_security_count"]:
        raise RuntimeError(
            "membership evidence did not label every security in the latest market cross-section: "
            f"labels={coverage['current_attribute_labels_available']} "
            f"securities={coverage['latest_security_count']}"
        )
    if coverage["current_sector_labels_available"] != coverage["latest_security_count"]:
        raise RuntimeError(
            "membership evidence did not provide a sector label for every latest security: "
            f"labels={coverage['current_sector_labels_available']} "
            f"securities={coverage['latest_security_count']}"
        )
    artifact = {
        "format": "MTS_V4_NEUTRAL_UNIVERSE_MARKET_STRUCTURE_STAGE2A_V1",
        "universe": asdict(universe),
        "query": asdict(query),
        "evidence": asdict(descriptor.durable_metadata()),
        "analysis": {
            "result_id": result.result_id,
            "request_id": result.request_id,
            "method_id": result.method_id,
            "limitations": list(result.limitations),
            "execution_metadata": dict(result.execution_metadata),
            "outputs": compact_outputs,
        },
        "reusable_dataset_row_counts": {
            name: len(rows) for name, rows in reusable.items() if isinstance(rows, (list, tuple))
        },
        "storage_policy": {
            "large_reproducible_analysis_rows_persisted": False,
            "source_derived_market_store_unchanged": True,
            "compact_analytics_and_metadata_only": True,
        },
        "sol_calls": 0,
    }
    canonical = json.dumps(artifact, sort_keys=True, default=str, separators=(",", ":"))
    artifact["artifact_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    print("STAGE2A_PHASE=WRITE_COMPACT_ARTIFACT", flush=True)
    _write_new(output, artifact)
    print(f"STAGE2A_OUTPUT={output}", flush=True)
    print(f"STAGE2A_EFFECTIVE_AS_OF={compact_outputs['observation_clock']['effective_as_of_date']}", flush=True)
    print(f"STAGE2A_LATEST_SECURITIES={compact_outputs['coverage']['latest_security_count']}", flush=True)
    print("STAGE2A_STATUS=PASS", flush=True)
    print("SOL_CALLS=0", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
