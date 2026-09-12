from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from MTS_V4.batch_contracts import (
    BatchResearchDecision,
    ResearchPackagePlan,
    ScientificAnalysisSpecification,
    ScientificInputReference,
)
from MTS_V4.batch_research_recording import BatchCampaignResearchRecorder
from MTS_V4.contracts import ResearchPhase, SubjectMetadata
from MTS_V4.research_package_store import JsonResearchPackageStore
from MTS_V4.sol_batch_provider import SolBatchResearchDirector


class BatchedPredictiveResearchPackageLifecycleTests(unittest.TestCase):
    SUBJECT = SubjectMetadata(subject_id="equity:AMD", ticker="AMD")
    CAMPAIGN_ID = "campaign:test-amd"

    @classmethod
    def _analysis(cls, *, analysis_id: str, rp_id: str) -> ScientificAnalysisSpecification:
        return ScientificAnalysisSpecification(
            analysis_id=analysis_id,
            rp_id=rp_id,
            question_id=f"question:{analysis_id}",
            subject_id=cls.SUBJECT.subject_id,
            question="Measure the RD-authored relationship without changing its scientific meaning.",
            method_id="analysis.descriptive.statistics",
            inputs=(
                ScientificInputReference(
                    role="source",
                    evidence_id="evidence:test",
                ),
            ),
            parameters={"columns": ["close"]},
            research_phase=ResearchPhase.EXPLORATION,
            rationale="Regression fixture for RP lifecycle ordering.",
        )

    @classmethod
    def _plan(cls, *, rp_id: str, analysis_id: str) -> ResearchPackagePlan:
        return ResearchPackagePlan(
            rp_id=rp_id,
            objective="Test one bounded predictive-discovery line.",
            analyses=(cls._analysis(analysis_id=analysis_id, rp_id=rp_id),),
            decision_boundary="Interpret the completed result before contingent follow-up.",
        )

    @staticmethod
    def _predictive_update(rp_id: str):
        return {
            "rp_id": rp_id,
            "action": "CREATE_TENTATIVE",
            "hypothesis_id": "hypothesis:test",
            "statement": "A frozen test proposition.",
            "success_definition": "Frozen objective outcome criterion.",
            "minimum_required_trials": 3,
            "source_result_ids": ["result:already-completed"],
        }

    def _provider(self, store: JsonResearchPackageStore) -> SolBatchResearchDirector:
        return SolBatchResearchDirector(
            research_package_store=store,
            base_url="http://example.invalid",
            model="test-model",
            required_subject_id=self.SUBJECT.subject_id,
            required_research_phase=ResearchPhase.EXPLORATION,
        )

    def test_new_same_decision_rp_is_not_treated_as_durable_for_predictive_update(self):
        """A brand-new RP cannot own completed source results from before it existed."""
        with tempfile.TemporaryDirectory() as directory:
            store = JsonResearchPackageStore(Path(directory) / "research_packages")
            provider = self._provider(store)
            rp_id = "RP-AMD-NEW"
            decision = BatchResearchDecision(
                continue_research=True,
                research_packages=(self._plan(rp_id=rp_id, analysis_id="analysis:new"),),
                research_state={
                    "predictive_hypothesis_updates": [self._predictive_update(rp_id)]
                },
            )

            defect = provider._batch_phase_defect(decision)

            self.assertIsNotNone(defect)
            self.assertIn("not yet durable", defect)

    def test_recorded_prior_plan_makes_rp_valid_for_later_predictive_update(self):
        """The planning-probe path must persist its RP before a later Sol interpretation."""
        with tempfile.TemporaryDirectory() as directory:
            store = JsonResearchPackageStore(Path(directory) / "research_packages")
            recorder = BatchCampaignResearchRecorder(package_store=store)
            provider = self._provider(store)
            rp_id = "RP-AMD-002"

            initial = BatchResearchDecision(
                continue_research=True,
                research_packages=(self._plan(rp_id=rp_id, analysis_id="analysis:initial"),),
            )
            recorder.record_plan(
                campaign_id=self.CAMPAIGN_ID,
                subject=self.SUBJECT,
                decision=initial,
            )
            self.assertIsNotNone(store.load(rp_id))

            later = BatchResearchDecision(
                continue_research=True,
                research_packages=(self._plan(rp_id=rp_id, analysis_id="analysis:later"),),
                research_state={
                    "predictive_hypothesis_updates": [self._predictive_update(rp_id)]
                },
            )

            self.assertIsNone(provider._batch_phase_defect(later))

    def test_unknown_rp_remains_rejected_even_without_new_batch_plan(self):
        with tempfile.TemporaryDirectory() as directory:
            store = JsonResearchPackageStore(Path(directory) / "research_packages")
            provider = self._provider(store)
            decision = BatchResearchDecision(
                continue_research=True,
                research_state={
                    "predictive_hypothesis_updates": [self._predictive_update("RP-UNKNOWN")]
                },
            )

            defect = provider._batch_phase_defect(decision)

            self.assertIsNotNone(defect)
            self.assertIn("RP-UNKNOWN", defect)
            self.assertIn("not yet durable", defect)


if __name__ == "__main__":
    unittest.main()
