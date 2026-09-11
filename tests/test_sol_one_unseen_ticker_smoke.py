from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

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
