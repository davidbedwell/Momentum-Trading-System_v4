from __future__ import annotations

import math
from typing import Any, Mapping

from .analysis import RegisteredAnalysisMethod
from .method_catalog import MethodSpec, ParameterContract

METHOD_ID = "analysis.statistics.benjamini_hochberg"


def benjamini_hochberg(evidence_payloads: Mapping[str, object], parameters: Mapping[str, Any]) -> Mapping[str, Any]:
    if len(evidence_payloads) != 1:
        raise ValueError(f"{METHOD_ID} requires one supplied row dataset")
    rows = tuple(next(iter(evidence_payloads.values())))  # type: ignore[arg-type]
    p_column = str(parameters.get("p_value_column", "")).strip()
    output_column = str(parameters.get("output_column", "bh_q_value")).strip()
    if not p_column or not output_column:
        raise ValueError("p_value_column and output_column must be nonblank")
    indexed = []
    output = [dict(row) for row in rows]
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping) or p_column not in row:
            raise ValueError(f"missing p-value column {p_column!r}")
        try:
            p = float(row[p_column])
        except (TypeError, ValueError):
            output[index][output_column] = None
            continue
        if not math.isfinite(p) or p < 0 or p > 1:
            output[index][output_column] = None
            continue
        indexed.append((index, p))
    indexed.sort(key=lambda item: item[1])
    m = len(indexed)
    adjusted = [0.0] * m
    running = 1.0
    for reverse_position in range(m - 1, -1, -1):
        rank = reverse_position + 1
        candidate = indexed[reverse_position][1] * m / rank
        running = min(running, candidate)
        adjusted[reverse_position] = min(1.0, running)
    for position, (index, _) in enumerate(indexed):
        output[index][output_column] = adjusted[position]
    return {
        "tested_hypotheses": m,
        "excluded_invalid_p_values": len(rows) - m,
        "p_value_column": p_column,
        "output_column": output_column,
        "derived_dataset_catalog": {
            "bh_adjusted_dataset": {
                "row_count": len(output),
                "schema": list(output[0].keys()) if output else [],
                "output_path": ["derived_datasets", "bh_adjusted_dataset"],
                "temporary": True,
            }
        },
        "derived_datasets": {"bh_adjusted_dataset": output},
        "interpretation_boundary": "MECHANICAL_BH_ADJUSTMENT_ONLY_RD_DEFINES_TEST_FAMILY_AND_INTERPRETS",
    }


def method_spec() -> MethodSpec:
    return MethodSpec(
        METHOD_ID,
        ("TABULAR", "NORMALIZED_DATASET"),
        "Apply Benjamini-Hochberg adjustment to an exact RD-selected p-value column. RD remains responsible for defining the scientifically coherent family of tests.",
        (
            ParameterContract("p_value_column", True, (str,)),
            ParameterContract("output_column", False, (str,)),
        ),
        1,
        metadata={"scientific_selection": "AI_RESEARCH_DIRECTOR_ONLY", "multiple_testing_adjustment": "BENJAMINI_HOCHBERG"},
    )


def analysis_method() -> RegisteredAnalysisMethod:
    return RegisteredAnalysisMethod(METHOD_ID, benjamini_hochberg)
