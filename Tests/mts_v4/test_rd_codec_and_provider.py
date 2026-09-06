from __future__ import annotations

import json
import unittest

from MTS_V4.contracts import EvidenceDescriptor, ResearchPhase
from MTS_V4.openai_compatible_provider import OpenAICompatibleResearchDirector
from MTS_V4.rd_codec import ResearchDecisionCodec, ResearchDecisionDecodeError


class V4ResearchDirectorCodecTests(unittest.TestCase):
    def test_provider_json_safe_serializes_user_defined_enum(self):
        self.assertEqual(
            OpenAICompatibleResearchDirector._json_safe(ResearchPhase.EXPLORATION),
            "EXPLORATION",
        )

    def test_every_deterministic_request_requirement_is_exposed_to_rd(self):
        evidence = EvidenceDescriptor(
            evidence_id="ev:1",
            subject_id="AAPL",
            evidence_type="OHLCV",
            artifact_type="NORMALIZED_DATASET",
            source_identity="fixture-source",
            coverage_start="2020-01-01",
            coverage_end="2026-01-01",
            row_count=100,
            schema=("date", "close", "volume"),
            cache_key="cache:private:1",
            provenance={"pulled_at": "2026-09-06T10:00:00-07:00"},
            neutral_semantics="Observed path and aggregate volume.",
        )
        method = {
            "method_id": "analysis.relationship.correlation",
            "artifact_types": ["NORMALIZED_DATASET"],
            "parameters": [
                {
                    "name": "columns",
                    "required": True,
                    "types": ["list"],
                    "exact_length": 2,
                    "minimum_length": None,
                    "maximum_length": None,
                    "allowed_values": [],
                    "meaning": "RD-selected pair of columns.",
                }
            ],
            "minimum_sample": 3,
            "exploration_allowed": True,
            "validation_allowed": True,
            "allows_future_information": False,
        }
        requirements = OpenAICompatibleResearchDirector._execution_requirements(
            evidence=(evidence,),
            available_methods=(method,),
        )
        self.assertIn("must be disclosed", requirements["visibility_rule"])
        self.assertEqual(
            requirements["analysis_request"]["method_contracts"][0]["parameters"][0]["exact_length"],
            2,
        )
        supplied = requirements["available_evidence"][0]
        self.assertEqual(supplied["schema"], ["date", "close", "volume"])
        self.assertEqual(supplied["source_identity"], "fixture-source")
        self.assertNotIn("cache_key", supplied)
        self.assertTrue(
            requirements["evidence_continuity"]["changed_is_not_scientific_failure"]
        )

    def test_continuation_requires_ai_authored_next_request(self):
        with self.assertRaisesRegex(
            ResearchDecisionDecodeError,
            "continuing research requires an AI-authored next_request",
        ):
            ResearchDecisionCodec.decode(
                json.dumps(
                    {
                        "continue_research": True,
                        "next_request": None,
                        "promote_findings": [],
                        "research_state": {},
                        "close_reason": None,
                    }
                )
            )

    def test_codec_does_not_invent_missing_scientific_fields(self):
        payload = {
            "continue_research": True,
            "next_request": {
                "request_id": "r:1",
                "subject_id": "AAPL",
                "question": "What relationship should be tested?",
                "evidence_ids": ["ev:1"],
                "parameters": {},
                "research_phase": "EXPLORATION",
            },
            "promote_findings": [],
            "research_state": {},
            "close_reason": None,
        }
        with self.assertRaisesRegex(
            ResearchDecisionDecodeError,
            "next_request missing required fields:.*method_id",
        ):
            ResearchDecisionCodec.decode(json.dumps(payload))

    def test_valid_ai_decision_round_trips_without_scientific_rewrite(self):
        payload = {
            "continue_research": True,
            "next_request": {
                "request_id": "r:2",
                "subject_id": "AAPL",
                "question": "Does close co-vary with volume under the selected window?",
                "method_id": "relationship.correlation",
                "evidence_ids": ["ev:1"],
                "parameters": {"columns": ["close", "volume"], "window": 30},
                "research_phase": "EXPLORATION",
                "rationale": "RD selected this as an exploratory relationship test.",
            },
            "promote_findings": [],
            "research_state": {"hypothesis": "volume-conditioned movement"},
            "close_reason": None,
        }
        decision = ResearchDecisionCodec.decode(json.dumps(payload))
        self.assertEqual(decision.next_request.method_id, "relationship.correlation")
        self.assertEqual(decision.next_request.parameters["window"], 30)
        self.assertEqual(
            decision.research_state["hypothesis"],
            "volume-conditioned movement",
        )

    def test_malformed_json_fails_instead_of_triggering_deterministic_scientific_repair(self):
        with self.assertRaises(ResearchDecisionDecodeError):
            ResearchDecisionCodec.decode("choose correlation and use close/volume")


if __name__ == "__main__":
    unittest.main()
