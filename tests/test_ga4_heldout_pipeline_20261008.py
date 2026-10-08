import unittest
from Core.layered_ga.ga4_heldout_evidence_pipeline import run_evidence

def fixture():
    return dict(selection_digest="frozen",selection_frozen_at="2026-10-07T00:00:00Z",
        heldout_opened_at="2026-10-08T00:00:00Z",attempted_hypotheses=50,
        training_security_ids=["DEV_A"],heldout_security_ids=["HELD_B"],
        candidate_masks={"a":[True]*30},baseline_mask=[True]*30,
        net_returns=[.01]*30,cluster_ids=list(range(30)),
        provenance={"source_sha256":"abc","selection_ledger_sha256":"def"},
        independent_membership_audit=True)
class PipelineTests(unittest.TestCase):
    def test_disjoint_valid_input_is_not_self_certified(self):
        x=run_evidence(fixture())
        self.assertFalse(x["independently_verified"])
        self.assertTrue(x["membership_disjoint_verified"])
    def test_rejects_contaminated_holdout(self):
        x=fixture();x["heldout_security_ids"]=["DEV_A"]
        with self.assertRaises(ValueError):run_evidence(x)
    def test_rejects_post_open_selection(self):
        x=fixture();x["selection_frozen_at"]="2026-10-09T00:00:00Z"
        with self.assertRaises(ValueError):run_evidence(x)
    def test_rejects_unaudited_membership(self):
        x=fixture();x["independent_membership_audit"]=False
        with self.assertRaises(ValueError):run_evidence(x)
    def test_rejects_missing_attempt_count(self):
        x=fixture();x["attempted_hypotheses"]=0
        with self.assertRaises(ValueError):run_evidence(x)
