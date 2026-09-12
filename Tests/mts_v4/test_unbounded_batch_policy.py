from __future__ import annotations

import json
import unittest

from MTS_V4.batch_contracts import BatchAnalysisRecord, BatchExecutionReport
from MTS_V4.batch_rd_codec import BatchResearchDecisionCodec
from MTS_V4.sol_batch_provider import SolBatchResearchDirector


class UnboundedBatchPolicyTests(unittest.TestCase):
    def _decision_payload(self, count: int) -> dict:
        packages = []
        for index in range(count):
            rp_id = f"rp:{index}"
            packages.append(
                {
                    "rp_id": rp_id,
                    "parent_rp_id": None,
                    "objective": f"Scientific objective {index}",
                    "decision_boundary": None,
                    "analyses": [
                        {
                            "analysis_id": f"analysis:{index}",
                            "rp_id": rp_id,
                            "question_id": f"question:{index}",
                            "parent_question_id": None,
                            "parent_rp_id": None,
                            "subject_id": "equity:AMD",
                            "question": f"Scientific question {index}",
                            "method_id": "analysis.descriptive.statistics",
                            "inputs": [
                                {
                                    "role": "market_data",
                                    "evidence_id": "evidence:amd",
                                    "analysis_id": None,
                                    "dataset_name": None,
                                }
                            ],
                            "parameters": {"columns": ["close"]},
                            "research_phase": "EXPLORATION",
                            "rationale": f"Scientific rationale {index}",
                        }
                    ],
                }
            )
        return {
            "continue_research": True,
            "research_packages": packages,
            "rp_closures": [],
            "promote_findings": [],
            "research_state": {},
            "research_progress": {
                "estimated_percent_complete": 25,
                "estimated_remaining_batches": 3,
                "estimated_remaining_sol_calls": 3,
                "estimate_confidence": "medium",
                "estimate_rationale": "Several independent scientific lines remain unresolved.",
            },
            "batch_interpretation": None,
            "close_reason": None,
        }

    def test_codec_does_not_impose_rp_quota_or_preferred_count(self):
        count = 64
        decision = BatchResearchDecisionCodec.decode(
            json.dumps(self._decision_payload(count))
        )
        self.assertEqual(len(decision.research_packages), count)
        self.assertEqual(
            [package.rp_id for package in decision.research_packages],
            [f"rp:{index}" for index in range(count)],
        )

    def test_consolidated_return_contains_every_rp_analysis_record(self):
        count = 64
        report = BatchExecutionReport(
            records=tuple(
                BatchAnalysisRecord(
                    analysis_id=f"analysis:{index}",
                    rp_id=f"rp:{index}",
                    status="SUCCESS",
                )
                for index in range(count)
            )
        )

        payload = SolBatchResearchDirector._report_payload(report)
        records = payload["records"]

        self.assertEqual(len(records), count)
        self.assertEqual(
            [record["analysis_id"] for record in records],
            [f"analysis:{index}" for index in range(count)],
        )
        self.assertEqual(
            [record["rp_id"] for record in records],
            [f"rp:{index}" for index in range(count)],
        )

    def test_sol_prompt_has_no_preferred_rp_count_and_requires_progress_estimate(self):
        messages = SolBatchResearchDirector._batch_messages(
            operation="BEGIN_BATCH_RESEARCH",
            mission="test mission",
            payload={},
        )
        system = messages[0]["content"]
        user = json.loads(messages[1]["content"])
        instructions = "\n".join(user["instructions"])
        schema = user["required_batch_decision_schema"]

        self.assertIn("as many Research Packages as you judge scientifically relevant", system)
        self.assertIn("Zero, one, or many Research Packages", system)
        self.assertNotIn("Create several Research Packages", system)
        self.assertIn("do not target any preferred RP count", instructions)
        self.assertIn("research_progress", schema)
        self.assertIn("estimated_percent_complete", schema["research_progress"])
        self.assertIn("estimated_remaining_sol_calls", schema["research_progress"])


if __name__ == "__main__":
    unittest.main()
