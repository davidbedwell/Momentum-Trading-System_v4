from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from MTS_V4.contracts import EvidenceDescriptor, SubjectMetadata
from MTS_V4.openai_compatible_provider import OpenAICompatibleResearchDirector


class _Response:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        decision = {
            "continue_research": False,
            "next_request": None,
            "promote_findings": [],
            "research_state": {
                "questions_answered": 0,
                "questions_unanswered_lack_resource": 1,
                "lack_resource": [
                    {
                        "question": "example",
                        "required_resources": ["example resource"],
                        "reason": "not available",
                    }
                ],
            },
            "close_reason": "No other meaningful answerable question remains.",
        }
        document = {"choices": [{"message": {"content": json.dumps(decision)}}]}
        return json.dumps(document).encode("utf-8")


class ResourceGapPolicyTests(unittest.TestCase):
    def test_provider_tells_rd_to_record_resource_gap_and_continue_other_research(self):
        captured = {}

        def fake_urlopen(request, timeout):
            captured["body"] = json.loads(request.data.decode("utf-8"))
            return _Response()

        rd = OpenAICompatibleResearchDirector(
            base_url="http://127.0.0.1:8000",
            model="test-model",
        )
        subject = SubjectMetadata(subject_id="equity:AAPL", ticker="AAPL")
        evidence = (
            EvidenceDescriptor(
                evidence_id="evidence:1",
                subject_id="equity:AAPL",
                evidence_type="OHLCV",
                artifact_type="NORMALIZED_DATASET",
                source_identity="TEST",
                coverage_start="2026-01-01",
                coverage_end="2026-01-02",
                row_count=2,
                schema=("date", "close"),
                cache_key="cache:1",
            ),
        )

        with patch("urllib.request.urlopen", fake_urlopen):
            decision = rd.begin_research(
                mission="test mission",
                subject=subject,
                evidence=evidence,
                available_methods=(),
                nexus_context={},
            )

        self.assertEqual(decision.research_state["questions_unanswered_lack_resource"], 1)
        messages = captured["body"]["messages"]
        system = messages[0]["content"]
        user = json.loads(messages[1]["content"])
        instruction_text = "\n".join(user["instructions"])
        self.assertIn("LACK_RESOURCE", system)
        self.assertIn("continue to another scientifically useful answerable question", system)
        self.assertIn("rather than ending the campaign solely for that gap", instruction_text)
        self.assertIn("Do not promote missing tools", instruction_text)
        self.assertIn("questions_answered", user["required_decision_schema"]["research_state"])
        self.assertIn("questions_unanswered_lack_resource", user["required_decision_schema"]["research_state"])


if __name__ == "__main__":
    unittest.main()
