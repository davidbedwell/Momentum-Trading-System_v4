from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Mapping

from .analysis import RegisteredAnalysisMethod
from .method_catalog import MethodSpec, ParameterContract


NULL_METHOD_ID = "analysis.controls.deterministic_null"


@dataclass(frozen=True, slots=True)
class BlindedScientificControl:
    control_id: str
    research_prompt: str
    required_evidence_families: tuple[str, ...]


# These prompts intentionally do not state the expected direction/result. Grading
# criteria belong in human-side acceptance documentation, not RD context.
BLINDED_CONTROLS = (
    BlindedScientificControl(
        "cross_sectional_medium_term_momentum",
        "Investigate whether a security's medium-term relative price history contains reproducible information about subsequent returns across the eligible universe. Choose and justify formulation, horizon, cohorts, and robustness tests.",
        ("TRAILING_RETURNS", "CROSS_SECTIONAL_RANKS", "HISTORICAL_OUTCOMES"),
    ),
    BlindedScientificControl(
        "medium_term_trend_persistence",
        "Investigate whether objectively measurable medium-term trend state contains reproducible information about subsequent market behavior. Choose the trend representation and subsequent horizon rather than assuming one.",
        ("TREND", "HISTORICAL_OUTCOMES"),
    ),
    BlindedScientificControl(
        "short_horizon_reversal",
        "Investigate whether recent short-horizon price movement contains reproducible information about subsequent short-horizon behavior, including whether continuation or reversal is better supported.",
        ("SHORT_RETURNS", "HISTORICAL_OUTCOMES"),
    ),
    BlindedScientificControl(
        "post_earnings_behavior",
        "Investigate whether point-in-time earnings-announcement information contains reproducible information about subsequent price behavior, with event timing and eligible controls handled explicitly.",
        ("POINT_IN_TIME_EARNINGS", "EVENT_RELATIVE_PRICE", "HISTORICAL_OUTCOMES"),
    ),
    BlindedScientificControl(
        "deterministic_negative_control",
        "Investigate whether the supplied neutral control measurement contains stable predictive information about subsequent market behavior. Apply the same skepticism and robustness standards used for other candidate predictors.",
        ("DETERMINISTIC_NULL", "HISTORICAL_OUTCOMES"),
    ),
)


def deterministic_null(evidence_payloads: Mapping[str, object], parameters: Mapping[str, Any]) -> Mapping[str, Any]:
    if len(evidence_payloads) != 1:
        raise ValueError(f"{NULL_METHOD_ID} requires exactly one row dataset")
    rows = tuple(next(iter(evidence_payloads.values())))  # type: ignore[arg-type]
    security_column = str(parameters.get("security_column", "security_id"))
    date_column = str(parameters.get("date_column", "effective_date"))
    output_column = str(parameters.get("output_column", "deterministic_null"))
    salt = str(parameters.get("salt", "MTS_V4_ACCEPTANCE_NULL_V1"))
    output = []
    for raw in rows:
        if not isinstance(raw, Mapping) or security_column not in raw or date_column not in raw:
            raise ValueError("null-control identity columns missing")
        token = f"{salt}|{raw[security_column]}|{raw[date_column]}".encode("utf-8")
        integer = int.from_bytes(hashlib.sha256(token).digest()[:8], "big")
        row = dict(raw)
        row[output_column] = integer / float(2**64 - 1)
        output.append(row)
    return {
        "output_column": output_column,
        "row_count": len(output),
        "derived_dataset_catalog": {
            "deterministic_null_dataset": {
                "row_count": len(output),
                "schema": list(output[0].keys()) if output else [],
                "output_path": ["derived_datasets", "deterministic_null_dataset"],
                "temporary": True,
            }
        },
        "derived_datasets": {"deterministic_null_dataset": output},
        "interpretation_boundary": "MECHANICAL_IDENTITY_HASH_NEGATIVE_CONTROL_NO_EXPECTED_RESULT_EXPOSED_TO_RD",
    }


def null_method_spec() -> MethodSpec:
    return MethodSpec(
        NULL_METHOD_ID,
        ("TABULAR", "NORMALIZED_DATASET"),
        "Create a deterministic identity-hash neutral measurement for scientific negative-control testing; no market variable is used to construct the value.",
        (
            ParameterContract("security_column", False, (str,)),
            ParameterContract("date_column", False, (str,)),
            ParameterContract("output_column", False, (str,)),
            ParameterContract("salt", False, (str,)),
        ),
        1,
        metadata={"scientific_selection": "none", "acceptance_control": True, "expected_result_exposed_to_rd": False},
    )


def null_analysis_method() -> RegisteredAnalysisMethod:
    return RegisteredAnalysisMethod(NULL_METHOD_ID, deterministic_null)
