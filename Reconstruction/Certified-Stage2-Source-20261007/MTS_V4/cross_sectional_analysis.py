from __future__ import annotations

import math
from collections import defaultdict
from typing import Any, Mapping

from .analysis import RegisteredAnalysisMethod
from .method_catalog import MethodSpec, ParameterContract


METHOD_ID = "analysis.cross_sectional.rank"


def _numeric(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        number = float(value)
        return number if math.isfinite(number) else None
    if isinstance(value, str):
        try:
            number = float(value.strip().replace(",", ""))
        except (ValueError, AttributeError):
            return None
        return number if math.isfinite(number) else None
    return None


def cross_sectional_rank(
    evidence_payloads: Mapping[str, object],
    parameters: Mapping[str, Any],
) -> Mapping[str, Any]:
    """Rank an RD-selected numeric column within exact RD-selected cross-sections.

    This method creates no scientific rule. RD selects the value, grouping
    columns, direction, and output name. Ties receive average rank. Percentiles
    are in [0, 1], with 1.0 assigned to the highest rank when ascending=True.
    """

    if len(evidence_payloads) != 1:
        raise ValueError("analysis.cross_sectional.rank requires exactly one supplied dataset")
    payload = next(iter(evidence_payloads.values()))
    rows = tuple(payload)  # type: ignore[arg-type]
    if not all(isinstance(row, Mapping) for row in rows):
        raise ValueError("cross_sectional.rank input must be an iterable of row mappings")

    value_column = str(parameters.get("value_column", "")).strip()
    output_column = str(parameters.get("output_column", "")).strip()
    group_by_raw = parameters.get("group_by", ["effective_date"])
    ascending = parameters.get("ascending", True)
    if not value_column or not output_column:
        raise ValueError("value_column and output_column must be nonblank")
    if not isinstance(group_by_raw, (list, tuple)) or not group_by_raw:
        raise ValueError("group_by must contain at least one exact column")
    group_by = tuple(str(item).strip() for item in group_by_raw)
    if any(not item for item in group_by):
        raise ValueError("group_by columns must be nonblank")
    if not isinstance(ascending, bool):
        raise ValueError("ascending must be boolean")

    grouped: dict[tuple[object, ...], list[tuple[int, float]]] = defaultdict(list)
    output_rows: list[dict[str, Any]] = [dict(row) for row in rows]
    excluded = 0
    for index, row in enumerate(rows):
        missing = [column for column in (*group_by, value_column) if column not in row]
        if missing:
            raise ValueError(f"required column is missing from input row: {missing[0]!r}")
        number = _numeric(row[value_column])
        if number is None:
            excluded += 1
            output_rows[index][output_column] = None
            continue
        key = tuple(row[column] for column in group_by)
        grouped[key].append((index, number))

    group_sizes: dict[str, int] = {}
    for key, observations in grouped.items():
        observations.sort(key=lambda item: item[1], reverse=not ascending)
        n = len(observations)
        group_sizes[repr(key)] = n
        position = 0
        while position < n:
            tie_end = position + 1
            while tie_end < n and observations[tie_end][1] == observations[position][1]:
                tie_end += 1
            average_one_based_rank = ((position + 1) + tie_end) / 2.0
            percentile = 1.0 if n == 1 else (average_one_based_rank - 1.0) / (n - 1.0)
            for offset in range(position, tie_end):
                row_index = observations[offset][0]
                output_rows[row_index][output_column] = percentile
            position = tie_end

    schema = list(output_rows[0].keys()) if output_rows else [*group_by, value_column, output_column]
    return {
        "group_by": list(group_by),
        "value_column": value_column,
        "output_column": output_column,
        "ascending": ascending,
        "input_row_count": len(rows),
        "ranked_row_count": len(rows) - excluded,
        "excluded_non_numeric": excluded,
        "group_sizes": group_sizes,
        "derived_dataset_catalog": {
            "cross_sectional_ranked_dataset": {
                "row_count": len(output_rows),
                "schema": schema,
                "output_path": ["derived_datasets", "cross_sectional_ranked_dataset"],
                "temporary": True,
            }
        },
        "derived_datasets": {"cross_sectional_ranked_dataset": output_rows},
        "interpretation_boundary": (
            "MECHANICAL_WITHIN_GROUP_RANKING_ONLY_RD_SELECTS_VALUE_GROUPS_DIRECTION_AND_MEANING"
        ),
    }


def method_spec() -> MethodSpec:
    return MethodSpec(
        METHOD_ID,
        ("TABULAR", "NORMALIZED_DATASET"),
        (
            "Mechanically compute within-cross-section percentile ranks for an exact RD-selected numeric column. "
            "RD selects grouping columns, direction, and output name. No signal threshold, cohort, hypothesis, "
            "or scientific interpretation is selected by deterministic code."
        ),
        (
            ParameterContract("value_column", True, (str,)),
            ParameterContract("output_column", True, (str,)),
            ParameterContract("group_by", False, (list, tuple), minimum_length=1),
            ParameterContract("ascending", False, (bool,)),
        ),
        1,
        metadata={
            "scientific_selection": "none",
            "cross_sectional": True,
            "reusable_derived_dataset": True,
            "derived_dataset_name": "cross_sectional_ranked_dataset",
        },
    )


def analysis_method() -> RegisteredAnalysisMethod:
    return RegisteredAnalysisMethod(METHOD_ID, cross_sectional_rank)
