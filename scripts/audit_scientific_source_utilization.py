from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Iterable, Mapping

UW_MARKERS = ("UNUSUAL_WHALES", "UNUSUAL WHALES", "DARKPOOL", "DARK POOL")
GENERALIZATION_MARKERS = (
    "cross-subject", "cross subject", "generaliz", "other ticker", "other subject",
    "prior subject", "across ticker", "across subject", "transfer", "replicat",
)
DECISION_JSONL = (
    "batch_decisions.jsonl", "resumed_batch_decisions.jsonl", "continuation_batch_decisions.jsonl",
    "rd_decisions.jsonl",
)
DECISION_JSON = ("resume_interpretation_decision.json", "continuation_summary.json")


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path) -> list[object]:
    if not path.is_file():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            out.append(json.loads(line))
    return out


def _walk(value: object) -> Iterable[Mapping[str, object]]:
    if isinstance(value, Mapping):
        yield value
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def _decision(row: object) -> Mapping[str, object] | None:
    if not isinstance(row, Mapping):
        return None
    nested = row.get("decision")
    if isinstance(nested, Mapping):
        return nested
    return row if ("research_packages" in row or "continue_research" in row) else None


def _subject_id(documents: Iterable[object], fallback: str) -> str:
    for document in documents:
        for row in _walk(document):
            value = row.get("subject_id")
            if isinstance(value, str) and value.startswith("equity:"):
                return value
    match = re.search(r"(?:^|[-_])([A-Z]{1,6})(?:[-_]|$)", fallback.upper())
    return f"equity:{match.group(1)}" if match else fallback


def _is_uw_descriptor(row: Mapping[str, object]) -> bool:
    text = json.dumps(row, sort_keys=True, default=str).upper()
    source = str(row.get("source_identity", "")).upper()
    provider = ""
    provenance = row.get("provenance")
    if isinstance(provenance, Mapping):
        provider = str(provenance.get("provider", "")).upper()
    return "UNUSUAL_WHALES" in source or "UNUSUAL WHALES" in provider or any(m in text for m in UW_MARKERS[:2])


def _analyses(decisions: Iterable[Mapping[str, object]]) -> dict[str, Mapping[str, object]]:
    out: dict[str, Mapping[str, object]] = {}
    for decision in decisions:
        packages = decision.get("research_packages", [])
        if not isinstance(packages, list):
            continue
        for package in packages:
            if not isinstance(package, Mapping):
                continue
            analyses = package.get("analyses", [])
            if not isinstance(analyses, list):
                continue
            for analysis in analyses:
                if isinstance(analysis, Mapping) and isinstance(analysis.get("analysis_id"), str):
                    out[str(analysis["analysis_id"])] = analysis
    return out


def _refs(spec: Mapping[str, object]) -> tuple[set[str], set[str]]:
    ev: set[str] = set()
    deps: set[str] = set()
    inputs = spec.get("inputs", [])
    if not isinstance(inputs, list):
        return ev, deps
    for ref in inputs:
        if not isinstance(ref, Mapping):
            continue
        if isinstance(ref.get("evidence_id"), str):
            ev.add(str(ref["evidence_id"]))
        if isinstance(ref.get("analysis_id"), str):
            deps.add(str(ref["analysis_id"]))
    return ev, deps


def _transitive_uw(aid: str, specs: Mapping[str, Mapping[str, object]], uw_ids: set[str], memo: dict[str, bool], active: set[str]) -> bool:
    if aid in memo:
        return memo[aid]
    if aid in active or aid not in specs:
        return False
    active.add(aid)
    ev, deps = _refs(specs[aid])
    answer = bool(ev & uw_ids) or any(_transitive_uw(dep, specs, uw_ids, memo, active) for dep in deps)
    active.remove(aid)
    memo[aid] = answer
    return answer


def _text_hits(value: object, markers: tuple[str, ...]) -> list[str]:
    text = json.dumps(value, sort_keys=True, default=str)
    lower = text.lower()
    return [marker for marker in markers if marker.lower() in lower]


