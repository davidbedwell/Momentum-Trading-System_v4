from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from MTS_V4.cache import TemporaryResearchCache
from MTS_V4.campaign import CheckpointedCampaignRunner
from MTS_V4.checkpoint import JsonCampaignCheckpointStore
from MTS_V4.contracts import AnalysisRequest, AnalysisResult, EvidenceDescriptor, ResearchDecision, ResearchPhase, SubjectMetadata
from MTS_V4.method_catalog import MethodCatalog, MethodSpec
from MTS_V4.nexus import InMemoryResearchNexus
from MTS_V4.orchestrator import ResearchLoopOrchestrator
from MTS_V4.validation import ObjectiveContractValidator


class _Analysis:
    def __init__(self):
        self.executed = []

    def execute(self, request, evidence_payloads):
        self.executed.append(request.request_id)
        return AnalysisResult(
            result_id=f"result:{request.request_id}",
            request_id=request.request_id,
            subject_id=request.subject_id,
            method_id=request.method_id,
            outputs={"value": 1.0},
            evidence_ids=request.evidence_ids,
        )


class _RD:
    def __init__(self):
        self.resume_calls = []
        self.interpret_calls = 0

    @staticmethod
    def _request(request_id, evidence_id="ev:1"):
        return AnalysisRequest(
            request_id=request_id,
            subject_id="AAPL",
            question="AI-authored beta research question",
            method_id="analysis.fixture",
            evidence_ids=(evidence_id,),
            parameters={},
            research_phase=ResearchPhase.EXPLORATION,
        )

    def begin_research(self, **kwargs):
        return ResearchDecision(
            continue_research=True,
            next_request=self._request("r:1"),
            research_state={"frontier": "beta-resume-proof"},
        )

    def resume_research(self, *, evidence_continuity, prior_decision, evidence, **kwargs):
        self.resume_calls.append(evidence_continuity)
        # Changed evidence is not deterministically rejected. RD explicitly
        # chooses the newly reacquired evidence identity for its fresh request.
        return ResearchDecision(
            continue_research=True,
            next_request=self._request("r:resume", evidence[0].evidence_id),
            research_state={
                **dict(prior_decision.research_state),
                "continuity_reviewed": evidence_continuity["status"],
            },
        )

    def repair_request(self, **kwargs):
        raise AssertionError("fixture requests are objectively valid")

    def interpret_result(self, **kwargs):
        self.interpret_calls += 1
        if self.interpret_calls == 1:
            evidence_id = kwargs["result"].evidence_ids[0]
            return ResearchDecision(
                continue_research=True,
                next_request=self._request("r:2", evidence_id),
                research_state={"frontier": "after-first-analysis"},
            )
        return ResearchDecision(
            continue_research=False,
            research_state={"frontier": "closed-by-rd"},
            close_reason="RD_COMPLETE",
        )


class V4CampaignResumeTests(unittest.TestCase):
    def _runtime(self, directory):
        rd = _RD()
        analysis = _Analysis()
        cache = TemporaryResearchCache()
        catalog = MethodCatalog(
            [MethodSpec(method_id="analysis.fixture", artifact_types=("NORMALIZED_DATASET",))]
        )
        orchestrator = ResearchLoopOrchestrator(
            mission="discover reproducible exploitable market conditions",
            rd=rd,
            validator=ObjectiveContractValidator(catalog),
            analysis=analysis,
            nexus=InMemoryResearchNexus(),
            cache=cache,
            available_methods=catalog.capability_payloads(),
        )
        store = JsonCampaignCheckpointStore(Path(directory) / "campaign.json")
        runner = CheckpointedCampaignRunner(
            orchestrator=orchestrator,
            cache=cache,
            checkpoint_store=store,
        )
        return rd, analysis, cache, store, runner

    @staticmethod
    def _evidence(
        cache,
        *,
        evidence_id="ev:1",
        coverage_end="2026-01-01",
        row_count=100,
        cache_key="cache:1",
    ):
        cache.put(cache_key, [{"close": 100.0}])
        return EvidenceDescriptor(
            evidence_id=evidence_id,
            subject_id="AAPL",
            evidence_type="OHLCV",
            artifact_type="NORMALIZED_DATASET",
            source_identity="fixture-source",
            coverage_start="2020-01-01",
            coverage_end=coverage_end,
            row_count=row_count,
            schema=("close",),
            cache_key=cache_key,
            provenance={"vendor": "fixture"},
            neutral_semantics="Observed market evidence.",
        )

    def test_same_evidence_resume_preserves_ai_state_without_new_scientific_resume_decision(self):
        with tempfile.TemporaryDirectory() as directory:
            rd, analysis, cache, store, runner = self._runtime(directory)
            subject = SubjectMetadata(subject_id="AAPL", ticker="AAPL")
            evidence = self._evidence(cache)
            first = runner.run_new(
                campaign_id="campaign:1",
                subject=subject,
                evidence=(evidence,),
                max_analyses=1,
            )
            self.assertFalse(first.closed)
            self.assertEqual(first.close_reason, "ANALYSIS_BUDGET_EXHAUSTED")
            self.assertIsNotNone(store.load())

            cache.release(evidence.cache_key)
            cache.purge_released()
            reacquired = self._evidence(cache, cache_key="cache:reacquired")
            resumed = runner.resume(reacquired_evidence=(reacquired,), max_analyses=2)

            self.assertTrue(resumed.closed)
            self.assertEqual(resumed.close_reason, "RD_COMPLETE")
            self.assertEqual(rd.resume_calls, [])
            self.assertEqual(analysis.executed, ["r:1", "r:2"])
            self.assertIsNone(store.load())
            self.assertEqual(cache.active_keys(), ())

    def test_changed_evidence_is_reported_to_rd_and_rd_decides_to_continue(self):
        with tempfile.TemporaryDirectory() as directory:
            rd, analysis, cache, store, runner = self._runtime(directory)
            subject = SubjectMetadata(subject_id="AAPL", ticker="AAPL")
            evidence = self._evidence(cache)
            runner.run_new(
                campaign_id="campaign:2",
                subject=subject,
                evidence=(evidence,),
                max_analyses=1,
            )

            cache.release(evidence.cache_key)
            cache.purge_released()
            changed = self._evidence(
                cache,
                evidence_id="ev:changed",
                coverage_end="2026-01-02",
                row_count=101,
                cache_key="cache:changed",
            )
            resumed = runner.resume(reacquired_evidence=(changed,), max_analyses=2)

            self.assertTrue(resumed.closed)
            self.assertEqual(len(rd.resume_calls), 1)
            continuity = rd.resume_calls[0]
            self.assertEqual(continuity["status"], "CHANGED")
            changed_fields = {item["field"] for item in continuity["differences"]}
            self.assertEqual(changed_fields, {"coverage_end", "row_count"})
            self.assertEqual(continuity["scientific_consequence"], "AI_RESEARCH_DIRECTOR_DECIDES")
            self.assertIn("r:resume", analysis.executed)
            self.assertIsNone(store.load())


if __name__ == "__main__":
    unittest.main()
