from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from MTS_V4.analysis import ExactMethodAnalysisExecutor, RegisteredAnalysisMethod
from MTS_V4.cache import TemporaryResearchCache
from MTS_V4.checkpoint import CampaignCheckpoint
from MTS_V4.contracts import (
    AnalysisRequest,
    AnalysisResultInput,
    AnalysisResultMetadata,
    EvidenceDescriptor,
    EvidenceMetadata,
    Finding,
    ResearchDecision,
    ResearchPhase,
    SubjectMetadata,
)
from MTS_V4.intake import IntakeEngine, IntakePayload
from MTS_V4.method_catalog import MethodCatalog, MethodSpec
from MTS_V4.nexus import InMemoryResearchNexus, NexusError
from MTS_V4.openai_compatible_provider import OpenAICompatibleResearchDirector
from MTS_V4.orchestrator import ResearchLoopOrchestrator
from MTS_V4.recovery import CampaignRecovery, EvidenceContinuityStatus
from MTS_V4.validation import ObjectiveContractValidator


class _TimestampedSource:
    def __init__(self, acquired_at: str, close: float = 100.0):
        self.acquired_at = acquired_at
        self.close = close

    def acquire(self, subject):
        yield IntakePayload(
            payload=[{"date": "2026-01-01", "close": self.close}],
            evidence_type="OHLCV",
            artifact_type="NORMALIZED_DATASET",
            source_identity="fixture-source",
            coverage_start="2026-01-01",
            coverage_end="2026-01-01",
            row_count=1,
            schema=("date", "close"),
            provenance={"vendor": "fixture", "acquired_at_utc": self.acquired_at},
            neutral_semantics="Observed price path.",
        )


class _FutureRD:
    def __init__(self):
        self.seen_results = []

    def begin_research(self, **kwargs):
        return ResearchDecision(
            continue_research=True,
            next_request=AnalysisRequest(
                request_id="req:future",
                subject_id="AAPL",
                question="Measure a forward path selected by RD.",
                method_id="analysis.future",
                evidence_ids=("ev:1",),
                analysis_inputs=(),
                parameters={},
                research_phase=ResearchPhase.EXPLORATION,
            ),
        )

    def interpret_result(self, *, result, **kwargs):
        self.seen_results.append(result)
        if len(self.seen_results) == 1:
            return ResearchDecision(
                continue_research=True,
                next_request=AnalysisRequest(
                    request_id="req:chain",
                    subject_id="AAPL",
                    question="Analyze the RD-selected derived forward observations.",
                    method_id="analysis.chain",
                    evidence_ids=(),
                    analysis_inputs=(
                        AnalysisResultInput(
                            result_id=result.result_id,
                            output_path=("derived_datasets", "forward"),
                            input_name="forward",
                        ),
                    ),
                    parameters={},
                    research_phase=ResearchPhase.EXPLORATION,
                ),
            )
        return ResearchDecision(continue_research=False, close_reason="RD_COMPLETE")

    def repair_request(self, **kwargs):
        raise AssertionError(kwargs.get("defects"))

    def resume_research(self, **kwargs):
        raise AssertionError("not used")


