from __future__ import annotations

import tempfile
import unittest

from MTS_V4.bootstrap import build_runtime
from MTS_V4.contracts import AnalysisRequest, EvidenceDescriptor, Finding, ResearchDecision, ResearchPhase, SubjectMetadata
from MTS_V4.intake import IntakeEngine, IntakePayload
from MTS_V4.standard_methods import forward_path_measurement, percent_change_series, standard_method_catalog
from MTS_V4.validation import ObjectiveContractValidator


class _Source:
    def acquire(self, subject):
        yield IntakePayload(
            payload=[
                {"date": "2026-01-01", "close": 100.0, "volume": 10.0},
                {"date": "2026-01-02", "close": 101.0, "volume": 12.0},
                {"date": "2026-01-03", "close": 103.0, "volume": 15.0},
            ],
            evidence_type="OHLCV",
            artifact_type="NORMALIZED_DATASET",
            source_identity="synthetic-proof",
            coverage_start="2026-01-01",
            coverage_end="2026-01-03",
            row_count=3,
            schema=("date", "close", "volume"),
            provenance={"purpose": "test"},
            neutral_semantics="Observed price path and aggregate volume; no intent inferred.",
        )


class _FakeAIResearchDirector:
    def __init__(self):
        self.seen_result = None
        self.begin_context = None

    def begin_research(self, *, subject, evidence, nexus_context, **kwargs):
        self.begin_context = nexus_context
        return ResearchDecision(
            continue_research=True,
            next_request=AnalysisRequest(
                request_id="r:1",
                subject_id=subject.subject_id,
                question="Does close co-vary with volume in this exploratory evidence?",
                method_id="analysis.relationship.correlation",
                evidence_ids=(evidence[0].evidence_id,),
                parameters={"columns": ["close", "volume"], "correlation_type": "pearson"},
                research_phase=ResearchPhase.EXPLORATION,
                rationale="AI selected an exploratory relationship test.",
            ),
        )

    def repair_request(self, **kwargs):
        raise AssertionError("valid AI request should not require repair")

    def interpret_result(self, *, subject, result, **kwargs):
        self.seen_result = result
        return ResearchDecision(
            continue_research=False,
            promote_findings=(
                Finding(
                    finding_id="finding:correlation-proof",
                    subject_id=subject.subject_id,
                    statement="The synthetic proof produced a positive close-volume relationship.",
                    supporting_result_ids=(result.result_id,),
                    evidence_ids=result.evidence_ids,
                    metadata={
                        "significance": "AI judged the proof worth retaining for runtime verification.",
                        "status": "EXPLORATORY",
                    },
                ),
            ),
            close_reason="PROOF_COMPLETE",
        )


