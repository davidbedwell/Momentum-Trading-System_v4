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
from MTS_V4.contracts import ResearchPhase, SubjectMetadata
from MTS_V4.context_enriched_revisit import build_context_enriched_revisit_evidence
from MTS_V4.control_readiness import require_calibration_pass
from MTS_V4.intake import IntakeEngine
from MTS_V4.derived_market_store import ParquetDerivedMarketStore
from MTS_V4.market_reading_calibration import load_market_reading_assessment
from MTS_V4.pre_sol_substrates import build_for_subject as build_pre_sol_substrates
from MTS_V4.research_lead_sources import standard_research_lead_market_source
from MTS_V4.research_package_store import JsonResearchPackageStore
from MTS_V4.sol_spend_guard import (
    DEFAULT_AUTHORIZED_SOL_SPEND_USD,
    SolSpendAuthorizationRequired,
    SolSpendAuthorizationSnapshot,
)
from MTS_V4.subject_scientific_context import (
    SubjectContextSolBatchResearchDirector,
    load_subject_scientific_context,
)
from MTS_V4.universe_membership import load_membership_csv
from MTS_V4.universe_scientific_partition import ScientificCohort, load_frozen_partition


CONTEXT_ENRICHED_REVISIT_QUESTION = (
    "Since your prior analysis of this ticker, the available evidence and governing evaluation "
    "standards have changed. You now have time-aligned market, current-sector, breadth, volatility, "
    "participation, dispersion, and cross-sectional context that was not available during the prior "
    "analysis. Trading-hypothesis candidacy, scientific validation, and trading-promotion eligibility "
    "are now governed separately using executable policy, chronological path, adverse risk, costs, and "
    "expectancy. Do any of these changes affect your previous analyses, recommendations, findings, "
    "hypotheses, unresolved questions, or conclusions for this ticker?"
)