class V4IntegrityRepairTests(unittest.TestCase):
    def test_evidence_identity_ignores_acquisition_time_but_changes_with_content(self):
        cache = TemporaryResearchCache()
        intake = IntakeEngine(cache)
        subject = SubjectMetadata(subject_id="AAPL", ticker="AAPL")
        first = intake.ingest(subject=subject, source=_TimestampedSource("2026-09-07T20:00:00Z"))[0]
        second = intake.ingest(subject=subject, source=_TimestampedSource("2026-09-07T21:00:00Z"))[0]
        changed = intake.ingest(subject=subject, source=_TimestampedSource("2026-09-07T22:00:00Z", close=101.0))[0]
        self.assertEqual(first.evidence_id, second.evidence_id)
        self.assertEqual(first.content_identity, second.content_identity)
        self.assertNotEqual(first.evidence_id, changed.evidence_id)
        self.assertNotEqual(first.content_identity, changed.content_identity)

    def test_nexus_refuses_evidence_identity_overwrite_and_validates_finding_lineage(self):
        nexus = InMemoryResearchNexus()
        nexus.upsert_subject(SubjectMetadata(subject_id="AAPL", ticker="AAPL"))
        evidence = EvidenceMetadata(
            evidence_id="ev:1",
            subject_id="AAPL",
            evidence_type="OHLCV",
            artifact_type="NORMALIZED_DATASET",
            source_identity="fixture",
            coverage_start="2026-01-01",
            coverage_end="2026-01-02",
            row_count=2,
            schema=("close",),
            provenance={"vendor": "fixture"},
            content_identity="sha256:one",
        )
        nexus.upsert_evidence_metadata(evidence)
        with self.assertRaisesRegex(NexusError, "different metadata"):
            nexus.upsert_evidence_metadata(
                EvidenceMetadata(
                    **{**evidence.__dict__}  # pragma: no cover - slots prevents this path
                )
            )

    def test_nexus_rejects_unknown_result_reference_without_judging_science(self):
        nexus = InMemoryResearchNexus()
        nexus.upsert_subject(SubjectMetadata(subject_id="AAPL", ticker="AAPL"))
        nexus.upsert_evidence_metadata(
            EvidenceMetadata(
                evidence_id="ev:1",
                subject_id="AAPL",
                evidence_type="OHLCV",
                artifact_type="NORMALIZED_DATASET",
                source_identity="fixture",
                coverage_start=None,
                coverage_end=None,
                row_count=1,
                schema=("close",),
            )
        )
        with self.assertRaisesRegex(NexusError, "unknown result_id"):
            nexus.publish_finding(
                Finding(
                    finding_id="f:bad",
                    subject_id="AAPL",
                    statement="Arbitrary scientific statement is not judged here.",
                    supporting_result_ids=("result:missing",),
                    evidence_ids=("ev:1",),
                    metadata={"unanticipated_scientific_label": "allowed"},
                )
            )
        nexus.register_analysis_result_metadata(
            AnalysisResultMetadata(
                result_id="result:1",
                request_id="req:1",
                subject_id="AAPL",
                method_id="analysis.fixture",
                evidence_ids=("ev:1",),
            )
        )
        nexus.publish_finding(
            Finding(
                finding_id="f:ok",
                subject_id="AAPL",
                statement="Arbitrary scientific statement is accepted with valid lineage.",
                supporting_result_ids=("result:1",),
                evidence_ids=("ev:1",),
                metadata={"unanticipated_scientific_label": "allowed"},
            )
        )
        self.assertEqual(nexus.get_finding("f:ok").metadata["unanticipated_scientific_label"], "allowed")

    def test_recovery_rebinds_legacy_checkpoint_identity_and_ignores_acquisition_timestamp(self):
        subject = SubjectMetadata(subject_id="AAPL", ticker="AAPL")
        expected = EvidenceMetadata(
            evidence_id="legacy:ev:1",
            subject_id="AAPL",
            evidence_type="OHLCV",
            artifact_type="NORMALIZED_DATASET",
            source_identity="fixture-source",
            coverage_start="2026-01-01",
            coverage_end="2026-01-01",
            row_count=1,
            schema=("date", "close"),
            provenance={"vendor": "fixture", "acquired_at_utc": "old"},
            neutral_semantics="Observed price path.",
            content_identity=None,
        )
        checkpoint = CampaignCheckpoint(
            campaign_id="campaign:legacy",
            subject=subject,
            evidence_metadata=(expected,),
            decision=ResearchDecision(continue_research=False, close_reason="fixture"),
            analyses_executed=0,
            decisions_made=1,
        )
        actual = EvidenceDescriptor(
            evidence_id="evidence:AAPL:new-content-derived-id",
            subject_id="AAPL",
            evidence_type="OHLCV",
            artifact_type="NORMALIZED_DATASET",
            source_identity="fixture-source",
            coverage_start="2026-01-01",
            coverage_end="2026-01-01",
            row_count=1,
            schema=("date", "close"),
            cache_key="cache:new",
            provenance={"vendor": "fixture", "acquired_at_utc": "new"},
            neutral_semantics="Observed price path.",
            content_identity="sha256:newly-computed",
        )
        assessment = CampaignRecovery.compare(checkpoint, (actual,))
        self.assertEqual(assessment.status, EvidenceContinuityStatus.SAME)
        self.assertEqual(assessment.recovered[0].evidence_id, "legacy:ev:1")
        self.assertEqual(assessment.recovered[0].cache_key, "cache:new")

    def test_forward_information_metadata_propagates_through_derived_chaining(self):
        cache = TemporaryResearchCache()
        cache.put("cache:1", [{"close": 100.0}, {"close": 101.0}])
        evidence = EvidenceDescriptor(
            evidence_id="ev:1",
            subject_id="AAPL",
            evidence_type="OHLCV",
            artifact_type="NORMALIZED_DATASET",
            source_identity="fixture",
            coverage_start=None,
            coverage_end=None,
            row_count=2,
            schema=("close",),
            cache_key="cache:1",
        )
        catalog = MethodCatalog(
            [
                MethodSpec(
                    method_id="analysis.future",
                    artifact_types=("NORMALIZED_DATASET",),
                    allows_future_information=True,
                ),
                MethodSpec(
                    method_id="analysis.chain",
                    artifact_types=("NORMALIZED_DATASET",),
                ),
            ]
        )
        analysis = ExactMethodAnalysisExecutor()
        analysis.register(
            RegisteredAnalysisMethod(
                "analysis.future",
                lambda payloads, parameters: {
                    "derived_datasets": {"forward": [{"value": 0.01}]},
                    "derived_dataset_catalog": {
                        "forward": {
                            "row_count": 1,
                            "schema": ["value"],
                            "output_path": ["derived_datasets", "forward"],
                            "temporary": True,
                        }
                    },
                },
            )
        )
        analysis.register(
            RegisteredAnalysisMethod(
                "analysis.chain",
                lambda payloads, parameters: {"count": len(payloads["forward"])},
            )
        )
        rd = _FutureRD()
        nexus = InMemoryResearchNexus()
        orchestrator = ResearchLoopOrchestrator(
            mission="fixture",
            rd=rd,
            validator=ObjectiveContractValidator(catalog),
            analysis=analysis,
            nexus=nexus,
            cache=cache,
            available_methods=catalog.capability_payloads(),
        )
        outcome = orchestrator.run(
            subject=SubjectMetadata(subject_id="AAPL", ticker="AAPL"),
            evidence=(evidence,),
            max_analyses=2,
        )
        self.assertTrue(outcome.closed)
        self.assertTrue(rd.seen_results[0].execution_metadata["future_information"]["contains_future_information"])
        self.assertTrue(rd.seen_results[1].execution_metadata["future_information"]["contains_future_information"])
        self.assertEqual(
            rd.seen_results[1].execution_metadata["future_information"]["inherited_from_result_ids"],
            [rd.seen_results[0].result_id],
        )
        self.assertTrue(
            nexus.get_analysis_result_metadata(rd.seen_results[1].result_id).future_information[
                "contains_future_information"
            ]
        )

    def test_transport_has_headroom_and_does_not_duplicate_complete_catalogs(self):
        evidence = tuple(
            EvidenceDescriptor(
                evidence_id=f"ev:{i}",
                subject_id="AAPL",
                evidence_type=f"TYPE_{i}",
                artifact_type="NORMALIZED_DATASET",
                source_identity=f"source-{i}",
                coverage_start="2024-01-01",
                coverage_end="2026-09-01",
                row_count=500,
                schema=tuple(f"field_{i}_{j}" for j in range(25)),
                cache_key=f"cache:{i}",
                provenance={"vendor": "fixture", "scope": "ticker"},
                neutral_semantics="Neutral source semantics without scientific interpretation. " * 3,
            )
            for i in range(6)
        )
        methods = tuple(
            {
                "method_id": f"analysis.fixture.{i}",
                "description": "Neutral capability description " * 4,
                "artifact_types": ["NORMALIZED_DATASET"],
                "parameters": [
                    {
                        "name": f"parameter_{j}",
                        "required": True,
                        "types": ["str"],
                        "allowed_values": [],
                        "meaning": "RD-selected value; deterministic code does not choose it.",
                    }
                    for j in range(4)
                ],
                "minimum_sample": 1,
                "exploration_allowed": True,
                "validation_allowed": True,
                "allows_future_information": False,
                "metadata": {},
            }
            for i in range(10)
        )
        payload = OpenAICompatibleResearchDirector._common_payload(
            subject=SubjectMetadata(subject_id="AAPL", ticker="AAPL"),
            evidence=evidence,
            available_methods=methods,
            nexus_context={},
        )
        requirements = payload["objective_execution_requirements"]
        self.assertNotIn("available_evidence", requirements)
        self.assertNotIn("method_contracts", requirements["analysis_request"])
        messages = OpenAICompatibleResearchDirector._decision_messages(
            operation="INTERPRET_ANALYSIS_RESULT",
            mission="fixture mission",
            payload=payload,
        )
        serialized_characters = len(json.dumps(messages, sort_keys=True))
        # Conservative CI guardrail for deterministic prompt growth. The live
        # Qwen tokenizer remains the final exact token-count authority.
        self.assertLess(serialized_characters, 90000)


if __name__ == "__main__":
    unittest.main()
