from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path

from MTS_V4.batch_contracts import BatchExecutionReport
from MTS_V4.batch_research_recording import BatchCampaignResearchRecorder
from MTS_V4.bootstrap import DEFAULT_MISSION, build_batch_runtime
from MTS_V4.contracts import ResearchPhase
from MTS_V4.derived_market_evidence import derived_market_evidence_descriptor
from MTS_V4.derived_market_store import DerivedMarketQuery, ParquetDerivedMarketStore
from MTS_V4.research_package_store import JsonResearchPackageStore
from MTS_V4.research_scope import universe_scope
from MTS_V4.sol_spend_guard import (
    DEFAULT_AUTHORIZED_SOL_SPEND_USD,
    SolSpendAuthorizationRequired,
    SolSpendAuthorizationSnapshot,
)
from MTS_V4.subject_scientific_context import (
    SubjectContextSolBatchResearchDirector,
    load_subject_scientific_context,
)


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"required environment variable is not set: {name}")
    return value


def _append_jsonl(path: Path, payload) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True, default=str, separators=(",", ":")) + "\n")


def _write_json_atomic(path: Path, payload) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _format_money(value: float | None) -> str:
    return "unknown" if value is None else f"${value:.2f}"


def _interactive_spend_authorization(snapshot: SolSpendAuthorizationSnapshot) -> float | None:
    print("\nHUMAN SOL SPEND AUTHORIZATION REQUIRED", flush=True)
    print(f"AUTHORIZED={_format_money(snapshot.authorized_spend_usd)}", flush=True)
    print(f"ACTUAL_SPEND={_format_money(snapshot.actual_spend_usd)}", flush=True)
    print(f"SOL_CALLS_COMPLETED={snapshot.completed_sol_calls}", flush=True)
    print(f"ESTIMATED_PERCENT_COMPLETE={snapshot.estimated_percent_complete}", flush=True)
    print(f"ESTIMATED_REMAINING_BATCHES={snapshot.estimated_remaining_batches}", flush=True)
    print(f"ESTIMATED_REMAINING_SOL_CALLS={snapshot.estimated_remaining_sol_calls}", flush=True)
    print(
        "ESTIMATED_ADDITIONAL_SPEND="
        f"{_format_money(snapshot.estimated_additional_spend_low_usd)}-"
        f"{_format_money(snapshot.estimated_additional_spend_high_usd)}",
        flush=True,
    )
    print(
        "ESTIMATED_TOTAL_SPEND="
        f"{_format_money(snapshot.estimated_total_spend_low_usd)}-"
        f"{_format_money(snapshot.estimated_total_spend_high_usd)}",
        flush=True,
    )
    print(f"ESTIMATE_CONFIDENCE={snapshot.estimate_confidence}", flush=True)
    print(f"ESTIMATE_RATIONALE={snapshot.estimate_rationale}", flush=True)
    print(
        f"RECOMMENDED_NEW_CEILING={_format_money(snapshot.recommended_authorized_ceiling_usd)}",
        flush=True,
    )
    try:
        raw = input(
            "Enter a new total Sol spend ceiling in USD to authorize more, or press Enter to stop: "
        ).strip()
    except (EOFError, OSError):
        return None
    if not raw:
        return None
    try:
        value = float(raw)
    except ValueError:
        print("Authorization was not numeric; stopping before another Sol call.", flush=True)
        return None
    if value <= snapshot.authorized_spend_usd:
        print("New authorization must exceed the current ceiling; stopping.", flush=True)
        return None
    return value


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run one explicit universe-level MTS v4 research scope through the batched Sol Research "
            "Director path using a requested slice of the persistent Nexus-derived market store."
        )
    )
    parser.add_argument("--universe-id", required=True)
    parser.add_argument("--feature-set-id", required=True)
    parser.add_argument("--feature-set-version", required=True)
    parser.add_argument("--start-date", default=None)
    parser.add_argument("--end-date", default=None)
    parser.add_argument(
        "--security-id",
        action="append",
        default=[],
        help="optional stable security ID filter; repeat for multiple securities",
    )
    parser.add_argument(
        "--feature-column",
        action="append",
        default=[],
        help="optional exact derived feature column; repeat for multiple features",
    )
    parser.add_argument("--root", default="/home/ubuntu")
    parser.add_argument(
        "--derived-market-root",
        default=None,
        help="persistent Nexus-derived market directory; defaults to <root>/mts-v4-nexus-derived-market",
    )
    parser.add_argument("--state-dir", default=None)
    parser.add_argument(
        "--sol-spend-limit-usd",
        type=float,
        default=DEFAULT_AUTHORIZED_SOL_SPEND_USD,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="validate store/query/context without Sol API calls",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    universe_id = args.universe_id.strip()
    if not universe_id:
        raise RuntimeError("universe-id cannot be blank")
    if args.sol_spend_limit_usd <= 0:
        raise RuntimeError("--sol-spend-limit-usd must be positive")

    root = Path(args.root).expanduser().resolve()
    derived_market_root = Path(
        args.derived_market_root or (root / "mts-v4-nexus-derived-market")
    ).expanduser().resolve()
    subject = universe_scope(universe_id).to_subject_metadata(display_ticker=universe_id.upper())
    query = DerivedMarketQuery(
        universe_id=universe_id,
        feature_set_id=args.feature_set_id.strip(),
        feature_set_version=args.feature_set_version.strip(),
        start_date=args.start_date,
        end_date=args.end_date,
        security_ids=tuple(args.security_id),
        feature_columns=tuple(args.feature_column),
    )

    store = ParquetDerivedMarketStore(derived_market_root)
    universe = store.get_universe(universe_id)
    if universe is None:
        raise RuntimeError(f"derived market store does not contain universe: {universe_id}")
    feature_set = store.get_feature_set(query.feature_set_id, query.feature_set_version)
    if feature_set is None:
        raise RuntimeError(f"derived market store does not contain feature set: {query.feature_set_key}")
    store_state = store.state(universe_id, query.feature_set_id, query.feature_set_version)

    scientific_context = load_subject_scientific_context(
        root,
        active_subject_id=subject.subject_id,
        include_same_subject_prior_science=True,
    )
    frontier = scientific_context.memory_selection.store.frontier()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    state_dir = Path(
        args.state_dir or f"/home/ubuntu/mts-v4-sol-batched-universe-{universe_id.lower()}-{stamp}"
    )

    if args.dry_run:
        rows = store.query(query)
        print("DRY_RUN=True")
        print(f"RESEARCH_SCOPE={subject.subject_id}")
        print(f"UNIVERSE_ID={universe_id}")
        print(f"FEATURE_SET={query.feature_set_key}")
        print(f"DERIVED_MARKET_ROOT={derived_market_root}")
        print(f"HIGH_WATER_MARK={store_state.high_water_mark}")
        print(f"QUERY_ROW_COUNT={len(rows)}")
        print(f"QUERY_FEATURE_COLUMNS={','.join(query.feature_columns or feature_set.feature_columns)}")
        print(f"STATE_DIR={state_dir}")
        print("SOL_CALLS=0")
        return 0

    state_dir.mkdir(parents=True, exist_ok=False)
    os.environ.setdefault(
        "MTS_SOL_TELEMETRY_PATH",
        str(state_dir / "sol_transport_telemetry.jsonl"),
    )
    package_store = JsonResearchPackageStore(state_dir / "research_packages")
    recorder = BatchCampaignResearchRecorder(package_store=package_store)
    rd = SubjectContextSolBatchResearchDirector(
        research_package_store=package_store,
        prior_subject_scientific_context=scientific_context.prior_subject_science,
        same_subject_prior_scientific_context=scientific_context.same_subject_prior_science,
        base_url=_required_env("MTS_SOL_BASE_URL"),
        model=_required_env("MTS_SOL_MODEL"),
        api_key=_required_env("MTS_SOL_API_KEY"),
        timeout_seconds=int(os.getenv("MTS_SOL_TIMEOUT_SECONDS", "600")),
        required_subject_id=subject.subject_id,
        required_research_phase=ResearchPhase.EXPLORATION,
        sol_spend_limit_usd=args.sol_spend_limit_usd,
        human_spend_authorization_callback=_interactive_spend_authorization,
    )
    runtime = build_batch_runtime(
        rd=rd,
        mission=DEFAULT_MISSION,
        nexus_path=state_dir / "research_nexus.json",
        derived_market_root=derived_market_root,
        scientific_memory=scientific_context.memory_selection.store,
    )
    evidence = (
        derived_market_evidence_descriptor(
            store=runtime.nexus.derived_market_store,
            cache=runtime.cache,
            subject=subject,
            query=query,
        ),
    )
    campaign_id = f"mts-v4-sol-batched-universe-{universe_id.lower()}-{stamp}"

    (state_dir / "universe_scientific_context.json").write_text(
        json.dumps(
            {
                "active_scope_id": subject.subject_id,
                "scope_type": "UNIVERSE",
                "mission": DEFAULT_MISSION,
                "universe_definition": asdict(universe),
                "derived_market_query": asdict(query),
                "derived_market_high_water_mark": store_state.high_water_mark,
                "canonical_memory_source": str(scientific_context.memory_selection.source_path),
                "canonical_memory_frontier_version": frontier.version if frontier is not None else 0,
            },
            sort_keys=True,
            indent=2,
            default=str,
        ) + "\n",
        encoding="utf-8",
    )

    decision_path = state_dir / "batch_decisions.jsonl"
    report_path = state_dir / "batch_reports.jsonl"
    pending_decision_path = state_dir / "pending_batch_decision.json"
    latest_report: BatchExecutionReport | None = None

    def accepted(request):
        recorder.record_accepted_request(
            campaign_id=campaign_id,
            subject=subject,
            request=request,
        )

    def on_report(report, decisions, analyses):
        nonlocal latest_report
        latest_report = report
        recorder.record_report(report)
        _append_jsonl(
            report_path,
            {
                "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
                "decisions": decisions,
                "analyses_executed": analyses,
                "report": asdict(report),
            },
        )

    def on_decision(decision, decisions, analyses):
        _write_json_atomic(
            pending_decision_path,
            {
                "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
                "decision_sequence": decisions,
                "analyses_executed": analyses,
                "decision": asdict(decision),
            },
        )
        recorder.record_plan(
            campaign_id=campaign_id,
            subject=subject,
            decision=decision,
        )
        recorder.record_predictive_hypothesis_updates(
            decision,
            current_report=latest_report,
        )
        recorder.record_closures(decision)
        _append_jsonl(
            decision_path,
            {
                "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
                "decision_sequence": decisions,
                "analyses_executed": analyses,
                "decision": asdict(decision),
            },
        )
        pending_decision_path.unlink()

    try:
        outcome = runtime.orchestrator.run(
            subject=subject,
            evidence=evidence,
            decision_callback=on_decision,
            report_callback=on_report,
            accepted_request_callback=accepted,
            precomputed_results={},
        )
    except SolSpendAuthorizationRequired as exc:
        artifact = state_dir / "sol_spend_authorization_required.json"
        artifact.write_text(
            json.dumps(asdict(exc.snapshot), sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"STATE_DIR={state_dir}", flush=True)
        print("HUMAN_SOL_SPEND_AUTHORIZATION_REQUIRED=True", flush=True)
        print(f"AUTHORIZATION_ARTIFACT={artifact}", flush=True)
        return 2

    spend = rd.sol_spend_snapshot()
    summary = {
        "campaign_id": campaign_id,
        "scope_id": subject.subject_id,
        "scope_type": "UNIVERSE",
        "universe_id": universe_id,
        "derived_market_root": str(derived_market_root),
        "derived_market_query": asdict(query),
        "derived_market_high_water_mark": store_state.high_water_mark,
        "decisions": outcome.decisions,
        "batches_executed": outcome.batches_executed,
        "analyses_executed": outcome.analyses_executed,
        "findings_promoted": outcome.findings_promoted,
        "closed": outcome.closed,
        "close_reason": outcome.close_reason,
        "sol_spend": asdict(spend) if spend is not None else None,
        "sol_transport_telemetry": str(state_dir / "sol_transport_telemetry.jsonl"),
    }
    (state_dir / "run_summary.json").write_text(
        json.dumps(summary, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"STATE_DIR={state_dir}", flush=True)
    print(f"CAMPAIGN_ID={campaign_id}", flush=True)
    print(f"RESEARCH_SCOPE={subject.subject_id}", flush=True)
    print(f"UNIVERSE_ID={universe_id}", flush=True)
    print(f"FEATURE_SET={query.feature_set_key}", flush=True)
    print(f"DERIVED_MARKET_HIGH_WATER_MARK={store_state.high_water_mark}", flush=True)
    print(f"DECISIONS={outcome.decisions}", flush=True)
    print(f"BATCHES={outcome.batches_executed}", flush=True)
    print(f"ANALYSES={outcome.analyses_executed}", flush=True)
    print(f"CLOSED={outcome.closed}", flush=True)
    print(f"CLOSE_REASON={outcome.close_reason}", flush=True)
    if spend is not None:
        print(f"SOL_SPEND_USD={spend.actual_spend_usd:.4f}", flush=True)
        print(f"SOL_AUTHORIZED_USD={spend.authorized_spend_usd:.2f}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
