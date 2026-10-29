from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from MTS_V4.openai_compatible_provider import OpenAICompatibleResearchDirector


class _Response:
    def __init__(self, content: str) -> None:
        self._payload = json.dumps(
            {"choices": [{"message": {"content": content}}]}
        ).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self) -> bytes:
        return self._payload


class V4RDRepresentationRepairTests(unittest.TestCase):
    def test_missing_evidence_ids_is_returned_to_ai_for_authored_repair(self):
        malformed = json.dumps(
            {
                "continue_research": True,
                "next_request": {
                    "request_id": "r:bad",
                    "subject_id": "AAPL",
                    "question": "RD-authored question",
                    "method_id": "analysis.toolkit.scientific_function",
                    "analysis_inputs": [
                        {
                            "result_id": "analysis-result:1",
                            "output_path": ["derived_datasets", "forward_path_observations"],
                            "input_name": "forward_path_observations",
                        }
                    ],
                    "parameters": {
                        "tool_id": "scipy.stats.skew",
                        "args": [{"column": "terminal_directional_return"}],
                    },
                    "research_phase": "EXPLORATION",
                    "rationale": "RD chose this calculation.",
                },
                "promote_findings": [],
                "research_state": {},
                "close_reason": None,
            }
        )
        repaired = json.dumps(
            {
                "continue_research": True,
                "next_request": {
                    "request_id": "r:fixed",
                    "subject_id": "AAPL",
                    "question": "RD-authored question",
                    "method_id": "analysis.toolkit.scientific_function",
                    "evidence_ids": [],
                    "analysis_inputs": [
                        {
                            "result_id": "analysis-result:1",
                            "output_path": ["derived_datasets", "forward_path_observations"],
                            "input_name": "forward_path_observations",
                        }
                    ],
                    "parameters": {
                        "tool_id": "scipy.stats.skew",
                        "args": [{"column": "terminal_directional_return"}],
                    },
                    "research_phase": "EXPLORATION",
                    "rationale": "RD chose this calculation.",
                },
                "promote_findings": [],
                "research_state": {},
                "close_reason": None,
            }
        )
        calls = []

        def fake_urlopen(request, timeout):
            calls.append(json.loads(request.data.decode("utf-8")))
            return _Response(malformed if len(calls) == 1 else repaired)

        rd = OpenAICompatibleResearchDirector(
            base_url="http://127.0.0.1:8000",
            model="fixture-model",
        )
        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            decision = rd._request_decision(
                operation="INTERPRET_ANALYSIS_RESULT",
                mission="fixture mission",
                payload={},
            )

        self.assertEqual(len(calls), 2)
        self.assertEqual(decision.next_request.evidence_ids, ())
        self.assertEqual(
            decision.next_request.analysis_inputs[0].output_path,
            ("derived_datasets", "forward_path_observations"),
        )
        repair_message = json.loads(calls[1]["messages"][-1]["content"])
        self.assertEqual(repair_message["operation"], "REPAIR_DECISION_REPRESENTATION")
        self.assertIn("evidence_ids", repair_message["decode_defect"])

    def test_valid_decision_is_not_repaired_or_rewritten(self):
        valid = json.dumps(
            {
                "continue_research": False,
                "next_request": None,
                "promote_findings": [],
                "research_state": {"marker": "RD-authored"},
                "close_reason": "RD_DONE",
            }
        )
        calls = []

        def fake_urlopen(request, timeout):
            calls.append(json.loads(request.data.decode("utf-8")))
            return _Response(valid)

        rd = OpenAICompatibleResearchDirector(
            base_url="http://127.0.0.1:8000",
            model="fixture-model",
        )
        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            decision = rd._request_decision(
                operation="BEGIN_RESEARCH",
                mission="fixture mission",
                payload={},
            )

        self.assertEqual(len(calls), 1)
        self.assertFalse(decision.continue_research)
        self.assertEqual(decision.close_reason, "RD_DONE")
        self.assertEqual(decision.research_state["marker"], "RD-authored")


if __name__ == "__main__":
    unittest.main()
