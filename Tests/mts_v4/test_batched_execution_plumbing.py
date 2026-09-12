from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from MTS_V4.batch_contracts import (
    BatchResearchDecision,
    ResearchPackagePlan,
    ScientificAnalysisSpecification,
    ScientificInputReference,
)
from MTS_V4.batch_rd_codec import BatchResearchDecisionCodec
from MTS_V4.batch_research_recording import BatchCampaignResearchRecorder
from MTS_V4.contracts import ResearchPhase, SubjectMetadata
from MTS_V4.research_package_store import JsonResearchPackageStore
from MTS_V4.standard_methods import compose_aligned_dataset


class BatchedExecutionPlumbingTests(unittest.TestCase):
    def test_compose_moves_internal_alignment_key_when_scientific_output_uses_that_name(self):
        result = compose_aligned_dataset(
            {
                "left": ({"value": 10}, {"value": 20}),
                "right": ({"other": 1}, {"other": 2}),
            },
            {
                "alignment": [
                    {"input_name": "left", "key": {"mode": "ROW_POSITION"}},
                    {"input_name": "right", "key": {"mode": "ROW_POSITION"}},
                ],
                "selections": [
                    {
                        "input_name": "left",
                        "column": "value",
                        "output_name": "alignment_key",
                    },
                    {
                        "input_name": "right",
                        "column": "other",
                        "output_name": "other_value",
                    },
                ],
                "join_type": "INNER",
            },
        )

        self.assertEqual(result["alignment_key_column"], "__mts_alignment_key")
        rows = result["derived_datasets"]["composed_dataset"]
        self.assertEqual(rows[0]["alignment_key"], 10)
        self.assertEqual(rows[0]["__mts_alignment_key"], 0)
        self.assertEqual(rows[1]["alignment_key"], 20)
        self.assertEqual(rows[1]["__mts_alignment_key"], 1)

    def test_batch_codec_accepts_explicit_rp_closure_while_subject_continues(self):
        decision = BatchResearchDecisionCodec.decode(
            json.dumps(
                {
                    "continue_research": True,
                    "research_packages": [
                        {
                            "rp_id": "rp:new",
                            "parent_rp_id": None,
                            "objective": "Test another scientific proposition.",
                            "decision_boundary": None,
                            "analyses": [
                                {
                                    "analysis_id": "analysis:new",
                                    "rp_id": "rp:new",
                                    "question_id": "q:new",
                                    "parent_question_id": None,
                                    "parent_rp_id": None,
                                    "subject_id": "equity:AMD",
                                    "question": "Does the new proposition hold?",
                                    "method_id": "analysis.descriptive.statistics",
                                    "inputs": [
                                        {
                                            "role": "raw",
                                            "evidence_id": "ev:amd",
                                            "analysis_id": None,
                                            "dataset_name": None,
                                        }
                                    ],
                                    "parameters": {"columns": ["close"]},
                                    "research_phase": "EXPLORATION",
                                    "rationale": "AI-authored rationale",
                                }
                            ],
                        }
                    ],
                    "rp_closures": [
                        {
                            "rp_id": "rp:old",
                            "close_reason": "This proposition is scientifically exhausted.",
                            "final_assessment": "No useful relationship survived.",
                        }
                    ],
                    "promote_findings": [],
                    "research_state": {},
                    "batch_interpretation": "One RP closed while another begins.",
                    "close_reason": None,
                }
            )
        )
        self.assertTrue(decision.continue_research)
        self.assertEqual(decision.rp_closures[0].rp_id, "rp:old")
        self.assertEqual(decision.research_packages[0].rp_id, "rp:new")

    def test_batch_recorder_creates_child_rp_even_when_child_precedes_parent_in_decision(self):
        subject = SubjectMetadata(subject_id="equity:AMD", ticker="AMD")
        child_analysis = ScientificAnalysisSpecification(
            analysis_id="child:a",
            rp_id="rp:child",
            question_id="q:child",
            subject_id=subject.subject_id,
            question="Child question",
            method_id="analysis.descriptive.statistics",
            inputs=(ScientificInputReference(role="raw", evidence_id="ev:amd"),),
            parameters={"columns": ["close"]},
            research_phase=ResearchPhase.EXPLORATION,
            rationale="Child rationale",
            parent_rp_id="rp:parent",
        )
        parent_analysis = ScientificAnalysisSpecification(
            analysis_id="parent:a",
            rp_id="rp:parent",
            question_id="q:parent",
            subject_id=subject.subject_id,
            question="Parent question",
            method_id="analysis.descriptive.statistics",
            inputs=(ScientificInputReference(role="raw", evidence_id="ev:amd"),),
            parameters={"columns": ["close"]},
            research_phase=ResearchPhase.EXPLORATION,
            rationale="Parent rationale",
        )
        decision = BatchResearchDecision(
            continue_research=True,
            research_packages=(
                ResearchPackagePlan(
                    rp_id="rp:child",
                    parent_rp_id="rp:parent",
                    objective="Child objective",
                    analyses=(child_analysis,),
                ),
                ResearchPackagePlan(
                    rp_id="rp:parent",
                    objective="Parent objective",
                    analyses=(parent_analysis,),
                ),
            ),
        )

        with tempfile.TemporaryDirectory() as directory:
            store = JsonResearchPackageStore(Path(directory))
            recorder = BatchCampaignResearchRecorder(package_store=store)
            recorder.record_plan(
                campaign_id="campaign:test",
                subject=subject,
                decision=decision,
            )
            parent = store.load("rp:parent")
            child = store.load("rp:child")
            self.assertIsNotNone(parent)
            self.assertIsNotNone(child)
            self.assertEqual(child.parent_rp_id, "rp:parent")


if __name__ == "__main__":
    unittest.main()
