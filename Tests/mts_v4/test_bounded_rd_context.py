from __future__ import annotations

import json
import unittest

from MTS_V4.contracts import EvidenceDescriptor, SubjectMetadata
from MTS_V4.openai_compatible_provider import OpenAICompatibleResearchDirector


class V4BoundedRDContextTests(unittest.TestCase):
    @staticmethod
    def _historical_result(index: int) -> dict[str, object]:
        return {
            "result_id": f"result:{index}",
            "request_id": f"request:{index}",
            "subject_id": "equity:AAPL",
            "method_id": "analysis.descriptive.statistics",
            "evidence_ids": ["evidence:1"],
            "future_information": {"contains_future_information": False},
            "execution_metadata": {"execution_status": "EXECUTED_EXACT_REQUEST"},
        }

    @classmethod
    def _nexus_context(cls, historical_count: int, *, with_finding: bool = False):
        findings = []
        if with_finding:
            findings.append(
                {
                    "finding_id": "finding:significant",
                    "subject_id": "equity:AAPL",
                    "statement": "RD judged this result scientifically significant.",
                    "supporting_result_ids": ["result:2"],
                    "evidence_ids": ["evidence:1"],
                    "metadata": {"rd_authored": True},
                }
            )
        return {
            "subject": {"subject_id": "equity:AAPL", "ticker": "AAPL"},
            "evidence_metadata": [
                {
                    "evidence_id": "evidence:1",
                    "subject_id": "equity:AAPL",
                    "schema": ["date", "close"],
                }
            ],
            "significant_findings": findings,
            "historical_analysis_result_metadata": [
                cls._historical_result(index) for index in range(historical_count)
            ],
            "research_concepts": [
                {
                    "concept_id": "human.example",
                    "name": "Example",
                    "description": "Non-authoritative idea seed.",
                    "questions": ["Could this matter?"],
                }
            ],
            "campaign_analysis_result_catalog": [],
        }

    def test_unpromoted_analysis_audit_history_does_not_scale_transport(self):
        one = OpenAICompatibleResearchDirector._compact_nexus_context(
            self._nexus_context(1)
        )
        thousand = OpenAICompatibleResearchDirector._compact_nexus_context(
            self._nexus_context(1000)
        )
        self.assertNotIn("historical_analysis_result_metadata", thousand)
        self.assertNotIn("evidence_metadata", thousand)
        self.assertNotIn("subject", thousand)
        self.assertEqual(
            thousand["durable_inventory"]["historical_analysis_result_metadata_count"],
            1000,
        )
        self.assertEqual(thousand["historical_finding_support_lineage"], [])
        size_one = len(json.dumps(one, sort_keys=True))
        size_thousand = len(json.dumps(thousand, sort_keys=True))
        self.assertLess(size_thousand - size_one, 16)

    def test_rd_promoted_finding_and_its_exact_support_lineage_are_preserved(self):
        compact = OpenAICompatibleResearchDirector._compact_nexus_context(
            self._nexus_context(500, with_finding=True)
        )
        self.assertEqual(len(compact["significant_findings"]), 1)
        lineage = compact["historical_finding_support_lineage"]
        self.assertEqual(len(lineage), 1)
        self.assertEqual(lineage[0]["result_id"], "result:2")
        self.assertEqual(lineage[0]["method_id"], "analysis.descriptive.statistics")
        self.assertEqual(
            compact["durable_inventory"]["historical_analysis_result_metadata_count"],
            500,
        )
        self.assertFalse(
            compact["transport_policy"]["deterministic_scientific_ranking_or_selection"]
        )

    def test_common_payload_supplies_subject_and_evidence_once(self):
        evidence = EvidenceDescriptor(
            evidence_id="evidence:1",
            subject_id="equity:AAPL",
            evidence_type="OHLCV",
            artifact_type="NORMALIZED_DATASET",
            source_identity="fixture",
            coverage_start="2026-01-01",
            coverage_end="2026-01-02",
            row_count=2,
            schema=("date", "close"),
            cache_key="cache:1",
        )
        payload = OpenAICompatibleResearchDirector._common_payload(
            subject=SubjectMetadata(subject_id="equity:AAPL", ticker="AAPL"),
            evidence=(evidence,),
            available_methods=(),
            nexus_context=self._nexus_context(1000),
        )
        self.assertEqual(payload["subject"]["subject_id"], "equity:AAPL")
        self.assertEqual(payload["evidence"][0]["evidence_id"], "evidence:1")
        self.assertNotIn("subject", payload["nexus_context"])
        self.assertNotIn("evidence_metadata", payload["nexus_context"])

    def test_static_governance_contract_is_compact_but_complete_for_rejection_classes(self):
        requirements = OpenAICompatibleResearchDirector._execution_requirements(
            evidence=(), available_methods=()
        )
        self.assertIn("must be disclosed", requirements["visibility_rule"])
        self.assertTrue(requirements["analysis_request"]["no_hidden_defaults"])
        self.assertFalse(requirements["finding_envelope"]["deterministic_scientific_veto"])
        self.assertFalse(requirements["future_information_lineage"]["blanket_rejection"])
        self.assertIn("invalid_parameter_contract", requirements["hard_execution_failures"])
        self.assertLess(len(json.dumps(requirements, sort_keys=True)), 4000)


if __name__ == "__main__":
    unittest.main()
