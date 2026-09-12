from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from MTS_V4.predictive_provenance import relocate_predictive_hypothesis
from MTS_V4.research_package import (
    PredictiveHypothesisRecord,
    ResearchAnalysisRecord,
    ResearchPackage,
    ResearchQuestionRecord,
)
from MTS_V4.research_package_store import JsonResearchPackageStore


class PredictiveProvenanceRepairTests(unittest.TestCase):
    def test_relocation_preserves_frozen_hypothesis_and_audits_both_rps(self):
        with tempfile.TemporaryDirectory() as directory:
            store = JsonResearchPackageStore(Path(directory) / "research_packages")
            parent = ResearchPackage(
                rp_id="RP-AMD-001",
                subject_id="equity:AMD",
                campaign_id="campaign:amd",
                originating_question="Broad price-location discovery.",
                originating_rationale="Discovery lineage.",
            )
            store.create(parent)

            source = ResearchPackage(
                rp_id="RP-AMD-002",
                subject_id="equity:AMD",
                campaign_id="campaign:amd",
                originating_question="Dark-pool activity.",
                originating_rationale="Historical originating question.",
            )
            store.create(source)
            source = source.append_question(
                ResearchQuestionRecord(
                    question_id="Q1",
                    question="Threshold replication.",
                    rationale="Historical drift fixture.",
                    research_phase="EXPLORATION",
                )
            )
            source = source.append_analysis(
                ResearchAnalysisRecord(
                    request_id="request:1",
                    question_id="Q1",
                    method_id="analysis.descriptive.statistics",
                    parameters={},
                    evidence_ids=("evidence:1",),
                    analysis_inputs=(),
                    result_id="result:1",
                    execution_status="SUCCESS",
                    research_phase="EXPLORATION",
                )
            )
            hypothesis = PredictiveHypothesisRecord(
                hypothesis_id="AMD-H001",
                statement="Frozen AMD proposition.",
                success_definition="Frozen success rule.",
                minimum_required_trials=20,
                source_result_ids=("result:1",),
                discovered_with_lookahead=True,
            )
            source = source.append_predictive_hypothesis(hypothesis)
            store.save(source)

            repaired_source, target = relocate_predictive_hypothesis(
                store=store,
                hypothesis_id="AMD-H001",
                source_rp_id="RP-AMD-002",
                target_rp_id="RP-AMD-005",
                target_objective="Validate frozen AMD price-location hypotheses.",
                target_rationale="Repair semantic RP drift without changing H001.",
                parent_rp_id="RP-AMD-001",
            )

            self.assertEqual((), repaired_source.predictive_hypotheses)
            self.assertEqual(1, len(target.predictive_hypotheses))
            moved = target.predictive_hypotheses[0]
            self.assertEqual(hypothesis, moved)
            self.assertEqual("RP-AMD-001", target.parent_rp_id)
            self.assertEqual("Dark-pool activity.", repaired_source.originating_question)
            self.assertEqual("Validate frozen AMD price-location hypotheses.", target.originating_question)
            self.assertEqual(1, len(repaired_source.state_transitions))
            self.assertEqual(1, len(target.state_transitions))
            self.assertFalse(
                repaired_source.state_transitions[0].state["scientific_definition_changed"]
            )
            self.assertFalse(target.state_transitions[0].state["scientific_definition_changed"])
            self.assertEqual(
                ["RP-AMD-002"],
                target.state_transitions[0].state["source_result_rp_ids"],
            )


if __name__ == "__main__":
    unittest.main()