class V4StandardMethodsTests(unittest.TestCase):
    def test_catalog_requires_explicit_descriptive_columns(self):
        spec = standard_method_catalog().get("analysis.descriptive.statistics")
        columns = next(item for item in spec.parameters if item.name == "columns")
        self.assertTrue(columns.required)
        self.assertEqual(columns.minimum_length, 1)

    def test_correlation_contract_requires_exactly_two_columns(self):
        spec = standard_method_catalog().get("analysis.relationship.correlation")
        columns = next(item for item in spec.parameters if item.name == "columns")
        self.assertEqual(columns.exact_length, 2)

    def test_percent_change_requires_rd_selected_column_and_lag(self):
        spec = standard_method_catalog().get("analysis.transform.percent_change")
        parameters = {item.name: item for item in spec.parameters}
        self.assertEqual(set(parameters), {"column", "lag"})
        self.assertTrue(parameters["column"].required)
        self.assertTrue(parameters["lag"].required)
        self.assertEqual(parameters["lag"].minimum_value, 1)
        result = percent_change_series(
            {"ev:1": [{"close": 100.0}, {"close": 110.0}, {"close": 121.0}]},
            {"column": "close", "lag": 1},
        )
        self.assertEqual(result["observation_count"], 2)
        self.assertAlmostEqual(result["observations"][0]["value"], 0.10)
        self.assertAlmostEqual(result["observations"][1]["value"], 0.10)
        self.assertEqual(result["interpretation_boundary"], "MEASUREMENT_ONLY_RD_INTERPRETS")

    def test_forward_path_contract_exposes_all_scientific_parameters_and_lookahead_boundary(self):
        spec = standard_method_catalog().get("analysis.path.forward_measurement")
        parameters = {item.name: item for item in spec.parameters}
        self.assertEqual(set(parameters), {"price_column", "horizon", "direction"})
        self.assertTrue(all(item.required for item in parameters.values()))
        self.assertEqual(parameters["horizon"].minimum_value, 1)
        self.assertEqual(parameters["direction"].allowed_values, ("LONG", "SHORT"))
        self.assertTrue(spec.allows_future_information)
        self.assertTrue(spec.exploration_allowed)
        self.assertFalse(spec.validation_allowed)

    def test_forward_path_measurement_computes_path_without_interpreting_it(self):
        result = forward_path_measurement(
            {"ev:1": [{"close": 100.0}, {"close": 90.0}, {"close": 120.0}]},
            {"price_column": "close", "horizon": 2, "direction": "LONG"},
        )
        self.assertEqual(result["observation_count"], 1)
        observation = result["observations"][0]
        self.assertAlmostEqual(observation["terminal_directional_return"], 0.20)
        self.assertAlmostEqual(observation["max_favorable_directional_return"], 0.20)
        self.assertAlmostEqual(observation["max_adverse_directional_return"], -0.10)
        self.assertEqual(observation["bars_to_max_favorable"], 2)
        self.assertEqual(observation["bars_to_max_adverse"], 1)
        self.assertEqual(result["interpretation_boundary"], "LOOKAHEAD_MEASUREMENT_ONLY_RD_INTERPRETS")

    def test_forward_path_hidden_range_is_not_hidden_and_validation_use_is_blocked(self):
        evidence = EvidenceDescriptor(
            evidence_id="ev:1",
            subject_id="AAPL",
            evidence_type="OHLCV",
            artifact_type="NORMALIZED_DATASET",
            source_identity="fixture",
            coverage_start="2026-01-01",
            coverage_end="2026-01-03",
            row_count=3,
            schema=("close",),
            cache_key="cache:1",
        )
        request = AnalysisRequest(
            request_id="r:path",
            subject_id="AAPL",
            question="RD-authored path question",
            method_id="analysis.path.forward_measurement",
            evidence_ids=("ev:1",),
            parameters={"price_column": "close", "horizon": 0, "direction": "LONG"},
            research_phase=ResearchPhase.VALIDATION,
        )
        defects = ObjectiveContractValidator(standard_method_catalog()).validate(
            request, {"ev:1": evidence}
        )
        codes = {item.code for item in defects}
        self.assertIn("INVALID_PARAMETER_RANGE", codes)
        self.assertIn("INVALID_RESEARCH_PHASE", codes)
        self.assertIn("TEMPORAL_CONTRACT_VIOLATION", codes)

    def test_credential_free_end_to_end_runtime(self):
        rd = _FakeAIResearchDirector()
        with tempfile.TemporaryDirectory() as directory:
            runtime = build_runtime(rd=rd, nexus_path=f"{directory}/nexus.json")
            subject = SubjectMetadata(subject_id="AAPL", ticker="AAPL")
            intake = IntakeEngine(runtime.cache)
            evidence = intake.ingest(subject=subject, source=_Source())
            outcome = runtime.orchestrator.run(
                subject=subject,
                evidence=evidence,
                max_analyses=1,
            )

            self.assertTrue(outcome.closed)
            self.assertEqual(outcome.close_reason, "PROOF_COMPLETE")
            self.assertEqual(outcome.analyses_executed, 1)
            self.assertEqual(outcome.findings_promoted, 1)
            self.assertEqual(rd.seen_result.method_id, "analysis.relationship.correlation")
            self.assertGreater(rd.seen_result.outputs["correlation"], 0.9)
            self.assertEqual(len(runtime.nexus.findings_for_subject("AAPL")), 1)
            self.assertGreater(len(runtime.concepts.all()), 10)
            self.assertEqual(
                rd.begin_context["research_concept_policy"]["authority"],
                "NON_AUTHORITATIVE_IDEA_SEEDS",
            )
            self.assertTrue(
                rd.begin_context["research_concept_policy"]["rd_may_generate_additional_concepts"]
            )
            self.assertTrue(
                any(
                    item["concept_id"] == "human.support_resistance"
                    for item in rd.begin_context["research_concepts"]
                )
            )
            # Raw evidence remains in temporary cache, not Nexus.
            self.assertEqual(len(runtime.cache.active_keys()), 1)


if __name__ == "__main__":
    unittest.main()
