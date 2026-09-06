from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from MTS_V4.checkpoint import CampaignCheckpoint, JsonCampaignCheckpointStore
from MTS_V4.contracts import (
    AnalysisRequest,
    EvidenceDescriptor,
    EvidenceMetadata,
    ResearchDecision,
    ResearchPhase,
    SubjectMetadata,
)
from MTS_V4.recovery import CampaignRecovery, EvidenceContinuityStatus


class V4CheckpointTests(unittest.TestCase):
    def _checkpoint(self):
        return CampaignCheckpoint(
            campaign_id="campaign:aapl:1",
            subject=SubjectMetadata(subject_id="AAPL", ticker="AAPL"),
            evidence_metadata=(
                EvidenceMetadata(
                    evidence_id="ev:1",
                    subject_id="AAPL",
                    evidence_type="OHLCV",
                    artifact_type="NORMALIZED_DATASET",
                    source_identity="fixture-source",
                    coverage_start="2020-01-01",
                    coverage_end="2026-01-01",
                    row_count=100,
                    schema=("date", "close", "volume"),
                    provenance={"vendor": "fixture"},
                    neutral_semantics="Observed price path and aggregate volume.",
                ),
            ),
            decision=ResearchDecision(
                continue_research=True,
                next_request=AnalysisRequest(
                    request_id="r:1",
                    subject_id="AAPL",
                    question="Is close associated with volume?",
                    method_id="analysis.relationship.redundancy",
                    evidence_ids=("ev:1",),
                    parameters={"columns": ["close", "volume"], "correlation_type": "pearson"},
                    research_phase=ResearchPhase.EXPLORATION,
                    rationale="AI-authored exploration",
                ),
                research_state={"frontier": ["relationship under investigation"]},
            ),
            analyses_executed=2,
            decisions_made=3,
        )

    def _reacquired(self, **overrides):
        values = {
            "evidence_id": "ev:1",
            "subject_id": "AAPL",
            "evidence_type": "OHLCV",
            "artifact_type": "NORMALIZED_DATASET",
            "source_identity": "fixture-source",
            "coverage_start": "2020-01-01",
            "coverage_end": "2026-01-01",
            "row_count": 100,
            "schema": ("date", "close", "volume"),
            "cache_key": "cache:new-session:1",
            "provenance": {"vendor": "fixture"},
            "neutral_semantics": "Observed price path and aggregate volume.",
        }
        values.update(overrides)
        return EvidenceDescriptor(**values)

    def test_checkpoint_round_trip_preserves_ai_state_without_raw_data(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "campaign.json"
            store = JsonCampaignCheckpointStore(path)
            checkpoint = self._checkpoint()
            store.save(checkpoint)
            serialized = path.read_text(encoding="utf-8")
            self.assertNotIn('"payload"', serialized)
            self.assertNotIn('"rows"', serialized)
            self.assertNotIn('"cache_key"', serialized)

            restored = store.load()
            self.assertEqual(restored.campaign_id, checkpoint.campaign_id)
            self.assertEqual(restored.subject.ticker, "AAPL")
            self.assertEqual(restored.evidence_metadata[0].schema, ("date", "close", "volume"))
            self.assertEqual(restored.decision.next_request.method_id, "analysis.relationship.redundancy")
            self.assertEqual(restored.decision.research_state["frontier"], ["relationship under investigation"])
            self.assertEqual(restored.analyses_executed, 2)

    def test_checkpoint_is_distinct_from_nexus_format(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "campaign.json"
            path.write_text(json.dumps({"format": "MTS_V4_RESEARCH_NEXUS_V1"}), encoding="utf-8")
            with self.assertRaises(Exception):
                JsonCampaignCheckpointStore(path).load()

    def test_recovery_accepts_new_cache_location_when_evidence_identity_matches(self):
        assessment = CampaignRecovery.compare(self._checkpoint(), (self._reacquired(),))
        self.assertEqual(assessment.status, EvidenceContinuityStatus.SAME)
        self.assertEqual(assessment.recovered[0].cache_key, "cache:new-session:1")
        self.assertEqual(assessment.differences, ())

    def test_changed_evidence_is_reported_to_rd_context_not_rejected(self):
        assessment = CampaignRecovery.compare(
            self._checkpoint(),
            (
                self._reacquired(
                    coverage_end="2026-01-02",
                    row_count=101,
                    schema=("date", "close", "volume", "revision_flag"),
                ),
            ),
        )
        self.assertEqual(assessment.status, EvidenceContinuityStatus.CHANGED)
        changed_fields = {difference.field for difference in assessment.differences}
        self.assertEqual(changed_fields, {"coverage_end", "row_count", "schema"})

    def test_missing_or_unexpected_identity_is_unverifiable_not_scientific_rejection(self):
        assessment = CampaignRecovery.compare(self._checkpoint(), ())
        self.assertEqual(assessment.status, EvidenceContinuityStatus.UNVERIFIABLE)
        self.assertEqual(assessment.missing_evidence_ids, ("ev:1",))


if __name__ == "__main__":
    unittest.main()
