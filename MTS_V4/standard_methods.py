from __future__ import annotations

import math
import statistics
from typing import Any, Mapping

from .analysis import RegisteredAnalysisMethod
from .method_catalog import MethodCatalog, MethodSpec, ParameterContract


def _rows(evidence_payloads: Mapping[str, object]) -> tuple[Mapping[str, Any], ...]:
    if len(evidence_payloads) != 1:
        raise ValueError("standard single-dataset methods require exactly one evidence payload")
    payload = next(iter(evidence_payloads.values()))
    rows = tuple(payload)  # type: ignore[arg-type]
    if not all(isinstance(row, Mapping) for row in rows):
        raise ValueError("evidence payload must be an iterable of row mappings")
    return rows


def _finite_numeric(values):
    return [
        float(value)
        for value in values
        if isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    ]


def _quantile(sorted_values: list[float], q: float) -> float | None:
    if not sorted_values:
        return None
    if len(sorted_values) == 1:
        return sorted_values[0]
    pos = (len(sorted_values) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return sorted_values[lo]
    weight = pos - lo
    return sorted_values[lo] * (1 - weight) + sorted_values[hi] * weight


def descriptive_statistics(
    evidence_payloads: Mapping[str, object],
    parameters: Mapping[str, Any],
) -> Mapping[str, Any]:
    """Audited pre-B descriptive-statistics operation admitted into v4."""
    rows = _rows(evidence_payloads)
    columns = tuple(parameters["columns"])
    summaries: dict[str, Mapping[str, Any]] = {}
    for column in columns:
        raw = [row.get(column) for row in rows]
        values = sorted(_finite_numeric(raw))
        summaries[str(column)] = {
            "count": len(values),
            "missing_count": sum(value is None for value in raw),
            "mean": statistics.fmean(values) if values else None,
            "median": statistics.median(values) if values else None,
            "stddev_sample": statistics.stdev(values) if len(values) >= 2 else None,
            "minimum": min(values) if values else None,
            "maximum": max(values) if values else None,
            "q05": _quantile(values, 0.05),
            "q25": _quantile(values, 0.25),
            "q75": _quantile(values, 0.75),
            "q95": _quantile(values, 0.95),
        }
    return {
        "row_count": len(rows),
        "columns": summaries,
        "interpretation_boundary": "DESCRIPTIVE_ONLY",
    }


def _pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 2:
        return None
    mx = statistics.fmean(xs)
    my = statistics.fmean(ys)
    dx = [x - mx for x in xs]
    dy = [y - my for y in ys]
    denominator = math.sqrt(sum(x * x for x in dx) * sum(y * y for y in dy))
    if denominator == 0:
        return None
    return sum(x * y for x, y in zip(dx, dy)) / denominator


def _average_ranks(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda index: values[index])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        rank = (i + j + 2) / 2.0
        for index in range(i, j + 1):
            ranks[order[index]] = rank
        i = j + 1
    return ranks


def relationship_correlation(
    evidence_payloads: Mapping[str, object],
    parameters: Mapping[str, Any],
) -> Mapping[str, Any]:
    """Audited pre-B relationship operation admitted under exact v4 scope."""
    rows = _rows(evidence_payloads)
    left, right = tuple(parameters["columns"])
    correlation_type = str(parameters.get("correlation_type", "pearson")).lower()
    if correlation_type not in {"pearson", "spearman"}:
        raise ValueError("correlation_type must be pearson or spearman")

    xs: list[float] = []
    ys: list[float] = []
    for row in rows:
        x = row.get(left)
        y = row.get(right)
        if (
            isinstance(x, (int, float))
            and not isinstance(x, bool)
            and isinstance(y, (int, float))
            and not isinstance(y, bool)
            and math.isfinite(float(x))
            and math.isfinite(float(y))
        ):
            xs.append(float(x))
            ys.append(float(y))

    if correlation_type == "spearman":
        value = _pearson(_average_ranks(xs), _average_ranks(ys))
    else:
        value = _pearson(xs, ys)

    return {
        "left": left,
        "right": right,
        "n": len(xs),
        "correlation_type": correlation_type,
        "correlation": value,
        "interpretation_boundary": "RELATIONSHIP_NOT_CAUSATION",
    }


def forward_path_measurement(
    evidence_payloads: Mapping[str, object],
    parameters: Mapping[str, Any],
) -> Mapping[str, Any]:
    """Measure future path geometry exactly as parameterized by RD.

    This is an exploration-only look-ahead measurement primitive. It identifies
    no event, threshold, horizon, direction, or price field on its own. RD must
    provide all scientifically meaningful specifications explicitly.
    """
    rows = _rows(evidence_payloads)
    price_column = str(parameters["price_column"])
    horizon = int(parameters["horizon"])
    direction = str(parameters["direction"])
    factor = 1.0 if direction == "LONG" else -1.0

    observations: list[Mapping[str, Any]] = []
    excluded_non_numeric = 0
    excluded_zero_entry = 0
    for index in range(0, max(0, len(rows) - horizon)):
        entry_raw = rows[index].get(price_column)
        future_raw = [rows[index + offset].get(price_column) for offset in range(1, horizon + 1)]
        values = [entry_raw, *future_raw]
        if not all(
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and math.isfinite(float(value))
            for value in values
        ):
            excluded_non_numeric += 1
            continue
        entry = float(entry_raw)
        if entry == 0.0:
            excluded_zero_entry += 1
            continue
        future = [float(value) for value in future_raw]
        directional_returns = [factor * ((value - entry) / entry) for value in future]
        max_favorable = max(directional_returns)
        max_adverse = min(directional_returns)
        observations.append(
            {
                "start_index": index,
                "entry": entry,
                "terminal_directional_return": directional_returns[-1],
                "max_favorable_directional_return": max_favorable,
                "max_adverse_directional_return": max_adverse,
                "bars_to_max_favorable": directional_returns.index(max_favorable) + 1,
                "bars_to_max_adverse": directional_returns.index(max_adverse) + 1,
            }
        )

    return {
        "price_column": price_column,
        "horizon": horizon,
        "direction": direction,
        "eligible_start_count": max(0, len(rows) - horizon),
        "observation_count": len(observations),
        "excluded_non_numeric": excluded_non_numeric,
        "excluded_zero_entry": excluded_zero_entry,
        "observations": observations,
        "interpretation_boundary": "LOOKAHEAD_MEASUREMENT_ONLY_RD_INTERPRETS",
    }


def standard_method_catalog() -> MethodCatalog:
    """Build the initial positive-admission v4 method catalog."""
    return MethodCatalog(
        [
            MethodSpec(
                method_id="analysis.descriptive.statistics",
                artifact_types=("NORMALIZED_DATASET",),
                description="Compute descriptive summaries for columns explicitly selected by RD.",
                parameters=(
                    ParameterContract(
                        name="columns",
                        required=True,
                        python_types=(list, tuple),
                        minimum_length=1,
                        meaning="one or more RD-selected numeric columns",
                    ),
                ),
                minimum_sample=1,
            ),
            MethodSpec(
                method_id="analysis.relationship.correlation",
                artifact_types=("NORMALIZED_DATASET",),
                description="Measure pairwise Pearson or Spearman association without causal interpretation.",
                parameters=(
                    ParameterContract(
                        name="columns",
                        required=True,
                        python_types=(list, tuple),
                        exact_length=2,
                        meaning="exactly two RD-selected numeric columns",
                    ),
                    ParameterContract(
                        name="correlation_type",
                        required=False,
                        python_types=(str,),
                        allowed_values=("pearson", "spearman"),
                        meaning="correlation statistic selected by RD",
                    ),
                ),
                minimum_sample=2,
            ),
            MethodSpec(
                method_id="analysis.path.forward_measurement",
                artifact_types=("NORMALIZED_DATASET",),
                description=(
                    "Exploration-only look-ahead measurement of terminal return, maximum favorable "
                    "excursion, maximum adverse excursion, and timing over an RD-selected forward horizon."
                ),
                parameters=(
                    ParameterContract(
                        name="price_column",
                        required=True,
                        python_types=(str,),
                        meaning="price field explicitly selected by RD",
                    ),
                    ParameterContract(
                        name="horizon",
                        required=True,
                        python_types=(int,),
                        minimum_value=1,
                        meaning="number of forward rows explicitly selected by RD",
                    ),
                    ParameterContract(
                        name="direction",
                        required=True,
                        python_types=(str,),
                        allowed_values=("LONG", "SHORT"),
                        meaning="directional frame explicitly selected by RD",
                    ),
                ),
                minimum_sample=2,
                exploration_allowed=True,
                validation_allowed=False,
                allows_future_information=True,
                metadata={
                    "row_order": "uses evidence rows in supplied order",
                    "scientific_selection": "none; RD supplies price_column, horizon, and direction",
                },
            ),
        ]
    )


def standard_analysis_methods() -> tuple[RegisteredAnalysisMethod, ...]:
    return (
        RegisteredAnalysisMethod(
            method_id="analysis.descriptive.statistics",
            implementation=descriptive_statistics,
        ),
        RegisteredAnalysisMethod(
            method_id="analysis.relationship.correlation",
            implementation=relationship_correlation,
        ),
        RegisteredAnalysisMethod(
            method_id="analysis.path.forward_measurement",
            implementation=forward_path_measurement,
        ),
    )