def audit_state(state_dir: Path, known_tickers: set[str]) -> dict[str, object]:
    documents: list[object] = []
    nexus_path = state_dir / "research_nexus.json"
    if nexus_path.is_file():
        documents.append(_json(nexus_path))
    context_path = state_dir / "retrospective_context.json"
    if context_path.is_file():
        documents.append(_json(context_path))

    raw_decisions: list[object] = []
    for name in DECISION_JSONL:
        raw_decisions.extend(_jsonl(state_dir / name))
    for name in DECISION_JSON:
        path = state_dir / name
        if path.is_file():
            raw_decisions.append(_json(path))
    documents.extend(raw_decisions)

    subject_id = _subject_id(documents, state_dir.name)
    active_ticker = subject_id.split(":", 1)[-1].upper()
    decisions = [d for row in raw_decisions if (d := _decision(row)) is not None]
    specs = _analyses(decisions)

    evidence: dict[str, Mapping[str, object]] = {}
    for document in documents:
        for row in _walk(document):
            evidence_id = row.get("evidence_id")
            if isinstance(evidence_id, str) and "source_identity" in row:
                evidence[evidence_id] = row
    uw_evidence = {eid: row for eid, row in evidence.items() if _is_uw_descriptor(row)}
    uw_ids = set(uw_evidence)

    direct: list[str] = []
    for aid, spec in specs.items():
        ev, _ = _refs(spec)
        if ev & uw_ids:
            direct.append(aid)
    memo: dict[str, bool] = {}
    transitive = sorted(aid for aid in specs if _transitive_uw(aid, specs, uw_ids, memo, set()))

    uw_decision_mentions = []
    generalization_mentions = []
    other_ticker_mentions: dict[str, list[str]] = defaultdict(list)
    generalization_analysis_ids = []
    for index, decision in enumerate(decisions, start=1):
        if _text_hits(decision, UW_MARKERS):
            uw_decision_mentions.append(index)
        if _text_hits(decision, GENERALIZATION_MARKERS):
            generalization_mentions.append(index)
        text = json.dumps(decision, sort_keys=True, default=str).upper()
        for ticker in sorted(known_tickers - {active_ticker}):
            if re.search(rf"\b{re.escape(ticker)}\b", text):
                other_ticker_mentions[ticker].append(index)
    for aid, spec in specs.items():
        if _text_hits(spec, GENERALIZATION_MARKERS):
            generalization_analysis_ids.append(aid)
        else:
            text = json.dumps(spec, sort_keys=True, default=str).upper()
            if any(re.search(rf"\b{re.escape(t)}\b", text) for t in known_tickers - {active_ticker}):
                generalization_analysis_ids.append(aid)

    uw_sources = sorted({str(row.get("source_identity", "UNKNOWN")) for row in uw_evidence.values()})
    return {
        "state_dir": str(state_dir),
        "subject_id": subject_id,
        "analysis_specifications": len(specs),
        "uw_evidence_descriptors": len(uw_evidence),
        "uw_source_identities": uw_sources,
        "uw_direct_analysis_count": len(direct),
        "uw_direct_analysis_ids": sorted(direct),
        "uw_transitive_analysis_count": len(transitive),
        "uw_transitive_analysis_ids": transitive,
        "uw_mentioned_in_sol_decisions": uw_decision_mentions,
        "generalization_language_decisions": generalization_mentions,
        "other_tickers_named_in_sol_decisions": dict(sorted(other_ticker_mentions.items())),
        "generalization_analysis_count": len(set(generalization_analysis_ids)),
        "generalization_analysis_ids": sorted(set(generalization_analysis_ids)),
    }


def _discover(root: Path) -> list[Path]:
    patterns = (
        "mts-v4-retrospective-recovery-*", "mts-v4-amd-recovered-*",
        "mts-v4-sol-six-*", "mts-v4-sol-revisit-*",
    )
    paths: set[Path] = set()
    for pattern in patterns:
        for path in root.glob(pattern):
            if path.is_dir() and (path / "research_nexus.json").is_file():
                paths.add(path)
            subjects = path / "subjects"
            if subjects.is_dir():
                for child in subjects.iterdir():
                    if child.is_dir() and (child / "research_nexus.json").is_file():
                        paths.add(child)
    return sorted(paths)


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Audit actual Unusual Whales analysis utilization and cross-subject generalization behavior.")
    p.add_argument("--root", default="/home/ubuntu")
    p.add_argument("--state-dir", action="append", default=[])
    p.add_argument("--json-output")
    return p


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    dirs = [Path(x).expanduser().resolve() for x in args.state_dir] if args.state_dir else _discover(Path(args.root).expanduser().resolve())
    if not dirs:
        raise RuntimeError("no campaign state directories found")

    preliminary = []
    tickers: set[str] = set()
    for path in dirs:
        docs = []
        if (path / "research_nexus.json").is_file():
            docs.append(_json(path / "research_nexus.json"))
        sid = _subject_id(docs, path.name)
        tickers.add(sid.split(":", 1)[-1].upper())
        preliminary.append(path)

    reports = [audit_state(path, tickers) for path in preliminary]
    totals = {
        "subjects": len(reports),
        "analysis_specifications": sum(int(r["analysis_specifications"]) for r in reports),
        "uw_evidence_descriptors": sum(int(r["uw_evidence_descriptors"]) for r in reports),
        "uw_direct_analysis_count": sum(int(r["uw_direct_analysis_count"]) for r in reports),
        "uw_transitive_analysis_count": sum(int(r["uw_transitive_analysis_count"]) for r in reports),
        "subjects_with_direct_uw_analysis": sum(1 for r in reports if int(r["uw_direct_analysis_count"]) > 0),
        "subjects_with_generalization_language": sum(1 for r in reports if r["generalization_language_decisions"] or r["other_tickers_named_in_sol_decisions"]),
        "generalization_analysis_count": sum(int(r["generalization_analysis_count"]) for r in reports),
    }
    output = {"totals": totals, "subjects": reports}
    print(json.dumps(output, indent=2, sort_keys=True))
    if args.json_output:
        Path(args.json_output).write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
