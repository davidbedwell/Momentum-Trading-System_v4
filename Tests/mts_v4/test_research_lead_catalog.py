from __future__ import annotations

import unittest

from MTS_V4.concept_library import seed_market_concepts
from MTS_V4.research_leads import seed_external_research_leads


class ResearchLeadCatalogTests(unittest.TestCase):
    def test_leads_use_existing_non_authoritative_concept_transport(self):
        leads = seed_external_research_leads()
        payloads = {item["concept_id"]: item for item in seed_market_concepts().payloads()}
        self.assertGreaterEqual(len(leads), 10)
        for lead in leads:
            payload = payloads[lead.lead_id]
            metadata = payload["metadata"]
            self.assertTrue(metadata["research_lead"])
            self.assertEqual(metadata["scientific_authority"], "AI_RESEARCH_DIRECTOR_ONLY")
            self.assertTrue(metadata["rd_may_test_modify_combine_defer_reject_or_replace"])
            self.assertFalse(metadata["deterministic_thresholds"])
            self.assertFalse(metadata["deterministic_signal"])

    def test_human_threshold_examples_remain_nonbinding(self):
        lead = next(x for x in seed_external_research_leads() if x.lead_id == "lead.low_float_rvol_catalyst")
        metadata = lead.concept_metadata()
        self.assertEqual(metadata["human_seed_examples_only"]["float_shares"], 10_000_000)
        self.assertEqual(metadata["human_seed_examples_only"]["relative_volume"], 5.0)
        self.assertFalse(metadata["deterministic_thresholds"])


if __name__ == "__main__":
    unittest.main()
