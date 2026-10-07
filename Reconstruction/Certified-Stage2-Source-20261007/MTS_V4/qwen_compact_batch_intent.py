from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
import hashlib
import json
import re
from typing import Any, Mapping, Sequence

from .batch_contracts import (
    BatchResearchDecision,
    ResearchPackageClosure,
    ResearchPackagePlan,
    ScientificAnalysisSpecification,
    ScientificInputReference,
)
from .batch_rd_codec import BatchResearchDecisionCodec
from .contracts import Finding, ResearchPhase
from .sol_spend_guard import SolResearchProgressEstimate


class QwenCompactIntentError(ValueError):
    """Fail-closed defect in Qwen's compact scientific batch intent."""


@dataclass(frozen=True, slots=True)
class CompactInputIntent:
    role: str
    source_kind: str
    source_id: str
    dataset_name: str | None


@dataclass(frozen=True, slots=True)
class CompactAnalysisIntent:
    local_key: str
    parent_local_key: str | None
    question: str
    method_id: str
    inputs: tuple[CompactInputIntent, ...]
    parameters: Mapping[str, Any]
    research_phase: ResearchPhase
    rationale: str


@dataclass(frozen=True, slots=True)
class CompactResearchLineIntent:
    existing_rp_id: str | None
    parent_existing_rp_id: str | None
    objective: str
    decision_boundary: str | None
    analyses: tuple[CompactAnalysisIntent, ...]


@dataclass(frozen=True, slots=True)
class CompactClosureIntent:
    existing_rp_id: str
    close_reason: str
    final_assessment: str | None


@dataclass(frozen=True, slots=True)
class CompactFindingIntent:
    statement: str
    supporting_result_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    metadata: Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class CompactProgressIntent:
    estimated_percent_complete: float
    estimated_remaining_batches: int
    estimated_remaining_model_calls: int
    estimate_confidence: str
    estimate_rationale: str


@dataclass(frozen=True, slots=True)
class CompactBatchIntent:
    action: str
    batch_interpretation: str
    research_lines: tuple[CompactResearchLineIntent, ...]
    rp_closures: tuple[CompactClosureIntent, ...]
    findings: tuple[CompactFindingIntent, ...]
    continuation_summary: str | None
    close_reason: str | None
    progress: CompactProgressIntent


