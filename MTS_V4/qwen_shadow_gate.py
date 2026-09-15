from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Mapping, Sequence

from .subject_scientific_context import SubjectContextSolBatchResearchDirector


@dataclass(frozen=True, slots=True)
class QwenShadowObservation:
    case_id: str
    transport_success: bool
    decision_decoded: bool
    objective_contract_valid: bool
    analysis_operations_proposed: int
    continued_scientific_loop: bool | None = None
    used_available_toolkit: bool | None = None
    reached_cross_evidence_relationships: bool | None = None
    handled_lack_resource_without_stalling: bool | None = None
    produced_market_science_not_infrastructure_notes: bool | None = None
    scientific_usefulness_assessment: str | None = None
    unnecessary_analysis_assessment: str | None = None
    reviewer_notes: str | None = None


@dataclass(frozen=True, slots=True)
class QwenShadowGateReport:
    cases: int
    transport_failures: int
    decode_failures: int
    objective_contract_failures: int
    total_analysis_operations: int
    minimum_analysis_operations_reached: bool
    reviewer_fields_complete: bool
    autonomy_status: str
    human_authorization_required: bool
    observations: tuple[QwenShadowObservation, ...]


def evaluate_qwen_shadow_gate(
    observations: Sequence[QwenShadowObservation],
    *,
    minimum_analysis_operations: int = 20,
) -> QwenShadowGateReport:
    """Report evidence for autonomy review without inventing a scientific pass rate.

    The only numeric readiness floor encoded here is the previously approved
    minimum campaign exposure of 20 Analysis operations. Scientific usefulness,
    unnecessary work, and autonomous behavior remain explicit reviewer judgments.
    This function can never authorize Qwen autonomy.
    """
    if minimum_analysis_operations != 20:
        raise ValueError("Qwen shadow gate currently preserves the approved 20-Analysis minimum exactly")
    items = tuple(observations)
    total_analyses = sum(max(0, item.analysis_operations_proposed) for item in items)
    reviewer_complete = bool(items) and all(
        item.continued_scientific_loop is not None
        and item.used_available_toolkit is not None
        and item.reached_cross_evidence_relationships is not None
        and item.handled_lack_resource_without_stalling is not None
        and item.produced_market_science_not_infrastructure_notes is not None
        and isinstance(item.scientific_usefulness_assessment, str)
        and bool(item.scientific_usefulness_assessment.strip())
        and isinstance(item.unnecessary_analysis_assessment, str)
        and bool(item.unnecessary_analysis_assessment.strip())
        for item in items
    )
    minimum_reached = total_analyses >= minimum_analysis_operations
    if not minimum_reached:
        status = "INSUFFICIENT_SHADOW_EXPOSURE"
    elif not reviewer_complete:
        status = "AWAITING_SCIENTIFIC_AUTONOMY_REVIEW"
    else:
        status = "READY_FOR_HUMAN_AUTONOMY_DECISION"
    return QwenShadowGateReport(
        cases=len(items),
        transport_failures=sum(not item.transport_success for item in items),
        decode_failures=sum(not item.decision_decoded for item in items),
        objective_contract_failures=sum(not item.objective_contract_valid for item in items),
        total_analysis_operations=total_analyses,
        minimum_analysis_operations_reached=minimum_reached,
        reviewer_fields_complete=reviewer_complete,
        autonomy_status=status,
        human_authorization_required=True,
        observations=items,
    )


class ReplayCapturingSubjectContextSolBatchResearchDirector(SubjectContextSolBatchResearchDirector):
    """Sol RD that preserves exact governed prompt envelopes for later Qwen replay."""

    def __init__(self, *args, replay_capture_path: str | Path, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._replay_capture_path = Path(replay_capture_path)
        self._replay_call_index = 0

    def _chat_completion(self, messages: Sequence[Mapping[str, str]]) -> str:
        content = super()._chat_completion(messages)
        self._replay_call_index += 1
        self._replay_capture_path.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "format": "MTS_V4_SOL_REPLAY_ENVELOPE_V1",
            "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
            "call_index": self._replay_call_index,
            "operation": self._operation(messages),
            "messages": [dict(item) for item in messages],
            "sol_response": content,
            "raw_market_rows_present": False,
            "intended_use": "SUPERVISED_QWEN_REPLAY_SHADOW_ONLY",
        }
        with self._replay_capture_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True, default=str, separators=(",", ":")) + "\n")
        return content


def load_shadow_observations(path: str | Path) -> tuple[QwenShadowObservation, ...]:
    records: list[QwenShadowObservation] = []
    for line_number, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        raw = json.loads(line)
        try:
            records.append(QwenShadowObservation(**raw))
        except TypeError as exc:
            raise ValueError(f"invalid Qwen shadow observation at line {line_number}: {exc}") from exc
    return tuple(records)


def write_gate_report(path: str | Path, report: QwenShadowGateReport) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(asdict(report), indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
