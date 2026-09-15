from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


TRANSPORT_FORMAT = "MTS_V4_NEUTRAL_UNIVERSE_AI_TRANSPORT_ARTIFACT_V2"
ASSESSMENT_FORMAT = "MTS_V4_SOL_MARKET_READING_CALIBRATION_V1"


def _canonical_sha256(document: Mapping[str, Any]) -> str:
    payload = dict(document)
    payload.pop("artifact_sha256", None)
    canonical = json.dumps(payload, sort_keys=True, default=str, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def load_calibration_transport(path: Path) -> dict[str, Any]:
    document = json.loads(path.read_text(encoding="utf-8"))
    if document.get("format") != TRANSPORT_FORMAT:
        raise RuntimeError("market-reading calibration requires the Stage 2A V2 transport format")
    recorded_hash = document.get("artifact_sha256")
    if not isinstance(recorded_hash, str) or recorded_hash != _canonical_sha256(document):
        raise RuntimeError("Stage 2A transport artifact hash does not match its content")
    if document.get("sol_calls") != 0:
        raise RuntimeError("Stage 2A transport must record zero prior Sol calls")
    outputs = document.get("outputs")
    if not isinstance(outputs, dict):
        raise RuntimeError("Stage 2A transport is missing neutral outputs")
    policy = outputs.get("policy")
    if not isinstance(policy, dict) or policy.get("historical_outcomes_consumed") is not False:
        raise RuntimeError("market-reading calibration requires an explicit predictor-only policy")
    if policy.get("findings_created") is not False or policy.get("hypotheses_created") is not False:
        raise RuntimeError("market-reading calibration refuses pre-created findings or hypotheses")
    if "derived_datasets" in outputs or "historical_outcomes" in outputs:
        raise RuntimeError("market-reading calibration refuses raw/derived datasets and outcomes")
    return document


def calibration_messages(document: Mapping[str, Any]) -> list[Mapping[str, str]]:
    contract = {
        "operation": "MARKET_READING_CALIBRATION",
        "purpose": (
            "Assess whether Sol can accurately interpret the supplied neutral, predictor-only "
            "full-universe representation of the market at its recorded effective date."
        ),
        "strict_boundaries": [
            "Describe only what the supplied measurements support.",
            "Address market regime/structure, breadth, participation, trend, momentum, volatility, dispersion, cross-sectional organization, sector leadership, internal agreement or contradiction, and material uncertainty.",
            "Separate observations from interpretations and explicitly identify limitations.",
            "Do not use or infer historical outcomes, future returns, or reserved-cohort information.",
            "Do not create or test a predictive or trading hypothesis.",
            "Do not recommend a security, trade, allocation, entry, exit, or position size.",
            "Do not claim scientific validation, predictive accuracy, or a durable finding.",
            "Treat transport-rounded values as representational context, never as authoritative thresholds.",
        ],
        "requested_response_sections": [
            "observation_clock_and_coverage",
            "market_structure_reading",
            "breadth_and_participation",
            "trend_and_momentum",
            "volatility_and_dispersion",
            "sector_and_cross_sectional_structure",
            "agreement_contradictions_and_uncertainty",
            "capability_assessment",
        ],
        "stage2a_transport": document,
    }
    return [
        {
            "role": "system",
            "content": (
                "You are performing a bounded MTS v4 market-reading calibration, not scientific "
                "discovery or trading research. Follow every boundary in the user contract. Return "
                "a concise, evidence-linked assessment in plain text with the requested section headings."
            ),
        },
        {"role": "user", "content": json.dumps(contract, sort_keys=True, separators=(",", ":"))},
    ]


def write_calibration_assessment(
    *,
    output: Path,
    source_path: Path,
    source_document: Mapping[str, Any],
    model: str,
    response: str,
    authorized_spend_usd: float,
    estimated_spend_usd: float | None,
) -> dict[str, Any]:
    if output.exists():
        raise RuntimeError(f"refusing to replace frozen calibration assessment: {output}")
    payload: dict[str, Any] = {
        "format": ASSESSMENT_FORMAT,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "calibration_class": "DESCRIPTIVE_NON_SCIENTIFIC_MARKET_READING",
        "source_transport": str(source_path),
        "source_transport_sha256": source_document["artifact_sha256"],
        "model": model,
        "sol_calls": 1,
        "authorized_spend_usd": authorized_spend_usd,
        "estimated_spend_usd": estimated_spend_usd,
        "historical_outcomes_consumed": False,
        "verification_cohort_outcomes_accessed": False,
        "hypotheses_created": False,
        "findings_promoted": False,
        "trade_recommendations_authorized": False,
        "assessment": response.strip(),
    }
    payload["artifact_sha256"] = _canonical_sha256(payload)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(output)
    return payload