CONTEXT_ENRICHED_CANDIDACY_CHANGE = {
    "observation_vs_candidate": (
        "A predictive relationship may remain a scientific observation or supporting finding without "
        "being designated a candidate trading hypothesis."
    ),
    "candidate_requirement": (
        "Trading-hypothesis candidacy requires exploratory evidence supporting a specific, "
        "non-duplicative, falsifiable relationship between information observable at T and subsequent "
        "market behavior, plus a proposed human-executable policy with positive estimated net expectancy "
        "after estimated all-in costs."
    ),
    "executable_policy_scope": (
        "The proposed policy must specify observable entry, direction and instrument, prediction point, "
        "favorable outcome, adverse-risk unit, stop or invalidation, favorable exit, maximum horizon, "
        "gap/fill treatment, position management, costs, and applicable population or regime. Outcomes "
        "must be applied chronologically and no movement after policy exit may be credited."
    ),
    "no_universal_candidate_threshold": (
        "No universal success-rate, ATR-movement, or payoff threshold governs candidacy. The former "
        "greater-than-60-percent success at at-least-1.5-ATR standard is not the candidate definition."
    ),
    "later_scientific_validation": (
        "Scientific validation is separate and uses untouched evidence, a frozen policy, an appropriate "
        "predeclared uncertainty assessment, and a lower bound for path-executable net expectancy above zero."
    ),
    "later_trading_promotion": (
        "Only after scientific validation does candidacy for prospective paper testing require conservative "
        "net expectancy greater than zero, point-estimate net expectancy at least 0.15R, and point-estimate "
        "gross expectancy at least twice upper-bound all-in costs. These are rejection floors, not research targets."
    ),
    "identity": (
        "A material revision to a prior frozen proposition or policy requires a new hypothesis identity; "
        "historical records remain unchanged."
    ),
}


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
            "Run one live MTS v4 subject through the batched Sol Research Director path with permanent "
            "cross-subject scientific memory/frontier and prior durable subject science."
        )
    )
    parser.add_argument("--ticker", required=True, help="equity ticker, e.g. AMD")
    parser.add_argument("--root", default="/home/ubuntu")
    parser.add_argument("--state-dir", default=None)
    parser.add_argument(
        "--revisit",
        action="store_true",
        help=(
            "explicitly revisit a previously researched ticker and expose its compact durable "
            "same-subject science to Sol as nonbinding historical context"
        ),
    )
    parser.add_argument("--context-enriched-revisit", action="store_true")
    parser.add_argument("--derived-market-root", default=None)
    parser.add_argument("--universe-id", default=None)
    parser.add_argument("--membership-csv", default=None)
    parser.add_argument("--predictor-feature-set-id", default="mts_market_predictors")
    parser.add_argument("--predictor-feature-set-version", default="v1")
    parser.add_argument("--outcome-feature-set-id", default="mts_historical_outcomes")
    parser.add_argument("--outcome-feature-set-version", default="v1")
    parser.add_argument("--market-reading-calibration", default=None)
    parser.add_argument(
        "--scientific-partition-manifest",
        default=None,
        help=(
            "required for a context-enriched revisit; the ticker must belong to the frozen "
            "DISCOVERY cohort before historical outcomes are exposed"
        ),
    )
    parser.add_argument(
        "--sol-spend-limit-usd",
        type=float,
        default=DEFAULT_AUTHORIZED_SOL_SPEND_USD,
        help=(
            "initial human authorization for Sol API spend for this subject; default is $20. "
            "When Sol's own remaining-work estimate projects more spend, the runner stops before "
            "the next Sol call and requests human authorization for a higher dollar ceiling."
        ),
    )
    parser.add_argument(
        "--control-campaign-report",
        default=None,
        help="required complete CALIBRATION_PASS report before any new paid single-subject discovery",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="validate CLI/configuration and scientific context without Intake or Sol API calls",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    ticker = args.ticker.strip().upper()
    if not ticker:
        raise RuntimeError("ticker cannot be blank")
    if args.sol_spend_limit_usd <= 0:
        raise RuntimeError("--sol-spend-limit-usd must be positive")
    if args.context_enriched_revisit and not args.revisit:
        raise RuntimeError("--context-enriched-revisit requires --revisit")
    if args.context_enriched_revisit:
        required_context = {
            "--derived-market-root": args.derived_market_root,
            "--universe-id": args.universe_id,
            "--membership-csv": args.membership_csv,
            "--market-reading-calibration": args.market_reading_calibration,
            "--scientific-partition-manifest": args.scientific_partition_manifest,
        }
        missing = [name for name, value in required_context.items() if not value]
        if missing:
            raise RuntimeError(f"context-enriched revisit missing required options: {missing}")
    if not args.dry_run:
        if not args.control_campaign_report:
            raise RuntimeError(
                "new paid single-subject discovery is gated until --control-campaign-report records CALIBRATION_PASS"
            )
        require_calibration_pass(args.control_campaign_report)

    root = Path(args.root).expanduser().resolve()
    subject = SubjectMetadata(subject_id=f"equity:{ticker}", ticker=ticker)
    scientific_context = load_subject_scientific_context(
        root,
        active_subject_id=subject.subject_id,
        include_same_subject_prior_science=args.revisit,
    )
    prior_package_count = sum(
        len(item.get("research_packages", []))
        for item in scientific_context.prior_subject_science.get("subjects", [])
        if isinstance(item, dict)
    )
    same_subject_package_count = len(
        scientific_context.same_subject_prior_science.get("research_packages", [])
    ) if scientific_context.same_subject_prior_science is not None else 0
    same_subject_nexus_finding_count = len(
        scientific_context.same_subject_prior_science.get("nexus_only_findings", [])
    ) if scientific_context.same_subject_prior_science is not None else 0
    market_reading = None
    scientific_partition = None
    context_security_id = None
    context_sector_id = None
    context_security_sector_ids = None
    context_store = None
    if args.context_enriched_revisit:
        market_reading = load_market_reading_assessment(
            Path(args.market_reading_calibration).expanduser().resolve()
        )
        scientific_partition = load_frozen_partition(
            Path(args.scientific_partition_manifest).expanduser().resolve()
        )
        if scientific_partition.universe_id != args.universe_id:
            raise RuntimeError("scientific partition universe does not match --universe-id")
        membership = load_membership_csv(Path(args.membership_csv).expanduser().resolve())
        ticker_matches = [
            item for item in membership.intervals() if item.ticker.upper() == ticker
        ]
        security_ids = {item.security_id for item in ticker_matches}
        if len(security_ids) != 1:
            raise RuntimeError(f"expected exactly one calibration security identity for {ticker}")
        context_security_id = next(iter(security_ids))
        if context_security_id not in scientific_partition.members(ScientificCohort.DISCOVERY):
            raise RuntimeError(
                "context-enriched exploratory outcome access is restricted to DISCOVERY: "
                f"{context_security_id}"
            )
        context_sector_id = next(
            (str(item.sector_id) for item in ticker_matches if item.sector_id),
            "UNCLASSIFIED",
        )
        context_security_sector_ids = {
            item.security_id: str(item.sector_id or "UNCLASSIFIED")
            for item in membership.intervals()
        }
        context_store = ParquetDerivedMarketStore(
            Path(args.derived_market_root).expanduser().resolve()
        )
        if context_store.get_universe(args.universe_id) is None:
            raise RuntimeError(f"derived market store does not contain universe: {args.universe_id}")
        for feature_id, version in (
            (args.predictor_feature_set_id, args.predictor_feature_set_version),
            (args.outcome_feature_set_id, args.outcome_feature_set_version),
        ):
            if context_store.get_feature_set(feature_id, version) is None:
                raise RuntimeError(f"derived market store does not contain feature set: {feature_id}:{version}")
    revisit_change_context = None
    if args.context_enriched_revisit:
        revisit_change_context = {
            "human_scientific_question": CONTEXT_ENRICHED_REVISIT_QUESTION,
            "new_evidence": (
                "Time-aligned ticker, full-current-member-universe, and current-sector predictor context "
                "at each historical daily T; historical ticker outcomes remain explicitly exploratory."
            ),
            "governance_change": (
                "Trading-hypothesis candidacy, scientific validation, and trading-promotion eligibility "
                "are distinct and use executable chronological policy, adverse risk, costs, and expectancy."
            ),
            "candidate_characterization_change": CONTEXT_ENRICHED_CANDIDACY_CHANGE,
            "scientific_authority": (
                "Sol determines whether the changes affect any prior analysis, recommendation, finding, "
                "hypothesis, unresolved question, or conclusion. Deterministic code imposes no retest list."
            ),
            "current_market_reading": {
                "effective_scope": "CURRENT_APPLICABILITY_CONTEXT_ONLY_NOT_HISTORICAL_EVIDENCE",
                "source_sha256": market_reading["artifact_sha256"],
                "assessment": market_reading["assessment"],
            },
        }

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    state_dir = Path(args.state_dir or f"/home/ubuntu/mts-v4-sol-batched-{ticker.lower()}-{stamp}")
    frontier = scientific_context.memory_selection.store.frontier()
    if args.dry_run:
        print(f"DRY_RUN=True")
        print(f"TICKER={ticker}")
        print(f"STATE_DIR={state_dir}")
        print(f"SOL_SPEND_LIMIT_USD={args.sol_spend_limit_usd:.2f}")
        print(f"CANONICAL_MEMORY_SOURCE={scientific_context.memory_selection.source_path}")
        print(f"CANONICAL_MEMORY_RECORDS={len(scientific_context.memory_selection.store.records())}")
        print(f"CANONICAL_MEMORY_FRONTIER_VERSION={frontier.version if frontier is not None else 0}")
        print(f"PRIOR_SUBJECT_SCIENTIFIC_PACKAGES={prior_package_count}")
        print(f"REVISIT_MODE={args.revisit}")
        print(f"SAME_SUBJECT_SCIENTIFIC_PACKAGES={same_subject_package_count}")
        print(f"SAME_SUBJECT_NEXUS_ONLY_FINDINGS={same_subject_nexus_finding_count}")
        print(f"CONTEXT_ENRICHED_REVISIT={args.context_enriched_revisit}")
        if args.context_enriched_revisit:
            print(f"REVISIT_QUESTION={CONTEXT_ENRICHED_REVISIT_QUESTION}")
            print(f"MARKET_READING_CALIBRATION_SHA256={market_reading['artifact_sha256']}")
            print(f"SCIENTIFIC_PARTITION_ID={scientific_partition.partition_id}")
            print(f"REQUIRED_OUTCOME_COHORT={ScientificCohort.DISCOVERY.value}")
            print(f"SECURITY_ID={context_security_id}")
        print("CROSS_SUBJECT_CONTEXT_AUTOMATIC=True")
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
        revisit_change_context=revisit_change_context,
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
        scientific_memory=scientific_context.memory_selection.store,
    )
    evidence = IntakeEngine(runtime.cache).ingest(
        subject=subject,
        source=standard_research_lead_market_source(),
    )
    if args.context_enriched_revisit:
        contextual_evidence = build_context_enriched_revisit_evidence(
            store=context_store,
            cache=runtime.cache,
            subject=subject,
            universe_id=args.universe_id,
            security_id=context_security_id,
            sector_id=context_sector_id,
            security_sector_ids=context_security_sector_ids,
            predictor_feature_set_id=args.predictor_feature_set_id,
            predictor_feature_set_version=args.predictor_feature_set_version,
            outcome_feature_set_id=args.outcome_feature_set_id,
            outcome_feature_set_version=args.outcome_feature_set_version,
        )
        evidence = tuple(evidence) + contextual_evidence
    campaign_id = f"mts-v4-sol-batched-{ticker.lower()}-{stamp}"
    precomputed_results = dict(build_pre_sol_substrates(
        subject=subject,
        evidence=evidence,
        cache=runtime.cache,
        analysis=runtime.analysis,
    ))

    (state_dir / "subject_scientific_context.json").write_text(
        json.dumps(
            {
                "active_subject_id": subject.subject_id,
                "mode": "REVISIT" if args.revisit else "FRESH_FULL_SUBJECT",
                "mission": DEFAULT_MISSION,
                "canonical_memory_source": str(scientific_context.memory_selection.source_path),
                "canonical_memory_superseded_paths": [
                    str(path) for path in scientific_context.memory_selection.superseded_paths
                ],
                "canonical_memory_frontier_version": frontier.version if frontier is not None else 0,
                "canonical_memory_record_count": len(scientific_context.memory_selection.store.records()),
                "prior_subject_scientific_context": scientific_context.prior_subject_science,
                "revisit_mode": args.revisit,
                "same_subject_prior_science": scientific_context.same_subject_prior_science,
                "revisit_change_context": revisit_change_context,
                "scientific_partition_id": (
                    scientific_partition.partition_id if scientific_partition is not None else None
                ),
                "historical_outcome_cohort": (
                    ScientificCohort.DISCOVERY.value if scientific_partition is not None else None
                ),
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
            precomputed_results=precomputed_results,
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
        "subject_id": subject.subject_id,
        "cross_subject_context_automatic": True,
        "canonical_cross_subject_memory_source": str(scientific_context.memory_selection.source_path),
        "canonical_cross_subject_memory_record_count": len(scientific_context.memory_selection.store.records()),
        "canonical_cross_subject_frontier_version": frontier.version if frontier is not None else 0,
        "prior_subject_scientific_packages_exposed": prior_package_count,
        "revisit_mode": args.revisit,
        "same_subject_scientific_packages_exposed": same_subject_package_count,
        "same_subject_nexus_only_findings_exposed": same_subject_nexus_finding_count,
        "decisions": outcome.decisions,
        "batches_executed": outcome.batches_executed,
        "analyses_executed": outcome.analyses_executed,
        "pre_sol_analysis_substrate_count": len(precomputed_results),
        "pre_sol_analysis_substrate_ids": sorted(precomputed_results),
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
    print(f"SUBJECT={subject.subject_id}", flush=True)
    print("CROSS_SUBJECT_CONTEXT_AUTOMATIC=True", flush=True)
    print(f"PRIOR_SUBJECT_SCIENTIFIC_PACKAGES={prior_package_count}", flush=True)
    print(f"REVISIT_MODE={args.revisit}", flush=True)
    print(f"SAME_SUBJECT_SCIENTIFIC_PACKAGES={same_subject_package_count}", flush=True)
    print(f"SAME_SUBJECT_NEXUS_ONLY_FINDINGS={same_subject_nexus_finding_count}", flush=True)
    print(f"DECISIONS={outcome.decisions}", flush=True)
    print(f"BATCHES={outcome.batches_executed}", flush=True)
    print(f"ANALYSES={outcome.analyses_executed}", flush=True)
    print(f"PRE_SOL_ANALYSIS_SUBSTRATE_COUNT={len(precomputed_results)}", flush=True)
    print(f"PRE_SOL_ANALYSIS_SUBSTRATE_IDS={','.join(sorted(precomputed_results))}", flush=True)
    print(f"CLOSED={outcome.closed}", flush=True)
    print(f"CLOSE_REASON={outcome.close_reason}", flush=True)
    if spend is not None:
        print(f"SOL_SPEND_USD={spend.actual_spend_usd:.4f}", flush=True)
        print(f"SOL_AUTHORIZED_USD={spend.authorized_spend_usd:.2f}", flush=True)
    print(f"SOL_TELEMETRY={state_dir / 'sol_transport_telemetry.jsonl'}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
