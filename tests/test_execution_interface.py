from __future__ import annotations

import json

from MTS_V4.contracts import AnalysisRequest, EvidenceDescriptor, ResearchPhase
from MTS_V4.execution_interface import (
    TransparentExecutionResearchDirector,
    TransparentInputBindingValidator,
)
from MTS_V4.standard_methods import standard_method_catalog


def _evidence(evidence_id: str) -> EvidenceDescriptor:
    return EvidenceDescriptor(
        evidence_id=evidence_id,
        subject_id="equity:AAPL",
        evidence_type="OHLCV",
        artifact_type="NORMALIZED_DATASET",
        source_identity="test",
        coverage_start="2026-01-01",
        coverage_end="2026-01-02",
        row_count=2,
        schema=("date", "close", "volume"),
        cache_key=f"cache:{evidence_id}",
    )


def _compose_request(*, left_name: str, right_name: str) -> AnalysisRequest:
    left_id = "evidence:equity:AAPL:left"
    right_id = "evidence:equity:AAPL:right"
    return AnalysisRequest(
        request_id="req:test",
        subject_id="equity:AAPL",
        question="AI-authored question",
        method_id="analysis.dataset.compose",
        evidence_ids=(left_id, right_id),
        analysis_inputs=(),
        parameters={
            "alignment": [
                {"input_name": left_name, "key": {"mode": "COLUMN", "column": "date"}},
                {"input_name": right_name, "key": {"mode": "COLUMN", "column": "date"}},
            ],
            "selections": [
                {"input_name": left_name, "column": "close", "output_name": "close"},
                {"input_name": right_name, "column": "volume", "output_name": "volume"},
            ],
            "join_type": "INNER",
        },
        research_phase=ResearchPhase.EXPLORATION,
        rationale="AI-authored rationale",
    )


def test_compose_friendly_aliases_are_rejected_before_execution():
    left_id = "evidence:equity:AAPL:left"
    right_id = "evidence:equity:AAPL:right"
    validator = TransparentInputBindingValidator(standard_method_catalog())
    request = _compose_request(left_name="ohlcv", right_name="options_flow")

    defects = validator.validate(
        request,
        {
            left_id: _evidence(left_id),
            right_id: _evidence(right_id),
        },
        {},
    )

    binding_defects = [item for item in defects if item.code == "INVALID_INPUT_BINDING"]
    assert len(binding_defects) >= 2
    message = " ".join(item.message for item in binding_defects)
    assert "ohlcv" in message
    assert "options_flow" in message
    assert left_id in message
    assert right_id in message
    assert "exact evidence_id" in message


def test_compose_exact_acquired_evidence_bindings_are_accepted():
    left_id = "evidence:equity:AAPL:left"
    right_id = "evidence:equity:AAPL:right"
    validator = TransparentInputBindingValidator(standard_method_catalog())
    request = _compose_request(left_name=left_id, right_name=right_id)

    defects = validator.validate(
        request,
        {
            left_id: _evidence(left_id),
            right_id: _evidence(right_id),
        },
        {},
    )

    assert not [item for item in defects if item.code == "INVALID_INPUT_BINDING"]


def test_rd_receives_literal_input_namespace_and_compose_duplicate_key_rules():
    messages = TransparentExecutionResearchDirector._decision_messages(
        operation="BEGIN_RESEARCH",
        mission="test",
        payload={"subject": {"subject_id": "equity:AAPL"}},
    )

    system_text = messages[0]["content"]
    user = json.loads(messages[1]["content"])
    instruction_text = " ".join(user["instructions"])

    assert "exact evidence_id string" in system_text
    assert "no other implicit or friendly aliases exist" in system_text
    assert "Literal Analysis input namespace" in instruction_text
    assert "full evidence_id as input_name" in instruction_text
    assert "COLUMN alignment requires a unique key value" in instruction_text
    assert "performs no aggregation of duplicate keys" in instruction_text
    assert "deterministic code will not choose one for you" in instruction_text
