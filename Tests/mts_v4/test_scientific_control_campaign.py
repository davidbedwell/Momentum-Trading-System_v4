from __future__ import annotations

from MTS_V4.acceptance_controls import BLINDED_CONTROLS
from MTS_V4.scientific_control_campaign import (
    ControlAssessment,
    ControlGrade,
    ControlRunRecord,
    assemble_control_report,
)


def test_control_report_requires_all_five_and_independent_assessment():
    runs = tuple(ControlRunRecord(control.control_id, f"/{control.control_id}", 0, analyses_executed=1) for control in BLINDED_CONTROLS)
    report = assemble_control_report(runs)
    assert report.all_five_controls_present is True
    assert report.all_runs_completed is True
    assert report.all_controls_assessed is False
    assert report.overall_status == "AWAITING_INDEPENDENT_PASS_PARTIAL_FAIL_ASSESSMENT"

    assessments = tuple(
        ControlAssessment(control.control_id, ControlGrade.PASS, "independent rubric satisfied", "ChatGPT/human review")
        for control in BLINDED_CONTROLS
    )
    report = assemble_control_report(runs, assessments)
    assert report.overall_status == "CALIBRATION_PASS"
    assert report.grading_policy["BLINDING"].startswith("These grading criteria are never supplied")


def test_any_partial_or_fail_is_preserved_without_deterministic_regrading():
    runs = tuple(ControlRunRecord(control.control_id, f"/{control.control_id}", 0) for control in BLINDED_CONTROLS)
    assessments = []
    for index, control in enumerate(BLINDED_CONTROLS):
        grade = ControlGrade.FAIL if index == 0 else ControlGrade.PASS
        assessments.append(ControlAssessment(control.control_id, grade, "reviewed", "independent reviewer"))
    assert assemble_control_report(runs, assessments).overall_status == "CALIBRATION_FAIL"
