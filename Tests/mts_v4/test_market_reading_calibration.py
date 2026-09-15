from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from MTS_V4.market_reading_calibration import (
    ASSESSMENT_FORMAT,
    calibration_messages,
    load_calibration_transport,
    write_calibration_assessment,
)


def _write_transport(path: Path, *, outcomes: bool = False) -> dict[str, object]:
    document: dict[str, object] = {
        "format": "MTS_V4_NEUTRAL_UNIVERSE_AI_TRANSPORT_ARTIFACT_V2",
        "source_artifact": "/frozen/source.json",
        "source_artifact_sha256": "a" * 64,
        "analysis_result_id": "result:stage2a",
        "method_id": "universe_market_structure:v1",
        "outputs": {
            "policy": {
                "historical_outcomes_consumed": outcomes,
                "findings_created": False,
                "hypotheses_created": False,
            },
            "coverage": {"latest_security_count": 503},
        },
        "sol_calls": 0,
    }
    canonical = json.dumps(document, sort_keys=True, separators=(",", ":"))
    document["artifact_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    path.write_text(json.dumps(document), encoding="utf-8")
    return document


def test_transport_is_hash_checked_and_prompt_forbids_scientific_claims(tmp_path: Path) -> None:
    path = tmp_path / "transport.json"
    _write_transport(path)
    document = load_calibration_transport(path)
    messages = calibration_messages(document)
    prompt = messages[1]["content"]
    assert "Do not create or test a predictive or trading hypothesis" in prompt
    assert "Do not recommend a security, trade, allocation" in prompt
    assert '"historical_outcomes_consumed":false' in prompt


def test_transport_refuses_outcomes_and_tampering(tmp_path: Path) -> None:
    outcome_path = tmp_path / "outcomes.json"
    _write_transport(outcome_path, outcomes=True)
    with pytest.raises(RuntimeError, match="predictor-only"):
        load_calibration_transport(outcome_path)

    path = tmp_path / "tampered.json"
    document = _write_transport(path)
    document["sol_calls"] = 1
    path.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(RuntimeError, match="hash"):
        load_calibration_transport(path)


def test_assessment_is_immutable_and_records_non_scientific_boundary(tmp_path: Path) -> None:
    source = tmp_path / "transport.json"
    document = _write_transport(source)
    output = tmp_path / "assessment.json"
    result = write_calibration_assessment(
        output=output,
        source_path=source,
        source_document=document,
        model="sol-test",
        response="Bounded assessment.",
        authorized_spend_usd=2.0,
        estimated_spend_usd=0.25,
    )
    assert result["format"] == ASSESSMENT_FORMAT
    assert result["sol_calls"] == 1
    assert result["historical_outcomes_consumed"] is False
    assert result["verification_cohort_outcomes_accessed"] is False
    assert result["hypotheses_created"] is False
    assert result["findings_promoted"] is False
    with pytest.raises(RuntimeError, match="refusing to replace"):
        write_calibration_assessment(
            output=output,
            source_path=source,
            source_document=document,
            model="sol-test",
            response="replacement",
            authorized_spend_usd=2.0,
            estimated_spend_usd=0.25,
        )
