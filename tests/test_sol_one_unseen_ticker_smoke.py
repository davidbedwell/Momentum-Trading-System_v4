from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from MTS_V4.research_package import ResearchAnalysisRecord, ResearchPackage
from MTS_V4.research_package_store import JsonResearchPackageStore
from MTS_V4.subject_selection import RDSubjectSelectionDecision


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "run_sol_one_unseen_ticker_smoke.py"
SPEC = importlib.util.spec_from_file_location("run_sol_one_unseen_ticker_smoke", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_aapl_seed_preserves_subject_specific_scope() -> None:
    context = MODULE._aapl_scientific_context()
    hypothesis = context["important_tentative_hypothesis"]
    scope = hypothesis["subject_scope"]
    assert hypothesis["hypothesis_id"] == MODULE.AAPL_HYPOTHESIS_ID
    assert "AAPL only" in scope
    assert "explicitly authored and frozen before validation on another subject" in scope


def test_first_unseen_exploration_role_is_allowed() -> None:
    MODULE._require_scientifically_applicable_first_role(
        RDSubjectSelectionDecision(
            subject_id="equity:MSFT",
            rationale="Discriminate whether AAPL observations generalize.",
            mode="EXPLORATION",
            hypothesis_id=None,
        )
    )


def test_aapl_specific_hypothesis_cannot_be_rewritten_for_cross_subject_validation() -> None:
    with pytest.raises(RuntimeError, match="AAPL-specific frozen hypothesis"):
        MODULE._require_scientifically_applicable_first_role(
            RDSubjectSelectionDecision(
                subject_id="equity:MSFT",
                rationale="Blind test the AAPL rebound idea.",
                mode="VALIDATION_FIRST",
                hypothesis_id=MODULE.AAPL_HYPOTHESIS_ID,
            )
        )


def test_subject_research_provenance_preserves_rp_finding_and_result_ids(tmp_path) -> None:
    store = JsonResearchPackageStore(tmp_path / "research_packages")
    package = ResearchPackage(
        rp_id="RP-MSFT-001",
        subject_id="equity:MSFT",
        campaign_id="campaign-msft",
        originating_question="Does the exploratory relationship reproduce?",
        originating_rationale="Test portability without assuming it.",
        analyses=(
            ResearchAnalysisRecord(
                request_id="request-1",
                question_id="question-1",
                method_id="analysis.test",
                parameters={},
                evidence_ids=("evidence-1",),
                analysis_inputs=(),
                result_id="result-1",
                execution_status="SUCCESS",
                research_phase="EXPLORATION",
            ),
        ),
        findings=(
            {
                "finding_id": "F-MSFT-001",
                "summary": "Exploratory finding",
                "supporting_result_ids": ["result-1"],
            },
        ),
        status="CLOSED",
        close_reason="Exploration complete.",
        final_assessment="Do not promote a predictive hypothesis.",
    )
    store.create(package)

    provenance = MODULE._subject_research_provenance(
        package_store=store,
        subject_id="equity:MSFT",
    )

    assert len(provenance) == 1
    assert provenance[0]["rp_id"] == "RP-MSFT-001"
    assert provenance[0]["findings"][0]["finding_id"] == "F-MSFT-001"
    assert provenance[0]["findings"][0]["supporting_result_ids"] == ["result-1"]
    assert provenance[0]["analysis_results"] == [
        {
            "request_id": "request-1",
            "result_id": "result-1",
            "execution_status": "SUCCESS",
            "research_phase": "EXPLORATION",
        }
    ]


def test_subject_research_provenance_excludes_other_subjects(tmp_path) -> None:
    store = JsonResearchPackageStore(tmp_path / "research_packages")
    store.create(
        ResearchPackage(
            rp_id="RP-AAPL-001",
            subject_id="equity:AAPL",
            campaign_id="campaign-aapl",
            originating_question="AAPL question",
            originating_rationale="AAPL rationale",
        )
    )

    assert MODULE._subject_research_provenance(
        package_store=store,
        subject_id="equity:MSFT",
    ) == ()
