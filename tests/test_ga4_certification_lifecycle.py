[Reading 22 lines from start (total: 22 lines, 0 remaining)]

"""Certification cannot be manufactured before a search or external audit."""
import unittest
import json
from pathlib import Path
from Core.layered_ga.ga4_catastrophic_risk_certification import certify
from Core.layered_ga.ga4_heldout_evidence_pipeline import run_evidence

ROOT=Path(__file__).resolve().parents[1]
POLICY=ROOT/'Research/Design/MTS_STAGE2_V3_CATASTROPHIC_POLICY_FREEZE_20261007.json'

class TestCertificationLifecycle(unittest.TestCase):
    def test_presearch_freeze_not_equivalent_to_postsearch_certification(self):
        policy=json.loads(POLICY.read_text())
        self.assertEqual(policy['status'],'FROZEN_FOR_NEW_SEARCH_NOT_CERTIFIED')
        self.assertIsNone(policy['search_started_at'])
        result=certify(policy,{},None,source_root=ROOT)
        self.assertEqual(result['decision'],'FAIL')
        self.assertIn('pre-search freeze timestamp absent or invalid',result['failures'])
        self.assertIn('independent recalculation not verified',result['failures'])
    def test_heldout_requires_actual_external_evidence(self):
        with self.assertRaises(ValueError):run_evidence({'independently_verified':True})
if __name__=='__main__':unittest.main()

[executed on device: instance-e298gycb-main (a21f8a9b-b225-483b-b45f-ba34708f98ee)]