from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Mapping, Sequence

from MTS_V4.batch_contracts import BatchExecutionReport
from MTS_V4.batch_research_recording import BatchCampaignResearchRecorder
from MTS_V4.bootstrap import DEFAULT_MISSION, build_batch_runtime
from MTS_V4.contracts import ResearchPhase, SubjectMetadata
from MTS_V4.intake import IntakeEngine
from MTS_V4.live_sources import standard_live_market_source
from MTS_V4.research_package_store import JsonResearchPackageStore
from MTS_V4.retrospective_recovery import (
    SolRetrospectiveRecoveryResearchDirector,
    load_retrospective_subject_context,
)
from MTS_V4.sol_spend_guard import (
    DEFAULT_AUTHORIZED_SOL_SPEND_USD,
    SolSpendAuthorizationRequired,
    SolSpendAuthorizationSnapshot,
)
from MTS_V4.subject_scientific_context import load_subject_scientific_context


SEQUENCE = ("AAPL", "MSFT", "XOM")

SEQUENTIAL_RETROSPECTIVE_MISSION = DEFAULT_MISSION + (
    " This is retrospective recovery of a previously exposed subject under the corrected batched Research Director "
    "lifecycle. Historical subject work is discovery context only and is never blind validation. The AI Research "
    "Director also receives compact prior-subject scientific findings and the canonical RD-authored cross-subject "
    "scientific memory/frontier. Use those contexts as nonbinding scientific memory: actively consider transferability, "
    "contradictions, conditional structure, and falsifiable generalization pathways when scientifically useful, but do "
    "not assume that any prior relationship generalizes. Deterministic code does not choose subjects, variables, methods, "
    "thresholds, normalizations, horizons, hypotheses, or generalizations. The AI Research Director retains authority to "
    "test, challenge, reformulate, condition, defer, ignore, or reject prior cross-subject ideas."
)


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"required environment variable is not set: {name}")
    return value


def _append_jsonl(path: Path, payload: object) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True, default=str, separators=(",", ":")) + "\n")


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
    try:
        raw = input("Enter a new total Sol spend ceiling in USD, or press Enter to stop: ").strip()
    except EOFError:
        return None
    if not raw:
        return None
    try:
        value = float(raw)
    except ValueError:
        print("Authorization was not numeric; stopping.", flush=True)
        return None
    if value <= snapshot.authorized_spend_usd:
        print("New authorization must exceed the current ceiling; stopping.", flush=True)
        return None
    return value


def _parse_historical_overrides(values: Sequence[str]) -> dict[str, Path]:
    overrides: dict[str, Path] = {}
    for raw in values:
        ticker, separator, path = raw.partition("=")
        ticker = ticker.strip().upper()
        path = path.strip()
        if not separator or ticker not in SEQUENCE or not path:
            raise ValueError(
                "--historical-subject-dir must use TICKER=/absolute/path for AAPL, MSFT, or XOM"
            )
        if ticker in overrides:
            raise ValueError(f"duplicate historical subject override for {ticker}")
        overrides[ticker] = Path(path).expanduser().resolve()
    return overrides


def _discover_historical_subject_candidates(root: Path, ticker: str) -> tuple[Path, ...]:
    candidates: set[Path] = set()
    patterns = (f"mts-v4-*/subjects/{ticker}", f"mts-v4-*/{ticker}")
    for pattern in patterns:
        for path in root.glob(pattern):
            if not path.is_dir():
                continue
            try:
                load_retrospective_subject_context(path)
            except RuntimeError:
                continue
            candidates.add(path.resolve())
    return tuple(sorted(candidates, key=str))


def _resolve_historical_subject_dir(
    root: Path,
    ticker: str,
    overrides: Mapping[str, Path],
) -> Path:
    explicit = overrides.get(ticker)
    if explicit is not None:
        load_retrospective_subject_context(explicit)
        return explicit
    candidates = _discover_historical_subject_candidates(root, ticker)
    if len(candidates) == 1:
        return candidates[0]
    if not candidates:
        raise RuntimeError(
            f"no usable preserved historical subject directory found for {ticker}; "
            f"supply --historical-subject-dir {ticker}=/absolute/path"
        )
    rendered = "\n  ".join(str(path) for path in candidates)
    raise RuntimeError(
        f"multiple preserved historical subject directories found for {ticker}; deterministic code will not choose "
        f"which scientific history is authoritative. Supply an explicit override:\n  {rendered}"
    )


def _prior_package_count(context: object) -> int:
    if not isinstance(context, Mapping):
        return 0
    return sum(
        len(subject.get("research_packages", []))
        for subject in context.get("subjects", [])
        if isinstance(subject, Mapping)
    )


