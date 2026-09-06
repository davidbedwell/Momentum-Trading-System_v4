from __future__ import annotations

import json
import unittest

from MTS_V4.contracts import ResearchPhase
from MTS_V4.openai_compatible_provider import OpenAICompatibleResearchDirector
from MTS_V4.rd_codec import ResearchDecisionCodec, ResearchDecisionDecodeError


class V4ResearchDirectorCodecTests(unittest.TestCase):
    def test_provider_json_safe_serializes_user_defined_enum(self):
        self.assertEqual(
            OpenAICompatibleResearchDirector._json_safe(ResearchPhase.EXPLORATION),
            "EXPLORATION",
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
