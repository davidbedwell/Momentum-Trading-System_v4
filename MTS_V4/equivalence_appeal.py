from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping

from .openai_compatible_provider import OpenAICompatibleResearchDirector
from .virgin_equivalence import (
    EquivalenceProtocolError,
    blinded_pair,
    build_hybrid_appeal_context,
    canonical_sha256,
    freeze_arm_manifest,
    write_frozen_json,
)


APPEAL_SYSTEM = """You are the appellate Research Director for a controlled MTS experiment. You receive the COMPLETE frozen starting package, COMPLETE lower-cost Research Director work product, and ALL available hybrid Analysis results. Independently audit the work. Identify omitted research lines, unsupported promotions, missed findings, direction/horizon errors, robustness problems, and trading-conclusion errors. This V1 appeal is exactly one appellate model call and cannot execute a second corrective Analysis round. Therefore do not request new Analysis; record any work that would still be needed under unresolved instead. You may challenge, reject, reinterpret, or correct the supplied work, but you may not restart an unrestricted direct research campaign. Return strict JSON with keys: material_findings, omissions, rejected_promotions, corrections, unresolved, trading_conclusion, corrective_analysis_requests, appeal_complete."""


def collect_complete_hybrid_record(gemini_root: Path) -> tuple[list[Mapping[str, object]], list[Mapping[str, object]]]:
    work: list[Mapping[str, object]] = []
    analyses: list[Mapping[str, object]] = []
    for name in ("decisions.json", "reports.json", "outcome.json"):
        path = gemini_root / name
        if not path.is_file():
            raise EquivalenceProtocolError(f"hybrid record missing {path}")
        value = json.loads(path.read_text(encoding="utf-8"))
        work.append({"artifact": name, "content": value})
        if name == "reports.json":
            raw_reports = value.get("reports")
            if isinstance(raw_reports, list):
                for report_index, report in enumerate(raw_reports):
                    if not isinstance(report, Mapping):
                        continue
                    records = report.get("records")
                    if not isinstance(records, list):
                        continue
                    for record_index, record in enumerate(records):
                        if not isinstance(record, Mapping):
                            continue
                        result = record.get("result")
                        if isinstance(result, Mapping):
                            analyses.append({
                                "analysis_id": str(record.get("analysis_id") or result.get("result_id") or f"report:{report_index}:{record_index}"),
                                "result": dict(result),
                            })
        if name == "outcome.json":
            raw = value.get("precomputed_results")
            if isinstance(raw, Mapping):
                analyses.extend({"analysis_id": str(k), "result": v} for k, v in raw.items())
    for path in sorted((gemini_root / "research_packages").glob("*.json")):
        work.append({"artifact": str(path.relative_to(gemini_root)), "content": json.loads(path.read_text(encoding="utf-8"))})
    if not work:
        raise EquivalenceProtocolError("no Gemini work product found")
    return work, analyses


def run_bounded_sol_appeal(*, start: Mapping[str, object], gemini_root: Path, hybrid_root: Path, sol_provider: OpenAICompatibleResearchDirector, max_sol_calls: int, max_sol_spend_usd: float) -> Mapping[str, object]:
    work, analyses = collect_complete_hybrid_record(gemini_root)
    context = build_hybrid_appeal_context(starting_package=start, gemini_work=work, analysis_results=analyses, max_sol_calls=max_sol_calls, max_sol_spend_usd=max_sol_spend_usd)
    write_frozen_json(hybrid_root / "APPEAL_CONTEXT.json", context)
    if max_sol_calls != 1:
        raise EquivalenceProtocolError("V1 bounded appeal is exactly one Sol appellate call")
    raw = sol_provider._chat_completion([
        {"role": "system", "content": APPEAL_SYSTEM},
        {"role": "user", "content": json.dumps(context, sort_keys=True, separators=(",", ":"), default=str)},
    ])
    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        left, right = raw.find("{"), raw.rfind("}")
        if left < 0 or right <= left:
            raise EquivalenceProtocolError("Sol appeal did not return a JSON object")
        result = json.loads(raw[left:right + 1])
    if not isinstance(result, Mapping) or result.get("appeal_complete") is not True:
        raise EquivalenceProtocolError("Sol appeal did not close cleanly")
    corrective = result.get("corrective_analysis_requests")
    if corrective not in (None, []):
        raise EquivalenceProtocolError("V1 Sol appeal requested corrective Analysis that cannot execute inside the frozen one-call appeal")
    write_frozen_json(hybrid_root / "SOL_APPEAL.json", dict(result))
    return result


def freeze_hybrid_manifest(*, ticker: str, start: Mapping[str, object], gemini_root: Path, hybrid_root: Path, gemini_usage: Mapping[str, object], sol_usage: Mapping[str, object]) -> Mapping[str, object]:
    artifacts = []
    for root in (gemini_root, hybrid_root):
        for path in sorted(root.rglob("*.json")):
            artifacts.append({"path": str(path), "sha256": canonical_sha256(json.loads(path.read_text(encoding="utf-8")))})
    gemini_record = {}
    for name in ("decisions.json", "reports.json", "outcome.json"):
        path = gemini_root / name
        if not path.is_file():
            raise EquivalenceProtocolError(f"hybrid scientific record missing {path}")
        gemini_record[name.removesuffix(".json")] = json.loads(path.read_text(encoding="utf-8"))
    appeal_path = hybrid_root / "SOL_APPEAL.json"
    if not appeal_path.is_file():
        raise EquivalenceProtocolError("hybrid scientific record missing Sol appeal")
    appeal = json.loads(appeal_path.read_text(encoding="utf-8"))
    outcome = gemini_record.get("outcome", {}).get("outcome", {})
    waiting = bool(outcome.get("waiting_for_future_cohorts")) if isinstance(outcome, Mapping) else False
    terminal_state = "WAITING_FOR_FUTURE_COHORTS" if waiting else "CLOSED"
    manifest = freeze_arm_manifest(
        subject_id=ticker.upper(),
        arm="GEMINI_SOL_HYBRID",
        starting_sha256=str(start["sha256"]),
        artifacts=artifacts,
        usage=[dict(gemini_usage), dict(sol_usage)],
        complete=True,
        terminal_state=terminal_state,
        scientific_record={"trace": gemini_record, "final_assessment": appeal},
    )
    write_frozen_json(hybrid_root / "ARM_MANIFEST.json", manifest)
    return manifest


def create_blinded_packet(*, direct_manifest: Mapping[str, object], hybrid_manifest: Mapping[str, object], output: Path, salt: str) -> Mapping[str, object]:
    packet = blinded_pair(direct_manifest, hybrid_manifest, salt=salt)
    write_frozen_json(output, packet)
    return packet
