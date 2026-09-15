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
from MTS_V4.batch_research_recording import (
    BatchCampaignResearchRecorder,
    BatchResearchRecordingError,
)
from MTS_V4.contracts import ResearchPhase, SubjectMetadata
from MTS_V4.research_package import ResearchAnalysisRecord, ResearchPackage
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

    def test_v2_candidate_uses_executable_positive_net_expectancy_not_old_win_rate(self):
        with tempfile.TemporaryDirectory() as directory:
            store = JsonResearchPackageStore(Path(directory) / "research_packages")
            recorder = BatchCampaignResearchRecorder(package_store=store)
            package = ResearchPackage(
                rp_id="RP-AAPL-V2", subject_id="equity:AAPL", campaign_id="campaign:aapl",
                originating_question="Does context alter the prior science?",
                originating_rationale="Governed context-enriched reconsideration.",
                analyses=(ResearchAnalysisRecord(
                    request_id="request:1", question_id="question:1", method_id="analysis.test",
                    parameters={}, evidence_ids=("evidence:1",), analysis_inputs=(),
                    result_id="result:1", execution_status="SUCCESS",
                    future_information={"contains_future_information": True},
                ),),
            )
            store.create(package)
            update = {
                "rp_id": package.rp_id,
                "action": "CREATE_TRADING_CANDIDATE_V2",
                "hypothesis_id": "hypothesis:aapl:v2",
                "statement": "A frozen context-conditioned relationship.",
                "success_definition": "Frozen chronological policy outcome.",
                "minimum_required_trials": 20,
                "source_result_ids": ["result:1"],
                "executable_policy": {
                    "entry": "observable entry", "direction": "long", "instrument": "equity",
                    "prediction_point": "daily close T", "favorable_exit": "frozen target",
                    "adverse_risk_unit": "frozen R", "stop_or_invalidation": "frozen stop",
                    "maximum_horizon": "20 sessions", "gap_fill_treatment": "next executable price",
                    "position_management": "none", "all_in_cost_assumption": "0.01R",
                    "applicable_population_or_regime": "frozen context",
                },
                "exploratory_candidacy_assessment": {
                    "mean_realized_gross_expectancy": 0.11,
                    "mean_estimated_all_in_cost": 0.01,
                    "mean_realized_net_expectancy": 0.10,
                    "expectancy_units": "R",
                    "chronological_policy_applied": True,
                    "post_exit_movement_credited": False,
                },
            }
            recorder.record_predictive_hypothesis_updates(
                BatchResearchDecision(continue_research=False, research_state={
                    "predictive_hypothesis_updates": [update]
                }),
                current_report=None,
            )
            recorded = store.load(package.rp_id).predictive_hypotheses[0]
            self.assertEqual(recorded.status, "CANDIDATE_EXPLORATORY")
            self.assertEqual(recorded.lifecycle_version, "TRADING_HYPOTHESIS_LIFECYCLE_V2")
            self.assertNotIn("success_rate", recorded.exploratory_candidacy_assessment)

            invalid = dict(update)
            invalid["hypothesis_id"] = "hypothesis:aapl:negative"
            invalid["exploratory_candidacy_assessment"] = {
                **update["exploratory_candidacy_assessment"],
                "mean_realized_gross_expectancy": 0.005,
                "mean_realized_net_expectancy": -0.005,
            }
            with self.assertRaisesRegex(BatchResearchRecordingError, "positive exploratory net expectancy"):
                recorder.record_predictive_hypothesis_updates(
                    BatchResearchDecision(continue_research=False, research_state={
                        "predictive_hypothesis_updates": [invalid]
                    }), current_report=None,
                )


if __name__ == "__main__":
    unittest.main()
