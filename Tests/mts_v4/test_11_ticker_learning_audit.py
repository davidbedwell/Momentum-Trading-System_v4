from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from scripts.audit_11_ticker_learning import build_audit

class ElevenTickerLearningAuditTests(unittest.TestCase):
    def test_aggregates_exact_sol_authored_frequency_without_inventing_science(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            state=root/"01-aapl"
            state.mkdir()
            (root/"sequential_revisit_manifest.json").write_text(json.dumps({
                "status":"COMPLETE",
                "results":[{"ticker":"AAPL","state_dir":str(state),"return_code":0,"status":"COMPLETED"}],
            }))
            decision={
                "research_state":{
                    "campaign_learning_audit_state":{
                        "known_theory_coverage":[{"theory_id":"T1","status":"TESTED_UNSUPPORTED"}],
                        "known_structure_applications":[{"application_id":"k1","structure_name":"prior structure"}],
                        "known_structure_opportunity_summary":{
                            "observation_months":10,
                            "raw_unique_opportunities":30,
                            "executable_nonoverlapping_unique_opportunities":20,
                            "positive_net_ev_candidate_unique_opportunities":10,
                        },
                        "novel_strategy_discoveries":[{"novelty_id":"n1","statement":"novel"}],
                        "cross_subject_generalizations":[{"generalization_id":"g1","statement":"general"}],
                    }
                }
            }
            (state/"batch_decisions.jsonl").write_text(json.dumps({"decision":decision})+"\n")
            telemetry={"event":"SOL_CALL_COMPLETE","operation":"BEGIN_BATCH_RESEARCH","usage":{"prompt_tokens":100,"completion_tokens":20},"estimated_call_cost_usd":0.5}
            (state/"sol_transport_telemetry.jsonl").write_text(json.dumps(telemetry)+"\n")
            report=build_audit(root)
            self.assertEqual(report["aggregate"]["subjects_present"],1)
            self.assertEqual(report["aggregate"]["sol_calls"],1)
            self.assertEqual(report["aggregate"]["known_theory_coverage_records"],1)
            self.assertEqual(report["aggregate"]["known_theory_status_counts"],{"TESTED_UNSUPPORTED":1})
            self.assertEqual(report["aggregate"]["mean_raw_unique_per_month"],3.0)
            self.assertEqual(report["aggregate"]["mean_executable_nonoverlapping_per_month"],2.0)
            self.assertEqual(report["aggregate"]["mean_positive_net_ev_candidate_per_month"],1.0)
            self.assertEqual(report["aggregate"]["novel_strategy_claims"],1)
            self.assertEqual(report["aggregate"]["generalization_claims"],1)

    def test_missing_frequency_is_reported_as_missing_not_estimated(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); state=root/"01-aapl"; state.mkdir()
            (root/"sequential_revisit_manifest.json").write_text(json.dumps({
                "status":"STOPPED",
                "results":[{"ticker":"AAPL","state_dir":str(state),"return_code":2,"status":"STOPPED"}],
            }))
            (state/"batch_decisions.jsonl").write_text(json.dumps({"decision":{"research_state":{"campaign_learning_audit_state":{}}}})+"\n")
            report=build_audit(root)
            self.assertEqual(report["aggregate"]["subjects_with_exact_opportunity_frequency"],0)
            self.assertNotIn("mean_raw_unique_per_month",report["aggregate"])

if __name__=="__main__":
    unittest.main()
