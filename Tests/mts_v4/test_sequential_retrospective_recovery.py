from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from MTS_V4.cross_subject_memory import ResearchFrontierState, ScientificMemoryRecord
from MTS_V4.cross_subject_memory_store import JsonCrossSubjectScientificMemoryStore
from MTS_V4.research_package_store import JsonResearchPackageStore
from scripts.run_sequential_retrospective_recovery import (
    SEQUENCE,
    _compact_prior_subject_science,
    _discover_historical_subject_candidates,
    _parse_historical_overrides,
    _resolve_historical_subject_dir,
)


class SequentialRetrospectiveRecoveryTests(unittest.TestCase):
    def test_sequence_is_aapl_then_msft_then_xom(self) -> None:
        self.assertEqual(SEQUENCE, ("AAPL", "MSFT", "XOM"))

    def test_historical_candidate_discovery_does_not_rank_multiple_histories(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            for run_name in ("mts-v4-old-a", "mts-v4-old-b"):
                subject = root / run_name / "subjects" / "AAPL"
                subject.mkdir(parents=True)
                (subject / "research_nexus.json").write_text(
                    json.dumps({"format": "MTS_V4_RESEARCH_NEXUS_V1"}),
                    encoding="utf-8",
                )

            candidates = _discover_historical_subject_candidates(root, "AAPL")
            self.assertEqual(len(candidates), 2)
            with self.assertRaisesRegex(RuntimeError, "multiple preserved historical subject directories"):
                _resolve_historical_subject_dir(root, "AAPL", {})

    def test_explicit_historical_override_resolves_ambiguous_history(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            paths = []
            for run_name in ("mts-v4-old-a", "mts-v4-old-b"):
                subject = root / run_name / "subjects" / "AAPL"
                subject.mkdir(parents=True)
                (subject / "research_nexus.json").write_text(
                    json.dumps({"format": "MTS_V4_RESEARCH_NEXUS_V1"}),
                    encoding="utf-8",
                )
                paths.append(subject.resolve())

            overrides = _parse_historical_overrides((f"AAPL={paths[1]}",))
            self.assertEqual(_resolve_historical_subject_dir(root, "AAPL", overrides), paths[1])

    def test_prior_subject_science_exposes_findings_without_analysis_payloads(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            package_path = root / "mts-v4-completed" / "research_packages" / "RP-AMD-1.json"
            package_path.parent.mkdir(parents=True)
            package_path.write_text(
                json.dumps(
                    {
                        "format": JsonResearchPackageStore.FORMAT,
                        "research_package": {
                            "rp_id": "RP-AMD-1",
                            "campaign_id": "campaign-amd",
                            "subject_id": "equity:AMD",
                            "status": "CLOSED",
                            "originating_question": "Does it transfer?",
                            "originating_rationale": "Test transferability.",
                            "hypotheses": ["h1"],
                            "predictive_hypotheses": [{"hypothesis_id": "ph1"}],
                            "findings": [{"finding_id": "f1", "summary": "finding"}],
                            "unresolved_issues": ["u1"],
                            "analyses": [{"analysis_id": "a1", "payload": "must not be exposed"}],
                            "close_reason": "resolved",
                            "final_assessment": "assessment",
                        },
                    }
                ),
                encoding="utf-8",
            )

            context = _compact_prior_subject_science(root, active_ticker="MSFT")
            packages = context["subjects"][0]["research_packages"]
            self.assertEqual(len(packages), 1)
            package = packages[0]
            self.assertEqual(package["findings"][0]["finding_id"], "f1")
            self.assertEqual(package["predictive_hypotheses"][0]["hypothesis_id"], "ph1")
            self.assertEqual(package["final_assessment"], "assessment")
            self.assertNotIn("analysis_lineage", package)
            self.assertNotIn("analyses", package)
            self.assertFalse(context["policy"]["deterministic_scientific_ranking"])
            self.assertTrue(context["policy"]["rd_may_test_challenge_reformulate_condition_defer_or_ignore"])

    def test_canonical_memory_store_preserves_generalization_frontier(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            memory_path = root / "mts-v4-memory" / "cross_subject_memory.json"
            store = JsonCrossSubjectScientificMemoryStore(memory_path)
            store.publish(
                ScientificMemoryRecord(
                    record_id="r1",
                    subject_id="equity:NVDA",
                    kind="TENTATIVE_HYPOTHESIS",
                    summary="candidate pathway",
                )
            )
            store.set_frontier(
                ResearchFrontierState(
                    version=6,
                    summary="generalization frontier",
                    candidate_generalizations=("test conditional transfer",),
                    open_questions=("does it transfer?",),
                    source_record_ids=("r1",),
                )
            )

            selection = JsonCrossSubjectScientificMemoryStore.discover_current(root)
            self.assertIsNotNone(selection)
            assert selection is not None
            self.assertEqual(selection.store.frontier().version, 6)
            self.assertEqual(
                selection.store.frontier().candidate_generalizations,
                ("test conditional transfer",),
            )


if __name__ == "__main__":
    unittest.main()
