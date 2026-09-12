from __future__ import annotations

import math
import statistics
from typing import Any, Mapping

from .analysis import RegisteredAnalysisMethod
from .method_catalog import MethodSpec, ParameterContract


METHOD_ID = "analysis.dataset.group_aggregate"


def _numeric(value: Any) -> float | None:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        number = float(value)
        return number if math.isfinite(number) else None
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            number = float(text.replace(",", ""))
        except ValueError:
            return None
        return number if math.isfinite(number) else None
    return None


def group_aggregate(
    evidence_payloads: Mapping[str, object],
    parameters: Mapping[str, Any],
) -> Mapping[str, Any]:
    """Group one supplied row dataset by exact RD-selected keys and aggregate RD-selected columns."""
    if len(evidence_payloads) != 1:
        raise ValueError("analysis.dataset.group_aggregate requires exactly one supplied dataset")

    payload = next(iter(evidence_payloads.values()))
    rows = tuple(payload)  # type: ignore[arg-type]
    if not all(isinstance(row, Mapping) for row in rows):
        raise ValueError("group_aggregate input must be an iterable of row mappings")

    group_by = parameters.get("group_by")
    aggregations = parameters.get("aggregations")
    if not isinstance(group_by, (list, tuple)) or not group_by:
        raise ValueError("group_by must contain at least one RD-selected column")
    group_columns = tuple(str(column).strip() for column in group_by)
    if any(not column for column in group_columns):
        raise ValueError("group_by columns must be nonblank")
    if len(set(group_columns)) != len(group_columns):
        raise ValueError("group_by columns must be unique")

    if not isinstance(aggregations, (list, tuple)) or not aggregations:
        raise ValueError("aggregations must contain at least one RD-authored aggregation")

    normalized: list[tuple[str, str, str]] = []
    output_names = set(group_columns)
    allowed = {"sum", "mean", "median", "minimum", "maximum"}
    for spec in aggregations:
        if not isinstance(spec, Mapping):
            raise ValueError("each aggregation entry must be a mapping")
        column = str(spec.get("column", "")).strip()
        statistic = str(spec.get("statistic", "")).strip().lower()
        output_name = str(spec.get("output_name", "")).strip()
        if not column or not output_name:
            raise ValueError("each aggregation requires nonblank column and output_name")
        if statistic not in allowed:
            raise ValueError(
                "unsupported aggregation statistic: " + repr(statistic)
                + "; allowed: maximum, mean, median, minimum, sum"
            )
        if output_name in output_names:
            raise ValueError(f"aggregation output_name is duplicated or reserved: {output_name!r}")
        output_names.add(output_name)
        normalized.append((column, statistic, output_name))

    grouped: dict[tuple[object, ...], list[Mapping[str, Any]]] = {}
    group_order: list[tuple[object, ...]] = []
    distinct_group_values: dict[str, list[object]] = {column: [] for column in group_columns}
    for row in rows:
        missing = [column for column in group_columns if column not in row]
        if missing:
            raise ValueError(f"group_by column is missing from input row: {missing[0]!r}")
        key = tuple(row[column] for column in group_columns)
        if key not in grouped:
            grouped[key] = []
            group_order.append(key)
        grouped[key].append(row)
        for column, value in zip(group_columns, key):
            if value not in distinct_group_values[column]:
                distinct_group_values[column].append(value)

    output_rows: list[Mapping[str, Any]] = []
    excluded_non_numeric: dict[str, int] = {output_name: 0 for _, _, output_name in normalized}
    for key in group_order:
        source_rows = grouped[key]
        result_row: dict[str, Any] = {
            column: value for column, value in zip(group_columns, key)
        }
        for column, statistic, output_name in normalized:
            values: list[float] = []
            for row in source_rows:
                if column not in row:
                    raise ValueError(f"aggregation column {column!r} is missing from input row")
                number = _numeric(row[column])
                if number is None:
                    excluded_non_numeric[output_name] += 1
                else:
                    values.append(number)

            if not values:
                value = None
            elif statistic == "sum":
                value = sum(values)
            elif statistic == "mean":
                value = statistics.fmean(values)
            elif statistic == "median":
                value = statistics.median(values)
            elif statistic == "minimum":
                value = min(values)
            else:
                value = max(values)
            result_row[output_name] = value
        output_rows.append(result_row)

    schema = list(output_rows[0].keys()) if output_rows else list(group_columns) + [
        output_name for _, _, output_name in normalized
    ]
    return {
        "group_by": list(group_columns),
        "group_key_values": distinct_group_values,
        "aggregations": [
            {"column": column, "statistic": statistic, "output_name": output_name}
            for column, statistic, output_name in normalized
        ],
        "input_row_count": len(rows),
        "group_count": len(output_rows),
        "excluded_non_numeric": excluded_non_numeric,
        "derived_dataset_catalog": {
            "grouped_dataset": {
                "row_count": len(output_rows),
                "schema": schema,
                "output_path": ["derived_datasets", "grouped_dataset"],
                "temporary": True,
            }
        },
        "derived_datasets": {"grouped_dataset": output_rows},
        "output_order": "PRESERVES_FIRST_OCCURRENCE_OF_RD_SELECTED_GROUP_KEYS",
        "interpretation_boundary": (
            "MECHANICAL_GROUPING_AND_AGGREGATION_ONLY_RD_SELECTS_KEYS_COLUMNS_STATISTICS_AND_MEANING"
        ),
    }


def group_aggregation_method_spec() -> MethodSpec:
    return MethodSpec(
        METHOD_ID,
        ("NORMALIZED_DATASET",),
        (
            "Mechanically group one supplied raw or derived row dataset by exact RD-selected column values "
            "and compute RD-selected numeric aggregations. Mechanically parseable finite numeric strings are "
            "accepted as numbers, exact categorical grouping identities are returned to RD, and a temporary "
            "reusable grouped dataset is produced. Analysis does not infer grouping keys, time buckets, columns, "
            "statistics, aliases, or scientific meaning."
        ),
        (
            ParameterContract(
                "group_by",
                True,
                (list, tuple),
                minimum_length=1,
                meaning="RD-selected exact grouping columns; values are not transformed or bucketed",
            ),
            ParameterContract(
                "aggregations",
                True,
                (list, tuple),
                minimum_length=1,
                meaning=(
                    "RD-authored entries {column, statistic, output_name}; statistic is one of "
                    "sum, mean, median, minimum, maximum"
                ),
            ),
        ),
        1,
        metadata={
            "scientific_selection": "none",
            "reusable_derived_dataset": True,
            "derived_dataset_name": "grouped_dataset",
            "aggregation_statistics": ["sum", "mean", "median", "minimum", "maximum"],
            "execution_semantics": (
                "Groups use exact tuples of the RD-selected group_by column values and preserve first-occurrence "
                "group order. Exact distinct values for every selected grouping column are transported in "
                "group_key_values so category identity is not lost. Numeric aggregations accept finite numeric "
                "values or mechanically parseable finite numeric strings, exclude other values, and return null "
                "when a group has no numeric values for the selected aggregation column. No calendar resampling "
                "or time-bucket inference occurs."
            ),
        },
    )


def group_aggregation_analysis_method() -> RegisteredAnalysisMethod:
    return RegisteredAnalysisMethod(METHOD_ID, group_aggregate)
