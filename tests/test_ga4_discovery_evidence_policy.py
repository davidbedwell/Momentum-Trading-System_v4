import unittest
from Core.layered_ga.ga4_discovery_evidence_policy import annotate_discovery

class TestDiscoveryEvidencePolicy(unittest.TestCase):
    def test_weak_candidate_retained_with_metadata(self):
        r={"candidate_id":"weak","daily_horizon_evidence":[{"horizon":h,"n":100,"effective_n":3,"lcb95":float("nan")} for h in range(1,64)]}
        result=annotate_discovery(r)
        self.assertEqual(result["candidate_id"],"weak")
        self.assertEqual(result["discovery_evidence"]["retention"],"RETAIN_WITH_UNCERTAINTY")
        self.assertEqual(result["discovery_evidence"]["per_horizon"][0]["uncertainty_status"],"INSUFFICIENT_EVIDENCE")
        self.assertEqual(result["discovery_evidence"]["crash_episode_validation"],"DEFER_TO_STAGE_9")
        self.assertNotIn("discovery_evidence",r)
    def test_valid_estimate_not_crash_certification(self):
        r={"daily_horizon_evidence":[{"horizon":h,"n":500,"effective_n":80,"lcb95":.01} for h in range(1,64)]}
        result=annotate_discovery(r)
        self.assertEqual(result["discovery_evidence"]["per_horizon"][0]["uncertainty_status"],"ESTIMATED_NOT_MARKET_SHOCK_CERTIFIED")
    def test_incomplete_path_fails(self):
        with self.assertRaises(ValueError):
            annotate_discovery({"daily_horizon_evidence":[{"horizon":1}]})
if __name__=="__main__":unittest.main()
