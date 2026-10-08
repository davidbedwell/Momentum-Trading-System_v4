"""Fail-closed regression checks for GA4 Stage 2 certification.

The 45-case smoke/batch output is not a scientific certification. These checks
prevent the prior two missing artifacts from being silently treated as PASS.
"""
import unittest
from Core.layered_ga.stage2_certification_evidence_v3 import (
    audit_evolutionary_ledger, audit_catastrophic_policy,
)
from Core.layered_ga.stage2_independent_auditor_v3 import audit


class CertificationFailClosedTests(unittest.TestCase):
    def test_missing_ledger_rejected(self):
        self.assertIn("evolutionary ledger absent", audit_evolutionary_ledger(None))

    def test_smoke_ledger_without_heldout_rejected(self):
        ledger = {"generations": [{"evaluated_observations": []},
                                  {"evaluated_observations": []}],
                  "heldout_selection_adjusted_validation": None}
        self.assertIn("independent selection-adjusted validation absent",
                      audit_evolutionary_ledger(ledger))

    def test_missing_risk_policy_rejected(self):
        self.assertIn("catastrophic policy absent", audit_catastrophic_policy(None))

    def test_unfrozen_risk_policy_rejected(self):
        policy = {"policy_hash": "abc", "frozen_at": "2026-10-08T04:00:00Z",
                  "search_started_at": "2026-10-08T03:00:00Z",
                  "metrics": ["loss"], "thresholds": {"loss": [0.2]},
                  "provenance": {"source": "protocol"},
                  "independent_recalculation": {"checked": True}}
        self.assertIn("catastrophic policy was not frozen before search",
                      audit_catastrophic_policy(policy))

    def test_independent_audit_cannot_pass_without_both(self):
        result = audit({"cases": []}, None, None)
        self.assertEqual("FAIL", result["decision"])
        self.assertIn("evolutionary ledger absent", result["failed_criteria"])
        self.assertIn("catastrophic policy absent", result["failed_criteria"])


if __name__ == "__main__":
    unittest.main()
