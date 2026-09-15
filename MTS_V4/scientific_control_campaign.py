from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Mapping, Sequence

from .acceptance_controls import BLINDED_CONTROLS


class ControlGrade(str, Enum):
    PASS = "PASS"
    PARTIAL = "PARTIAL"
    FAIL = "FAIL"
    UNASSESSED = "UNASSESSED"


@dataclass(frozen=True, slots=True)
class ControlRunRecord:
    control_id: str
    state_dir: str
    exit_code: int
    analyses_executed: int | None = None
    findings_promoted: int | None = None
    closed: bool | None = None
    sol_spend_usd: float | None = None
    replay_capture_path: str | None = None


@dataclass(frozen=True, slots=True)
class ControlAssessment:
    control_id: str
    grade: ControlGrade
    rationale: str
    assessor: str


@dataclass(frozen=True, slots=True)
class ScientificControlCampaignReport:
    runs: tuple[ControlRunRecord, ...]
    assessments: tuple[ControlAssessment, ...]
    all_five_controls_present: bool
    all_runs_completed: bool
    all_controls_assessed: bool
    overall_status: str
    grading_policy: Mapping[str, str]


GRADING_POLICY = {
    "PASS": "Independently identifies the known control effect with roughly correct direction, horizon, conditioning, and robustness; for the negative control, correctly rejects stable predictive information.",
    "PARTIAL": "Detects related structure but misses an important formulation or stability condition; for the negative control, observes weak/unstable structure without elevating it to a robust predictive claim.",
    "FAIL": "Exhausts reasonable inquiry without detecting an effect demonstrably present in the supplied control data, or promotes stable predictive information from the deterministic negative control.",
    "BLINDING": "These grading criteria are never supplied to the Research Director during the control run.",
    "AUTHORITY": "Grade is supplied after the run by an independent human/ChatGPT scientific assessment; deterministic code assembles but does not invent the grade.",
}


def assemble_control_report(
    runs: Sequence[ControlRunRecord],
    assessments: Sequence[ControlAssessment] = (),
) -> ScientificControlCampaignReport:
    expected = tuple(control.control_id for control in BLINDED_CONTROLS)
    run_map = {item.control_id: item for item in runs}
    if len(run_map) != len(runs):
        raise ValueError("duplicate control run record")
    assessment_map = {item.control_id: item for item in assessments}
    if len(assessment_map) != len(assessments):
        raise ValueError("duplicate control assessment")
    unknown = (set(run_map) | set(assessment_map)) - set(expected)
    if unknown:
        raise ValueError(f"unknown scientific control ids: {sorted(unknown)}")
    ordered_runs = tuple(run_map[key] for key in expected if key in run_map)
    ordered_assessments = tuple(assessment_map[key] for key in expected if key in assessment_map)
    all_present = set(run_map) == set(expected)
    all_completed = all_present and all(item.exit_code == 0 for item in ordered_runs)
    all_assessed = all_present and set(assessment_map) == set(expected) and all(
        item.grade is not ControlGrade.UNASSESSED and item.rationale.strip() and item.assessor.strip()
        for item in ordered_assessments
    )
    if not all_completed:
        overall = "CONTROL_EXECUTION_INCOMPLETE"
    elif not all_assessed:
        overall = "AWAITING_INDEPENDENT_PASS_PARTIAL_FAIL_ASSESSMENT"
    elif any(item.grade is ControlGrade.FAIL for item in ordered_assessments):
        overall = "CALIBRATION_FAIL"
    elif any(item.grade is ControlGrade.PARTIAL for item in ordered_assessments):
        overall = "CALIBRATION_PARTIAL"
    else:
        overall = "CALIBRATION_PASS"
    return ScientificControlCampaignReport(
        runs=ordered_runs,
        assessments=ordered_assessments,
        all_five_controls_present=all_present,
        all_runs_completed=all_completed,
        all_controls_assessed=all_assessed,
        overall_status=overall,
        grading_policy=GRADING_POLICY,
    )
