from dataclasses import replace

from MTS_V4.contracts import AnalysisRequest, ResearchDecision, ResearchPhase
from MTS_V4.research_package import ResearchPackage
from MTS_V4.research_package_store import JsonResearchPackageStore
from MTS_V4.sol_primary_provider import SolPrimaryResearchDirector


def _decision_with_parent(parent_rp_id: str | None) -> ResearchDecision:
    return ResearchDecision(
        continue_research=True,
        research_state={},
        next_request=AnalysisRequest(
            request_id="REQ-1",
            subject_id="equity:MSFT",
            question="Does the rebound relationship reproduce?",
            method_id="GROUP_AGGREGATION",
            evidence_ids=("E-1",),
            parameters={},
            research_phase=ResearchPhase.EXPLORATION,
            rationale="test continuation",
            rp_id="RP-MSFT-NEW-001",
            question_id="Q-MSFT-NEW-001",
            parent_question_id=None,
            parent_rp_id=parent_rp_id,
        ),
        rp_id="RP-MSFT-NEW-001",
    )


def test_historical_seed_rp_cannot_be_used_as_unmaterialized_local_parent(tmp_path):
    store = JsonResearchPackageStore(tmp_path / "rps")
    rd = SolPrimaryResearchDirector(
        research_package_store=store,
        base_url="https://example.invalid",
        model="test",
        api_key="x",
        required_subject_id="equity:MSFT",
        required_research_phase=ResearchPhase.EXPLORATION,
    )

    defect = rd._decision_representation_defect(
        "BEGIN_RESEARCH",
        _decision_with_parent("RP-MSFT-SEVERE5D-REBOUND-001"),
        {},
    )

    assert defect is not None
    assert "not present in the active campaign package store" in defect
    assert "cross-subject scientific memory" in defect
    assert "parent_rp_id=null" in defect


def test_local_materialized_same_subject_parent_is_allowed(tmp_path):
    store = JsonResearchPackageStore(tmp_path / "rps")
    store.create(
        ResearchPackage(
            rp_id="RP-MSFT-LOCAL-PARENT",
            subject_id="equity:MSFT",
            campaign_id="C-1",
            originating_question="Prior local question",
            originating_rationale="local lineage",
        )
    )
    rd = SolPrimaryResearchDirector(
        research_package_store=store,
        base_url="https://example.invalid",
        model="test",
        api_key="x",
        required_subject_id="equity:MSFT",
        required_research_phase=ResearchPhase.EXPLORATION,
    )

    defect = rd._decision_representation_defect(
        "BEGIN_RESEARCH",
        _decision_with_parent("RP-MSFT-LOCAL-PARENT"),
        {},
    )

    assert defect is None


def test_cross_subject_local_parent_is_rejected(tmp_path):
    store = JsonResearchPackageStore(tmp_path / "rps")
    store.create(
        ResearchPackage(
            rp_id="RP-AAPL-LOCAL-PARENT",
            subject_id="equity:AAPL",
            campaign_id="C-1",
            originating_question="Prior AAPL question",
            originating_rationale="wrong subject lineage",
        )
    )
    rd = SolPrimaryResearchDirector(
        research_package_store=store,
        base_url="https://example.invalid",
        model="test",
        api_key="x",
        required_subject_id="equity:MSFT",
        required_research_phase=ResearchPhase.EXPLORATION,
    )

    defect = rd._decision_representation_defect(
        "BEGIN_RESEARCH",
        _decision_with_parent("RP-AAPL-LOCAL-PARENT"),
        {},
    )

    assert defect is not None
    assert "different subject" in defect
