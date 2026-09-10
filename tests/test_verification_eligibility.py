from __future__ import annotations

import pytest

from MTS_V4.research_package import ResearchAnalysisRecord, ResearchPackage, ResearchQuestionRecord
from MTS_V4.research_package_store import JsonResearchPackageStore
from MTS_V4.verification_eligibility import (
    PredictiveVerificationEligibilityError,
    previously_analyzed_subject_ids,
    require_unseen_verification_subject,
)


def _package(*, rp_id: str, subject_id: str, phase: str) -> ResearchPackage:
    package = ResearchPackage(
        rp_id=rp_id,
        subject_id=subject_id,
        campaign_id=f"campaign:{rp_id}",
        originating_question="fixture",
        originating_rationale="fixture",
    )
    package = package.append_question(
        ResearchQuestionRecord(
            question_id=f"Q:{rp_id}",
            question="fixture",
            rationale="fixture",
            research_phase=phase,
        )
    )
    return package.append_analysis(
        ResearchAnalysisRecord(
            request_id=f"REQ:{rp_id}",
            question_id=f"Q:{rp_id}",
            method_id="analysis.fixture",
            parameters={},
            evidence_ids=(),
            analysis_inputs=(),
            research_phase=phase,
        )
    )


def test_unseen_subject_is_eligible_until_it_enters_exploration(tmp_path):
    store = JsonResearchPackageStore(tmp_path / "research_packages")
    store.create(_package(rp_id="RP-VAL-XOM", subject_id="equity:XOM", phase="VALIDATION"))

    assert "equity:XOM" not in previously_analyzed_subject_ids(store)
    require_unseen_verification_subject(
        package_store=store,
        subject_id="equity:XOM",
    )


def test_any_prior_exploration_permanently_blocks_verification(tmp_path):
    store = JsonResearchPackageStore(tmp_path / "research_packages")
    store.create(_package(rp_id="RP-AAPL", subject_id="equity:AAPL", phase="EXPLORATION"))

    assert previously_analyzed_subject_ids(store) == frozenset({"equity:AAPL"})
    with pytest.raises(
        PredictiveVerificationEligibilityError,
        match="not previously analyzed by MTS",
    ):
        require_unseen_verification_subject(
            package_store=store,
            subject_id="equity:AAPL",
        )


def test_other_previously_analyzed_tickers_do_not_block_new_subject(tmp_path):
    store = JsonResearchPackageStore(tmp_path / "research_packages")
    store.create(_package(rp_id="RP-AAPL", subject_id="equity:AAPL", phase="EXPLORATION"))
    store.create(_package(rp_id="RP-MSFT", subject_id="equity:MSFT", phase="EXPLORATION"))

    require_unseen_verification_subject(
        package_store=store,
        subject_id="equity:XOM",
    )
