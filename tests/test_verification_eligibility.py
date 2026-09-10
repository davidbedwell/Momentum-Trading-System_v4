from __future__ import annotations

import pytest

from MTS_V4.research_package import ResearchAnalysisRecord, ResearchPackage, ResearchQuestionRecord
from MTS_V4.research_package_store import JsonResearchPackageStore
from MTS_V4.verification_eligibility import (
    HistoricalPredictiveVerificationEligibilityError,
    previously_analyzed_subject_ids,
    require_unseen_historical_verification_subject,
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


def test_unseen_subject_is_eligible_for_historical_verification_until_exploration(tmp_path):
    store = JsonResearchPackageStore(tmp_path / "research_packages")
    store.create(_package(rp_id="RP-VAL-XOM", subject_id="equity:XOM", phase="VALIDATION"))

    assert "equity:XOM" not in previously_analyzed_subject_ids(store)
    require_unseen_historical_verification_subject(
        package_store=store,
        subject_id="equity:XOM",
    )


def test_prior_exploration_blocks_retrospective_historical_verification(tmp_path):
    store = JsonResearchPackageStore(tmp_path / "research_packages")
    store.create(_package(rp_id="RP-AAPL", subject_id="equity:AAPL", phase="EXPLORATION"))

    assert previously_analyzed_subject_ids(store) == frozenset({"equity:AAPL"})
    with pytest.raises(
        HistoricalPredictiveVerificationEligibilityError,
        match="retrospective historical predictive verification",
    ):
        require_unseen_historical_verification_subject(
            package_store=store,
            subject_id="equity:AAPL",
        )


def test_other_previously_analyzed_tickers_do_not_block_new_historical_subject(tmp_path):
    store = JsonResearchPackageStore(tmp_path / "research_packages")
    store.create(_package(rp_id="RP-AAPL", subject_id="equity:AAPL", phase="EXPLORATION"))
    store.create(_package(rp_id="RP-MSFT", subject_id="equity:MSFT", phase="EXPLORATION"))

    require_unseen_historical_verification_subject(
        package_store=store,
        subject_id="equity:XOM",
    )


def test_seen_inventory_is_not_a_live_trading_prohibition(tmp_path):
    store = JsonResearchPackageStore(tmp_path / "research_packages")
    store.create(_package(rp_id="RP-AAPL", subject_id="equity:AAPL", phase="EXPLORATION"))

    # The eligibility module exposes only a historical-verification gate. AAPL
    # remaining in the seen inventory is expected and must not be interpreted as
    # a ban on genuine current/future-facing prediction or trading.
    assert "equity:AAPL" in previously_analyzed_subject_ids(store)