def _nonblank(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise QwenCompactIntentError(f"{field} must be a nonblank string")
    return value.strip()


def _nullable_nonblank(value: Any, field: str) -> str | None:
    if value is None:
        return None
    return _nonblank(value, field)


def _mapping(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise QwenCompactIntentError(f"{field} must be an object")
    return value


def _list(value: Any, field: str) -> list[Any]:
    if not isinstance(value, list):
        raise QwenCompactIntentError(f"{field} must be a list")
    return value


def _decode_input(raw: Any, path: str) -> CompactInputIntent:
    item = _mapping(raw, path)
    role = _nonblank(item.get("role"), f"{path}.role")
    source_kind = _nonblank(item.get("source_kind"), f"{path}.source_kind").upper()
    if source_kind not in {"EVIDENCE", "ANALYSIS"}:
        raise QwenCompactIntentError(
            f"{path}.source_kind must be EVIDENCE or ANALYSIS"
        )
    dataset_name = _nullable_nonblank(item.get("dataset_name"), f"{path}.dataset_name")
    if source_kind == "EVIDENCE" and dataset_name is not None:
        raise QwenCompactIntentError(
            f"{path}.dataset_name is allowed only for ANALYSIS sources"
        )
    return CompactInputIntent(
        role=role,
        source_kind=source_kind,
        source_id=_nonblank(item.get("source_id"), f"{path}.source_id"),
        dataset_name=dataset_name,
    )


def _decode_analysis(raw: Any, path: str) -> CompactAnalysisIntent:
    item = _mapping(raw, path)
    try:
        phase = ResearchPhase(_nonblank(item.get("research_phase"), f"{path}.research_phase"))
    except ValueError as exc:
        raise QwenCompactIntentError(
            f"{path}.research_phase must be EXPLORATION or VALIDATION"
        ) from exc
    parameters = _mapping(item.get("parameters"), f"{path}.parameters")
    inputs = tuple(
        _decode_input(value, f"{path}.inputs[{index}]")
        for index, value in enumerate(_list(item.get("inputs"), f"{path}.inputs"))
    )
    roles = [value.role for value in inputs]
    if len(roles) != len(set(roles)):
        raise QwenCompactIntentError(f"{path}.inputs roles must be unique")
    return CompactAnalysisIntent(
        local_key=_nonblank(item.get("local_key"), f"{path}.local_key"),
        parent_local_key=_nullable_nonblank(
            item.get("parent_local_key"), f"{path}.parent_local_key"
        ),
        question=_nonblank(item.get("question"), f"{path}.question"),
        method_id=_nonblank(item.get("method_id"), f"{path}.method_id"),
        inputs=inputs,
        parameters=dict(parameters),
        research_phase=phase,
        rationale=_nonblank(item.get("rationale"), f"{path}.rationale"),
    )


def decode_compact_batch_intent(text: str) -> CompactBatchIntent:
    try:
        raw = json.loads(text)
    except json.JSONDecodeError as exc:
        raise QwenCompactIntentError(f"compact intent is not valid JSON: {exc}") from exc
    root = _mapping(raw, "intent")
    action = _nonblank(root.get("action"), "action").upper()
    if action not in {"EXECUTE", "WAIT", "CLOSE"}:
        raise QwenCompactIntentError("action must be EXECUTE, WAIT, or CLOSE")

    lines = []
    for line_index, value in enumerate(
        _list(root.get("research_lines"), "research_lines")
    ):
        path = f"research_lines[{line_index}]"
        item = _mapping(value, path)
        analyses = tuple(
            _decode_analysis(raw_analysis, f"{path}.analyses[{analysis_index}]")
            for analysis_index, raw_analysis in enumerate(
                _list(item.get("analyses"), f"{path}.analyses")
            )
        )
        if not analyses:
            raise QwenCompactIntentError(f"{path}.analyses cannot be empty")
        local_keys = [analysis.local_key for analysis in analyses]
        if len(local_keys) != len(set(local_keys)):
            raise QwenCompactIntentError(f"{path}.analysis local_key values must be unique")
        lines.append(
            CompactResearchLineIntent(
                existing_rp_id=_nullable_nonblank(
                    item.get("existing_rp_id"), f"{path}.existing_rp_id"
                ),
                parent_existing_rp_id=_nullable_nonblank(
                    item.get("parent_existing_rp_id"),
                    f"{path}.parent_existing_rp_id",
                ),
                objective=_nonblank(item.get("objective"), f"{path}.objective"),
                decision_boundary=_nullable_nonblank(
                    item.get("decision_boundary"), f"{path}.decision_boundary"
                ),
                analyses=analyses,
            )
        )

    closures = []
    for index, value in enumerate(_list(root.get("rp_closures"), "rp_closures")):
        path = f"rp_closures[{index}]"
        item = _mapping(value, path)
        closures.append(
            CompactClosureIntent(
                existing_rp_id=_nonblank(
                    item.get("existing_rp_id"), f"{path}.existing_rp_id"
                ),
                close_reason=_nonblank(item.get("close_reason"), f"{path}.close_reason"),
                final_assessment=_nullable_nonblank(
                    item.get("final_assessment"), f"{path}.final_assessment"
                ),
            )
        )

    findings = []
    for index, value in enumerate(_list(root.get("findings"), "findings")):
        path = f"findings[{index}]"
        item = _mapping(value, path)
        supporting = tuple(
            _nonblank(entry, f"{path}.supporting_result_ids")
            for entry in _list(
                item.get("supporting_result_ids"), f"{path}.supporting_result_ids"
            )
        )
        evidence = tuple(
            _nonblank(entry, f"{path}.evidence_ids")
            for entry in _list(item.get("evidence_ids"), f"{path}.evidence_ids")
        )
        findings.append(
            CompactFindingIntent(
                statement=_nonblank(item.get("statement"), f"{path}.statement"),
                supporting_result_ids=supporting,
                evidence_ids=evidence,
                metadata=dict(_mapping(item.get("metadata"), f"{path}.metadata")),
            )
        )

    progress_raw = _mapping(root.get("progress"), "progress")
    try:
        progress = CompactProgressIntent(
            estimated_percent_complete=float(
                progress_raw.get("estimated_percent_complete")
            ),
            estimated_remaining_batches=int(
                progress_raw.get("estimated_remaining_batches")
            ),
            estimated_remaining_model_calls=int(
                progress_raw.get("estimated_remaining_model_calls")
            ),
            estimate_confidence=_nonblank(
                progress_raw.get("estimate_confidence"),
                "progress.estimate_confidence",
            ),
            estimate_rationale=_nonblank(
                progress_raw.get("estimate_rationale"),
                "progress.estimate_rationale",
            ),
        )
    except (TypeError, ValueError) as exc:
        raise QwenCompactIntentError("progress numeric values are invalid") from exc

    intent = CompactBatchIntent(
        action=action,
        batch_interpretation=_nonblank(
            root.get("batch_interpretation"), "batch_interpretation"
        ),
        research_lines=tuple(lines),
        rp_closures=tuple(closures),
        findings=tuple(findings),
        continuation_summary=_nullable_nonblank(
            root.get("continuation_summary"), "continuation_summary"
        ),
        close_reason=_nullable_nonblank(root.get("close_reason"), "close_reason"),
        progress=progress,
    )
    _validate_action_shape(intent)
    return intent


def _validate_action_shape(intent: CompactBatchIntent) -> None:
    if not 0 <= intent.progress.estimated_percent_complete <= 100:
        raise QwenCompactIntentError("estimated_percent_complete must be within [0, 100]")
    if intent.progress.estimated_remaining_batches < 0:
        raise QwenCompactIntentError("estimated_remaining_batches cannot be negative")
    if intent.progress.estimated_remaining_model_calls < 0:
        raise QwenCompactIntentError("estimated_remaining_model_calls cannot be negative")
    if intent.action == "EXECUTE":
        if not intent.research_lines:
            raise QwenCompactIntentError("EXECUTE requires at least one research line")
        if intent.close_reason is not None or not intent.continuation_summary:
            raise QwenCompactIntentError(
                "EXECUTE requires continuation_summary and close_reason=null"
            )
    elif intent.action == "WAIT":
        if intent.research_lines or intent.close_reason is not None:
            raise QwenCompactIntentError("WAIT requires no research lines and close_reason=null")
        if not intent.continuation_summary:
            raise QwenCompactIntentError("WAIT requires continuation_summary")
    elif intent.research_lines or not intent.close_reason:
        raise QwenCompactIntentError("CLOSE requires no research lines and a close_reason")

    continuing = intent.action in {"EXECUTE", "WAIT"}
    if continuing and (
        intent.progress.estimated_remaining_batches < 1
        or intent.progress.estimated_remaining_model_calls < 1
    ):
        raise QwenCompactIntentError(
            "continuing intent requires at least one remaining batch and model call"
        )
    if not continuing and (
        intent.progress.estimated_remaining_batches != 0
        or intent.progress.estimated_remaining_model_calls != 0
    ):
        raise QwenCompactIntentError("CLOSE requires zero remaining batches and model calls")


def _prompt_document(messages: Sequence[Mapping[str, str]]) -> Mapping[str, Any]:
    for message in reversed(messages):
        if message.get("role") != "user":
            continue
        try:
            value = json.loads(str(message.get("content", "")))
        except json.JSONDecodeError:
            continue
        if isinstance(value, Mapping) and isinstance(value.get("context"), Mapping):
            return value
    raise QwenCompactIntentError("prompt contains no governed user context")


def _existing_research_packages(context: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    transport = context.get("research_packages", {})
    summaries = (
        transport.get("research_package_summaries", [])
        if isinstance(transport, Mapping)
        else []
    )
    return {
        str(item["rp_id"]): item
        for item in summaries
        if isinstance(item, Mapping)
        and isinstance(item.get("rp_id"), str)
        and item.get("status") == "OPEN"
    }


def _batch_records(context: Mapping[str, Any]) -> tuple[Mapping[str, Any], ...]:
    report = context.get("batch_execution_report", {})
    if not isinstance(report, Mapping):
        return ()
    records = report.get("records", {})
    if isinstance(records, list):
        normalized = []
        for record in records:
            if not isinstance(record, Mapping):
                continue
            identity = {
                key: record[key]
                for key in (
                    "analysis_id",
                    "rp_id",
                    "status",
                    "objective_defect",
                    "mechanical_repairs",
                )
                if key in record
            }
            analysis_result = record.get("analysis_result")
            compiled = record.get("compiled_request_audit")
            if isinstance(analysis_result, Mapping):
                for key in ("method_id", "result_id", "limitations"):
                    if key in analysis_result:
                        identity[key] = analysis_result[key]
            if "method_id" not in identity and isinstance(compiled, Mapping):
                if "method_id" in compiled:
                    identity["method_id"] = compiled["method_id"]
            normalized.append(identity)
        return tuple(normalized)
    if isinstance(records, Mapping):
        values = records.get("record_identities_and_exceptions", [])
        if isinstance(values, list):
            return tuple(value for value in values if isinstance(value, Mapping))
    return ()


def _completed_batch_analysis_ids(context: Mapping[str, Any]) -> frozenset[str]:
    return frozenset(
        str(record["analysis_id"])
        for record in _batch_records(context)
        if record.get("status") == "SUCCESS"
        and isinstance(record.get("analysis_id"), str)
        and str(record["analysis_id"]).strip()
    )


_MISSING_OUTPUT_PATH = re.compile(
    r"does not contain the requested output_path\s*\((.*?)\)", re.IGNORECASE
)
_QUOTED_PATH_COMPONENT = re.compile(r"['\"]([^'\"]+)['\"]")


def _observed_unavailable_dataset_paths(
    context: Mapping[str, Any],
) -> tuple[Mapping[str, Any], ...]:
    unavailable = []
    seen = set()
    for record in _batch_records(context):
        if record.get("status") != "OBJECTIVE_CONTRACT_DEFECT":
            continue
        defect = record.get("objective_defect")
        if not isinstance(defect, str):
            continue
        match = _MISSING_OUTPUT_PATH.search(defect)
        if match is None:
            continue
        components = tuple(_QUOTED_PATH_COMPONENT.findall(match.group(1)))
        if not components:
            continue
        key = (str(record.get("analysis_id", "")), components)
        if key in seen:
            continue
        seen.add(key)
        unavailable.append(
            {
                "requesting_analysis_id": str(record.get("analysis_id", "")),
                "output_path": list(components),
                "dataset_name": components[-1],
                "objective_defect": defect,
            }
        )
    return tuple(unavailable)


def _confirmed_current_batch_dataset_names(
    context: Mapping[str, Any],
) -> tuple[str, ...]:
    report = context.get("batch_execution_report", {})
    records = report.get("records", {}) if isinstance(report, Mapping) else {}
    names = set()
    if isinstance(records, list):
        def visit(value: Any) -> None:
            if isinstance(value, Mapping):
                for key, child in value.items():
                    if key in {"derived_dataset_catalog", "derived_datasets"} and isinstance(
                        child, Mapping
                    ):
                        names.update(str(name) for name in child)
                    visit(child)
            elif isinstance(value, list):
                for child in value:
                    visit(child)

        for record in records:
            if not isinstance(record, Mapping) or record.get("status") != "SUCCESS":
                continue
            result = record.get("analysis_result")
            if isinstance(result, Mapping):
                visit(result.get("outputs", {}))
    elif isinstance(records, Mapping):
        outputs = records.get("scientific_outputs_by_method", {})
        if isinstance(outputs, Mapping):
            for method in outputs.values():
                if not isinstance(method, Mapping):
                    continue
                summaries = method.get("field_summaries", {})
                if not isinstance(summaries, Mapping):
                    continue
                for field in summaries:
                    match = re.search(r"derived_dataset_catalog\.([^.\[]+)", str(field))
                    if match:
                        names.add(match.group(1))
    return tuple(sorted(names))


def _metadata_only_catalog_dataset_names(
    context: Mapping[str, Any],
) -> tuple[str, ...]:
    nexus = context.get("nexus_context", {})
    catalog = (
        nexus.get("campaign_analysis_result_catalog", {})
        if isinstance(nexus, Mapping)
        else {}
    )
    if isinstance(catalog, list):
        entries = catalog
    elif isinstance(catalog, Mapping):
        entries = catalog.get("entries", [])
    else:
        entries = []
    names = set()
    if isinstance(entries, list):
        for entry in entries:
            refs = (
                entry.get("reusable_dataset_metadata_refs", {})
                if isinstance(entry, Mapping)
                else {}
            )
            if isinstance(refs, Mapping):
                names.update(str(name) for name in refs)
    confirmed = set(_confirmed_current_batch_dataset_names(context))
    return tuple(sorted(names - confirmed))


def _qwen_state_grounding_ledger(context: Mapping[str, Any]) -> Mapping[str, Any]:
    completed = []
    for record in _batch_records(context):
        if record.get("status") != "SUCCESS":
            continue
        completed.append(
            {
                "analysis_id": record.get("analysis_id"),
                "method_id": record.get("method_id"),
                "result_id": record.get("result_id"),
                "rp_id": record.get("rp_id"),
                "status": "COMPLETED_SUCCESS",
            }
        )
    return {
        "format": "MTS_V4_QWEN_STATE_GROUNDING_LEDGER_V1",
        "completed_newest_batch_analyses": completed,
        "completed_work_rule": (
            "Every COMPLETED_SUCCESS entry has already executed and its result is present in the "
            "current batch report. Interpret it; do not schedule it again. A scientifically new "
            "analysis must use a new local_key and state the new distinction in its question and "
            "rationale."
        ),
        "confirmed_executable_current_batch_datasets": list(
            _confirmed_current_batch_dataset_names(context)
        ),
        "metadata_only_catalog_datasets": list(
            _metadata_only_catalog_dataset_names(context)
        ),
        "observed_unavailable_dataset_paths": list(
            _observed_unavailable_dataset_paths(context)
        ),
        "dataset_execution_rule": (
            "Catalog metadata advertises scientific identity but does not prove that a dataset is "
            "exposed by the named executable result. An observed unavailable path overrides catalog "
            "advertisement. Do not retry it unless a genuinely different source result or newly "
            "supplied executable path is present."
        ),
    }


def _stable_id(prefix: str, case_id: str, ordinal: str, authored: Any) -> str:
    payload = json.dumps(
        {"case_id": case_id, "ordinal": ordinal, "authored": authored},
        sort_keys=True,
        default=str,
        separators=(",", ":"),
    ).encode("utf-8")
    return f"{prefix}:{hashlib.sha256(payload).hexdigest()[:24]}"


def _jsonable(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def decision_json(decision: BatchResearchDecision) -> str:
    return json.dumps(
        _jsonable(asdict(decision)),
        sort_keys=True,
        separators=(",", ":"),
    )


def compile_compact_batch_intent(
    intent: CompactBatchIntent,
    *,
    messages: Sequence[Mapping[str, str]],
    case_id: str,
) -> BatchResearchDecision:
    document = _prompt_document(messages)
    context = _mapping(document.get("context"), "context")
    subject = _mapping(context.get("subject"), "context.subject")
    subject_id = _nonblank(subject.get("subject_id"), "context.subject.subject_id")
    methods = {
        str(item["method_id"])
        for item in context.get("available_analysis_methods", [])
        if isinstance(item, Mapping) and isinstance(item.get("method_id"), str)
    }
    evidence_ids = {
        str(item["evidence_id"])
        for item in context.get("evidence", [])
        if isinstance(item, Mapping) and isinstance(item.get("evidence_id"), str)
    }
    existing_rps = _existing_research_packages(context)
    completed_analysis_ids = _completed_batch_analysis_ids(context)
    unavailable_dataset_names = {
        str(item["dataset_name"])
        for item in _observed_unavailable_dataset_paths(context)
        if isinstance(item.get("dataset_name"), str)
    }

    packages: list[ResearchPackagePlan] = []
    all_analysis_ids: dict[str, str] = {}
    line_analysis_keys: list[set[str]] = []
    resolved_lines: list[tuple[str, str | None]] = []
    occupied_rp_ids: set[str] = set()
    for line_index, line in enumerate(intent.research_lines, start=1):
        if line.existing_rp_id is not None:
            durable = existing_rps.get(line.existing_rp_id)
            if durable is None:
                raise QwenCompactIntentError(
                    f"selected existing_rp_id is not an open local RP: {line.existing_rp_id}"
                )
            rp_id = line.existing_rp_id
            # The compact model may redundantly emit a parent while identifying an
            # existing line.  Parentage is durable MTS state, not model-authored
            # scientific intent, so continuation always restores it from the
            # authoritative RP record and never accepts a replacement from Qwen.
            parent_rp_id = durable.get("parent_rp_id")
            if parent_rp_id is not None:
                parent_rp_id = str(parent_rp_id)
        else:
            parent_rp_id = line.parent_existing_rp_id
            if parent_rp_id is not None and parent_rp_id not in existing_rps:
                raise QwenCompactIntentError(
                    f"parent_existing_rp_id is not an open local RP: {parent_rp_id}"
                )
            rp_id = _stable_id(
                "QWEN-RP",
                case_id,
                str(line_index),
                {"objective": line.objective, "parent": parent_rp_id},
            )
        if rp_id in occupied_rp_ids:
            raise QwenCompactIntentError(f"research lines resolve to duplicate RP: {rp_id}")
        occupied_rp_ids.add(rp_id)
        resolved_lines.append((rp_id, parent_rp_id))
        keys = {analysis.local_key for analysis in line.analyses}
        line_analysis_keys.append(keys)
        for analysis_index, analysis in enumerate(line.analyses, start=1):
            if analysis.local_key in completed_analysis_ids:
                raise QwenCompactIntentError(
                    "analysis local_key identifies work already completed in the newest batch: "
                    f"{analysis.local_key}; interpret its supplied result instead of rerunning it"
                )
            if analysis.local_key in all_analysis_ids:
                raise QwenCompactIntentError(
                    f"analysis local_key must be unique across the batch: {analysis.local_key}"
                )
            all_analysis_ids[analysis.local_key] = _stable_id(
                "qwen-analysis",
                case_id,
                f"{line_index}.{analysis_index}",
                {"question": analysis.question, "method_id": analysis.method_id},
            )

    for line_index, line in enumerate(intent.research_lines):
        rp_id, parent_rp_id = resolved_lines[line_index]
        analyses: list[ScientificAnalysisSpecification] = []
        question_ids = {
            analysis.local_key: _stable_id(
                "QWEN-Q",
                case_id,
                f"{line_index + 1}.{analysis_index}",
                analysis.question,
            )
            for analysis_index, analysis in enumerate(line.analyses, start=1)
        }
        for analysis in line.analyses:
            if analysis.method_id not in methods:
                raise QwenCompactIntentError(
                    f"selected method_id is unavailable: {analysis.method_id}"
                )
            if analysis.parent_local_key is not None:
                if analysis.parent_local_key not in line_analysis_keys[line_index]:
                    raise QwenCompactIntentError(
                        f"parent_local_key must reference the same research line: "
                        f"{analysis.parent_local_key}"
                    )
                if analysis.parent_local_key == analysis.local_key:
                    raise QwenCompactIntentError("analysis cannot parent itself")
                parent_question_id = question_ids[analysis.parent_local_key]
            else:
                parent_question_id = None
            inputs = []
            for source in analysis.inputs:
                if source.source_kind == "EVIDENCE":
                    if source.source_id not in evidence_ids:
                        raise QwenCompactIntentError(
                            f"selected evidence_id is unavailable: {source.source_id}"
                        )
                    inputs.append(
                        ScientificInputReference(
                            role=source.role,
                            evidence_id=source.source_id,
                        )
                    )
                else:
                    if source.dataset_name in unavailable_dataset_names:
                        raise QwenCompactIntentError(
                            "selected analysis dataset was observed unavailable from executable "
                            f"result transport: {source.dataset_name}; catalog advertisement alone "
                            "does not authorize another retry"
                        )
                    dependency_id = all_analysis_ids.get(source.source_id, source.source_id)
                    if dependency_id == all_analysis_ids[analysis.local_key]:
                        raise QwenCompactIntentError("analysis cannot depend on itself")
                    inputs.append(
                        ScientificInputReference(
                            role=source.role,
                            analysis_id=dependency_id,
                            dataset_name=source.dataset_name,
                        )
                    )
            analyses.append(
                ScientificAnalysisSpecification(
                    analysis_id=all_analysis_ids[analysis.local_key],
                    rp_id=rp_id,
                    question_id=question_ids[analysis.local_key],
                    subject_id=subject_id,
                    question=analysis.question,
                    method_id=analysis.method_id,
                    inputs=tuple(inputs),
                    parameters=dict(analysis.parameters),
                    research_phase=analysis.research_phase,
                    rationale=analysis.rationale,
                    parent_question_id=parent_question_id,
                    parent_rp_id=parent_rp_id,
                )
            )
        packages.append(
            ResearchPackagePlan(
                rp_id=rp_id,
                objective=line.objective,
                analyses=tuple(analyses),
                parent_rp_id=parent_rp_id,
                decision_boundary=line.decision_boundary,
            )
        )

    package_ids = {package.rp_id for package in packages}
    closures = []
    closure_ids: set[str] = set()
    for closure in intent.rp_closures:
        if closure.existing_rp_id not in existing_rps:
            raise QwenCompactIntentError(
                f"closure references a non-open local RP: {closure.existing_rp_id}"
            )
        if closure.existing_rp_id in package_ids:
            raise QwenCompactIntentError(
                "an RP cannot be continued and closed in the same compact intent"
            )
        if closure.existing_rp_id in closure_ids:
            raise QwenCompactIntentError("compact intent contains duplicate RP closures")
        closure_ids.add(closure.existing_rp_id)
        closures.append(
            ResearchPackageClosure(
                rp_id=closure.existing_rp_id,
                close_reason=closure.close_reason,
                final_assessment=closure.final_assessment,
            )
        )

    findings = []
    for index, finding in enumerate(intent.findings, start=1):
        unavailable = sorted(set(finding.evidence_ids) - evidence_ids)
        if unavailable:
            raise QwenCompactIntentError(
                f"finding references unavailable evidence_ids: {unavailable}"
            )
        findings.append(
            Finding(
                finding_id=_stable_id(
                    "qwen-finding", case_id, str(index), finding.statement
                ),
                subject_id=subject_id,
                statement=finding.statement,
                supporting_result_ids=finding.supporting_result_ids,
                evidence_ids=finding.evidence_ids,
                metadata=dict(finding.metadata),
            )
        )

    continuing = intent.action in {"EXECUTE", "WAIT"}
    research_state = (
        {
            "scientific_continuation_state": {
                "summary": intent.continuation_summary,
                "source": "QWEN_COMPACT_BATCH_INTENT_V1",
            }
        }
        if continuing
        else {}
    )
    decision = BatchResearchDecision(
        continue_research=continuing,
        waiting_for_future_cohorts=intent.action == "WAIT",
        research_packages=tuple(packages),
        rp_closures=tuple(closures),
        promote_findings=tuple(findings),
        research_state=research_state,
        close_reason=intent.close_reason,
        batch_interpretation=intent.batch_interpretation,
        research_progress=SolResearchProgressEstimate(
            estimated_percent_complete=intent.progress.estimated_percent_complete,
            estimated_remaining_batches=intent.progress.estimated_remaining_batches,
            estimated_remaining_sol_calls=(
                intent.progress.estimated_remaining_model_calls
            ),
            estimate_confidence=intent.progress.estimate_confidence,
            estimate_rationale=intent.progress.estimate_rationale,
        ),
    )
    return BatchResearchDecisionCodec.decode(decision_json(decision))


def compact_intent_json_schema() -> Mapping[str, Any]:
    nonblank = {"type": "string", "minLength": 1}
    nullable_nonblank = {"anyOf": [nonblank, {"type": "null"}]}
    input_intent = {
        "type": "object",
        "required": ["role", "source_kind", "source_id", "dataset_name"],
        "properties": {
            "role": nonblank,
            "source_kind": {"enum": ["EVIDENCE", "ANALYSIS"]},
            "source_id": nonblank,
            "dataset_name": nullable_nonblank,
        },
        "additionalProperties": False,
    }
    analysis_intent = {
        "type": "object",
        "required": [
            "local_key",
            "parent_local_key",
            "question",
            "method_id",
            "inputs",
            "parameters",
            "research_phase",
            "rationale",
        ],
        "properties": {
            "local_key": nonblank,
            "parent_local_key": nullable_nonblank,
            "question": nonblank,
            "method_id": nonblank,
            "inputs": {"type": "array", "items": input_intent},
            "parameters": {"type": "object"},
            "research_phase": {"enum": ["EXPLORATION", "VALIDATION"]},
            "rationale": nonblank,
        },
        "additionalProperties": False,
    }
    line_intent = {
        "type": "object",
        "required": [
            "existing_rp_id",
            "parent_existing_rp_id",
            "objective",
            "decision_boundary",
            "analyses",
        ],
        "properties": {
            "existing_rp_id": nullable_nonblank,
            "parent_existing_rp_id": nullable_nonblank,
            "objective": nonblank,
            "decision_boundary": nullable_nonblank,
            "analyses": {"type": "array", "minItems": 1, "items": analysis_intent},
        },
        "additionalProperties": False,
    }
    closure_intent = {
        "type": "object",
        "required": ["existing_rp_id", "close_reason", "final_assessment"],
        "properties": {
            "existing_rp_id": nonblank,
            "close_reason": nonblank,
            "final_assessment": nullable_nonblank,
        },
        "additionalProperties": False,
    }
    finding_intent = {
        "type": "object",
        "required": [
            "statement",
            "supporting_result_ids",
            "evidence_ids",
            "metadata",
        ],
        "properties": {
            "statement": nonblank,
            "supporting_result_ids": {"type": "array", "items": nonblank},
            "evidence_ids": {"type": "array", "items": nonblank},
            "metadata": {"type": "object"},
        },
        "additionalProperties": False,
    }
    progress = {
        "type": "object",
        "required": [
            "estimated_percent_complete",
            "estimated_remaining_batches",
            "estimated_remaining_model_calls",
            "estimate_confidence",
            "estimate_rationale",
        ],
        "properties": {
            "estimated_percent_complete": {"type": "number", "minimum": 0, "maximum": 100},
            "estimated_remaining_batches": {"type": "integer", "minimum": 0},
            "estimated_remaining_model_calls": {"type": "integer", "minimum": 0},
            "estimate_confidence": nonblank,
            "estimate_rationale": nonblank,
        },
        "additionalProperties": False,
    }
    return {
        "type": "object",
        "required": [
            "action",
            "batch_interpretation",
            "research_lines",
            "rp_closures",
            "findings",
            "continuation_summary",
            "close_reason",
            "progress",
        ],
        "properties": {
            "action": {"enum": ["EXECUTE", "WAIT", "CLOSE"]},
            "batch_interpretation": nonblank,
            "research_lines": {"type": "array", "items": line_intent},
            "rp_closures": {"type": "array", "items": closure_intent},
            "findings": {"type": "array", "items": finding_intent},
            "continuation_summary": nullable_nonblank,
            "close_reason": nullable_nonblank,
            "progress": progress,
        },
        "additionalProperties": False,
    }


def compact_intent_messages(
    messages: Sequence[Mapping[str, str]],
) -> tuple[Mapping[str, str], ...]:
    transformed = [dict(message) for message in messages]
    document = dict(_prompt_document(transformed))
    context = document.get("context")
    if isinstance(context, Mapping):
        context = dict(context)
        context["qwen_state_grounding"] = _qwen_state_grounding_ledger(context)
        document["context"] = context
    document["required_batch_decision_schema"] = compact_intent_json_schema()
    document["qwen_compact_batch_contract"] = {
        "format": "MTS_V4_QWEN_COMPACT_BATCH_INTENT_V1",
        "batch_preservation": (
            "Return every scientifically warranted research line and Analysis together in this "
            "single batched intent. Never split the batch into per-analysis model calls."
        ),
        "scientific_authority": (
            "You select questions, evidence, methods, parameters, interpretation, continuation, "
            "closure, and findings. Deterministic code supplies only unique IDs, durable lineage, "
            "exact bindings, and canonical serialization."
        ),
        "identity_rules": (
            "Do not invent RP, analysis, question, or finding IDs. Use local_key only to connect "
            "same-batch analyses. Use exact existing_rp_id only when continuing or closing an open "
            "RP shown in context."
        ),
        "input_rules": (
            "For EVIDENCE use an exact context evidence_id as source_id. For ANALYSIS use a "
            "same-batch local_key or an exact prior analysis_id as source_id."
        ),
        "state_grounding_rules": (
            "Treat context.qwen_state_grounding as authoritative. Never repeat an analysis marked "
            "COMPLETED_SUCCESS. Never infer executable availability from metadata-only catalog "
            "advertisement, and never retry an observed unavailable dataset path without a genuinely "
            "new executable source."
        ),
    }
    raw_instructions = document.get("instructions", [])
    if isinstance(raw_instructions, list):
        instructions = list(raw_instructions)
    elif raw_instructions:
        instructions = [str(raw_instructions)]
    else:
        instructions = []
    instructions.append(
        "OUTPUT OVERRIDE: Return only MTS_V4_QWEN_COMPACT_BATCH_INTENT_V1. The compact schema "
        "supersedes full BatchResearchDecision identity and lineage fields for this Qwen-only "
        "shadow path. Preserve the complete scientific breadth of the batch."
    )
    document["instructions"] = instructions
    for index in range(len(transformed) - 1, -1, -1):
        if transformed[index].get("role") == "user":
            transformed[index] = {
                "role": "user",
                "content": json.dumps(
                    document,
                    sort_keys=True,
                    default=str,
                    separators=(",", ":"),
                ),
            }
            break
    transformed[0] = {
        "role": transformed[0].get("role", "system"),
        "content": str(transformed[0].get("content", ""))
        + "\n\nQWEN COMPACT OUTPUT OVERRIDE: Author one complete batched scientific intent using "
        "the compact schema in the user message. Do not emit full MTS identity or lineage plumbing.",
    }
    return tuple(transformed)
