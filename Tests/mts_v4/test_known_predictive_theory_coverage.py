from __future__ import annotations

from types import SimpleNamespace
import unittest

from MTS_V4.known_predictive_theories import KNOWN_PREDICTIVE_THEORY_IDS
from MTS_V4.sol_batch_provider import SolBatchResearchDirector


def _tested(theory_id: str):
    return {
        "theory_id": theory_id,
        "status": "TESTED_UNSUPPORTED",
        "scientific_formulation": "RD-selected formulation",
        "evidence_refs": [f"result:{theory_id}"],
        "interpretation": "No support under the tested formulation.",
    }


class KnownTheoryCoverageTests(unittest.TestCase):
    def test_subject_closure_blocks_missing_human_required_theories(self) -> None:
        decision = SimpleNamespace(research_state={
            "campaign_learning_audit_state": {
                "known_theory_coverage": [_tested(KNOWN_PREDICTIVE_THEORY_IDS[0])]
            }
        })
        defect = SolBatchResearchDirector._known_theory_coverage_defect(decision)
        self.assertIn("blocked", defect)
        self.assertIn(KNOWN_PREDICTIVE_THEORY_IDS[1], defect)

    def test_all_theories_may_be_tested_without_any_required_positive_result(self) -> None:
        decision = SimpleNamespace(research_state={
            "campaign_learning_audit_state": {
                "known_theory_coverage": [_tested(theory_id) for theory_id in KNOWN_PREDICTIVE_THEORY_IDS]
            }
        })
        self.assertIsNone(SolBatchResearchDirector._known_theory_coverage_defect(decision))

    def test_objective_unavailability_requires_reason_but_not_fake_test(self) -> None:
        coverage = [_tested(theory_id) for theory_id in KNOWN_PREDICTIVE_THEORY_IDS]
        coverage[0] = {
            "theory_id": KNOWN_PREDICTIVE_THEORY_IDS[0],
            "status": "OBJECTIVELY_NOT_TESTABLE",
            "untestable_reason": "Required cross-sectional evidence is unavailable for this subject run.",
            "evidence_refs": [],
        }
        decision = SimpleNamespace(research_state={
            "campaign_learning_audit_state": {"known_theory_coverage": coverage}
        })
        self.assertIsNone(SolBatchResearchDirector._known_theory_coverage_defect(decision))

    def test_tested_theory_requires_evidence_reference(self) -> None:
        coverage = [_tested(theory_id) for theory_id in KNOWN_PREDICTIVE_THEORY_IDS]
        coverage[0]["evidence_refs"] = []
        decision = SimpleNamespace(research_state={
            "campaign_learning_audit_state": {"known_theory_coverage": coverage}
        })
        defect = SolBatchResearchDirector._known_theory_coverage_defect(decision)
        self.assertIn("evidence_refs", defect)


if __name__ == "__main__":
    unittest.main()