def _run_subject(
    *,
    root: Path,
    ticker: str,
    historical_dir: Path,
    state_dir: Path,
    spend_limit_usd: float,
    dry_run: bool,
) -> Mapping[str, object]:
    subject_id = f"equity:{ticker}"
    retrospective_context = load_retrospective_subject_context(historical_dir)
    scientific_context = load_subject_scientific_context(root, active_subject_id=subject_id)
    retrospective_context["prior_subject_scientific_context"] = scientific_context.prior_subject_science
    retrospective_context["cross_subject_memory_provenance"] = {
        "source_path": str(scientific_context.memory_selection.source_path),
        "superseded_paths": [str(path) for path in scientific_context.memory_selection.superseded_paths],
        "frontier_version": (
            scientific_context.memory_selection.store.frontier().version
            if scientific_context.memory_selection.store.frontier() is not None
            else 0
        ),
        "record_count": len(scientific_context.memory_selection.store.records()),
    }
    prior_package_count = _prior_package_count(scientific_context.prior_subject_science)

    if dry_run:
        frontier = scientific_context.memory_selection.store.frontier()
        return {
            "ticker": ticker,
            "historical_subject_dir": str(historical_dir),
            "state_dir": str(state_dir),
            "canonical_memory_source": str(scientific_context.memory_selection.source_path),
            "canonical_memory_records": len(scientific_context.memory_selection.store.records()),
            "canonical_memory_frontier_version": frontier.version if frontier is not None else 0,
            "prior_subject_scientific_packages": prior_package_count,
            "closed": None,
            "dry_run": True,
        }

    state_dir.mkdir(parents=True, exist_ok=False)
    telemetry_path = state_dir / "sol_transport_telemetry.jsonl"
    os.environ["MTS_SOL_TELEMETRY_PATH"] = str(telemetry_path)

    subject = SubjectMetadata(subject_id=subject_id, ticker=ticker)
    package_store = JsonResearchPackageStore(state_dir / "research_packages")
    recorder = BatchCampaignResearchRecorder(package_store=package_store)
    rd = SolRetrospectiveRecoveryResearchDirector(
        research_package_store=package_store,
        retrospective_context=retrospective_context,
        base_url=_required_env("MTS_SOL_BASE_URL"),
        model=_required_env("MTS_SOL_MODEL"),
        api_key=_required_env("MTS_SOL_API_KEY"),
        timeout_seconds=int(os.getenv("MTS_SOL_TIMEOUT_SECONDS", "600")),
        required_subject_id=subject.subject_id,
        required_research_phase=ResearchPhase.EXPLORATION,
        sol_spend_limit_usd=spend_limit_usd,
        human_spend_authorization_callback=_interactive_spend_authorization,
    )
    runtime = build_batch_runtime(
        rd=rd,
        mission=SEQUENTIAL_RETROSPECTIVE_MISSION,
        nexus_path=state_dir / "research_nexus.json",
        scientific_memory=scientific_context.memory_selection.store,
    )
    evidence = IntakeEngine(runtime.cache).ingest(subject=subject, source=standard_live_market_source())
    campaign_id = state_dir.name

    (state_dir / "retrospective_context.json").write_text(
        json.dumps(retrospective_context, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )

    decision_path = state_dir / "batch_decisions.jsonl"
    report_path = state_dir / "batch_reports.jsonl"
    latest_report: BatchExecutionReport | None = None

    def accepted(request):
        recorder.record_accepted_request(campaign_id=campaign_id, subject=subject, request=request)

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
        recorder.record_plan(campaign_id=campaign_id, subject=subject, decision=decision)
        recorder.record_predictive_hypothesis_updates(decision, current_report=latest_report)
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

    try:
        outcome = runtime.orchestrator.run(
            subject=subject,
            evidence=evidence,
            decision_callback=on_decision,
            report_callback=on_report,
            accepted_request_callback=accepted,
        )
    except SolSpendAuthorizationRequired as exc:
        artifact = state_dir / "sol_spend_authorization_required.json"
        artifact.write_text(json.dumps(asdict(exc.snapshot), sort_keys=True, indent=2) + "\n", encoding="utf-8")
        return {
            "ticker": ticker,
            "state_dir": str(state_dir),
            "closed": False,
            "authorization_required": True,
            "authorization_artifact": str(artifact),
        }

    spend = rd.sol_spend_snapshot()
    frontier = scientific_context.memory_selection.store.frontier()
    summary = {
        "campaign_id": campaign_id,
        "subject_id": subject.subject_id,
        "historical_subject_dir": str(historical_dir),
        "historical_exposure_status": "EXPOSED",
        "research_phase": "EXPLORATION",
        "blind_validation_claim_allowed": False,
        "cross_subject_context_automatic": True,
        "canonical_cross_subject_memory_source": str(scientific_context.memory_selection.source_path),
        "canonical_cross_subject_memory_record_count": len(scientific_context.memory_selection.store.records()),
        "canonical_cross_subject_frontier_version": frontier.version if frontier is not None else 0,
        "prior_subject_scientific_packages_exposed": prior_package_count,
        "decisions": outcome.decisions,
        "batches_executed": outcome.batches_executed,
        "analyses_executed": outcome.analyses_executed,
        "findings_promoted": outcome.findings_promoted,
        "closed": outcome.closed,
        "close_reason": outcome.close_reason,
        "sol_spend": asdict(spend) if spend is not None else None,
        "sol_transport_telemetry": str(telemetry_path),
    }
    (state_dir / "run_summary.json").write_text(
        json.dumps(summary, sort_keys=True, indent=2, default=str) + "\n",
        encoding="utf-8",
    )
    return summary


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run AAPL, then MSFT, then XOM retrospective recovery sequentially. The next subject starts only after "
            "the prior subject closes. Permanent subject-level cross-subject scientific context is loaded for each run."
        )
    )
    parser.add_argument("--root", default="/home/ubuntu")
    parser.add_argument(
        "--historical-subject-dir",
        action="append",
        default=[],
        help="optional explicit TICKER=/absolute/path; repeat for AAPL, MSFT, XOM",
    )
    parser.add_argument(
        "--sol-spend-limit-usd",
        type=float,
        default=DEFAULT_AUTHORIZED_SOL_SPEND_USD,
        help="initial Sol spend authorization per subject",
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.sol_spend_limit_usd <= 0:
        raise RuntimeError("--sol-spend-limit-usd must be positive")

    root = Path(args.root).expanduser().resolve()
    overrides = _parse_historical_overrides(args.historical_subject_dir)
    historical_dirs = {
        ticker: _resolve_historical_subject_dir(root, ticker, overrides)
        for ticker in SEQUENCE
    }

    initial_context = load_subject_scientific_context(root, active_subject_id="equity:AAPL")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    results: list[Mapping[str, object]] = []

    print("SEQUENCE=" + ",".join(SEQUENCE), flush=True)
    print(f"CANONICAL_MEMORY_SOURCE={initial_context.memory_selection.source_path}", flush=True)
    print(f"CANONICAL_MEMORY_RECORDS={len(initial_context.memory_selection.store.records())}", flush=True)
    frontier = initial_context.memory_selection.store.frontier()
    print(f"CANONICAL_MEMORY_FRONTIER_VERSION={frontier.version if frontier is not None else 0}", flush=True)
    for ticker in SEQUENCE:
        print(f"HISTORICAL_{ticker}_DIR={historical_dirs[ticker]}", flush=True)

    for ordinal, ticker in enumerate(SEQUENCE, start=1):
        state_dir = root / f"mts-v4-sequential-rerun-{ordinal:02d}-{ticker.lower()}-{stamp}"
        result = _run_subject(
            root=root,
            ticker=ticker,
            historical_dir=historical_dirs[ticker],
            state_dir=state_dir,
            spend_limit_usd=args.sol_spend_limit_usd,
            dry_run=args.dry_run,
        )
        results.append(result)
        print(f"{ticker}_STATE_DIR={result['state_dir']}", flush=True)
        print(
            f"{ticker}_PRIOR_SUBJECT_SCIENTIFIC_PACKAGES="
            f"{result.get('prior_subject_scientific_packages', result.get('prior_subject_scientific_packages_exposed', 0))}",
            flush=True,
        )
        if args.dry_run:
            continue
        print(f"{ticker}_CLOSED={result.get('closed')}", flush=True)
        if result.get("authorization_required"):
            print(f"{ticker}_AUTHORIZATION_REQUIRED=True", flush=True)
            print(f"{ticker}_AUTHORIZATION_ARTIFACT={result.get('authorization_artifact')}", flush=True)
            return 2
        if result.get("closed") is not True:
            print(f"SEQUENCE_STOPPED_AFTER={ticker}", flush=True)
            print("REASON=PRIOR_SUBJECT_DID_NOT_CLOSE", flush=True)
            return 3

    summary = {
        "sequence": list(SEQUENCE),
        "dry_run": args.dry_run,
        "cross_subject_context_automatic": True,
        "canonical_memory_source_at_start": str(initial_context.memory_selection.source_path),
        "subjects": results,
    }
    summary_path = root / f"MTS_V4_SEQUENTIAL_RERUN_SUMMARY_{stamp}.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(f"SEQUENCE_SUMMARY={summary_path}", flush=True)
    if args.dry_run:
        print("DRY_RUN=True", flush=True)
        print("SOL_CALLS=0", flush=True)
    else:
        print("SEQUENCE_COMPLETE=True", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
