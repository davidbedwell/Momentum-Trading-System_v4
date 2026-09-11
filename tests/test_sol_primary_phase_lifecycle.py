from __future__ import annotations

import importlib.util
from pathlib import Path

from MTS_V4.contracts import AnalysisRequest, ResearchDecision, ResearchPhase
from MTS_V4.research_package_store import JsonResearchPackageStore
from MTS_V4.sol_primary_provider import SolPrimaryResearchDirector


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "run_sol_one_unseen_ticker_smoke.py"
SPEC = importlib.util.spec_from_file_location("run_sol_one_unseen_ticker_smoke_phase", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
SMOKE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SMOKE)


def _request(*, phase: ResearchPhase) -> AnalysisRequest:
    return AnalysisRequest(
        request_id="REQ-1",
        subject_id="equity:MSFT",
        question="Test question",
        method_id="analysis.transform.percent_change",
        evidence_ids=(),
        parameters={"column": "close", "lag": 5},
        research_phase=phase,
        rationale="Test rationale",
        rp_id="RP-MSFT-1",
        question_id="Q-MSFT-1",
        parent_question_id=None,
        parent_rp_id=None,
    )


def _rd(tmp_path: Path) -> SolPrimaryResearchDirector:
    return SolPrimaryResearchDirector(
        research_package_store=JsonResearchPackageStore(tmp_path / "research_packages"),
        base_url="https://example.invalid",
        model="test-sol",
        api_key="test",
        required_subject_id="equity:MSFT",
        required_research_phase=ResearchPhase.EXPLORATION,
    )


def test_exploration_selection_cannot_switch_to_validation(tmp_path: Path) -> None:
    rd = _rd(tmp_path)
    decision = ResearchDecision(
        continue_research=True,
        next_request=_request(phase=ResearchPhase.VALIDATION),
        rp_id="RP-MSFT-1",
    )
    defect = rd._decision_representation_defect("BEGIN_RESEARCH", decision, {})
    assert defect is not None
    assert "accepted subject phase contract" in defect
    assert "requires EXPLORATION" in defect


def test_new_rp_cannot_receive_hypothesis_update_before_it_is_durable(tmp_path: Path) -> None:
    rd = _rd(tmp_path)
    decision = ResearchDecision(
        continue_research=True,
        next_request=_request(phase=ResearchPhase.EXPLORATION),
        rp_id="RP-MSFT-1",
        research_state={
            "predictive_hypothesis_updates": [
                {
                    "action": "CREATE_TENTATIVE",
                    "hypothesis_id": "H-MSFT-1",
                    "statement": "test",
                    "success_definition": "test",
                    "minimum_required_trials": 20,
                    "source_result_ids": [],
                }
            ]
        },
    )
    defect = rd._decision_representation_defect("BEGIN_RESEARCH", decision, {})
    assert defect is not None
    assert "not yet durable" in defect
    assert "Establish that RP first" in defect


def test_default_unseen_candidate_universe_excludes_prior_xom_exposure(monkeypatch) -> None:
    monkeypatch.delenv("MTS_SOL_SMOKE_CANDIDATES", raising=False)
    candidates = SMOKE._candidate_subject_ids()
    assert "equity:AAPL" not in candidates
    assert "equity:XOM" not in candidates


def test_configured_xom_is_rejected_as_not_unseen(monkeypatch) -> None:
    monkeypatch.setenv("MTS_SOL_SMOKE_CANDIDATES", "MSFT,XOM")
    try:
        SMOKE._candidate_subject_ids()
    except RuntimeError as exc:
        assert "XOM has prior MTS exposure" in str(exc)
    else:
        raise AssertionError("configured XOM should be rejected from unseen smoke candidates")
