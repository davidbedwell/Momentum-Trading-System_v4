import unittest
from Core.layered_ga.ga4_catastrophic_risk_certification import certify

class RiskCertTests(unittest.TestCase):
    def test_missing_independent_recalculation_fails(self):
        p={"policy_hash":"x","provenance":{"source":"missing","source_sha256":"none"},"thresholds":{"loss_fraction_sensitivity":[.2,.25,.3,.4],"atr20_sensitivity":[6,8,10,12]},"frozen_at":"2026-10-08T00:00:00Z","search_started_at":None}
        x=certify(p,{"policy_hash":"x","results":{}},None,source_root=".")
        self.assertEqual(x["decision"],"FAIL")
        self.assertTrue(any("independent" in f for f in x["failures"]))
    def test_no_costs_cannot_pass(self):
        p={"policy_hash":"x","provenance":{"source":"missing","source_sha256":"none"},"thresholds":{}}
        x=certify(p,{},None,source_root=".")
        self.assertEqual(x["decision"],"FAIL")
        self.assertTrue(any("cost" in f for f in x["failures"]))
