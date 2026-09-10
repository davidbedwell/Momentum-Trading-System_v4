from __future__ import annotations

import math
import statistics
from collections import defaultdict
from datetime import datetime
from typing import Any, Mapping

from .analysis import RegisteredAnalysisMethod
from .method_catalog import MethodSpec, ParameterContract


METHOD_ID = "analysis.relationship.temporal_correlation"


def _numeric(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _parse_time(value: object) -> datetime:
    if isinstance(value, (int, float)):
        number = float(value)
        if number > 1e12:
            number /= 1000.0
        return datetime.utcfromtimestamp(number)
    text = str(value).strip().replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return datetime.strptime(text[:10], "%Y-%m-%d")


def _bucket(value: object, period: str) -> str:
    dt = _parse_time(value)
    if period == "day":
        return dt.date().isoformat()
    monday = dt.date().toordinal() - dt.weekday()
    return datetime.fromordinal(monday).date().isoformat()


def _aggregate(values: list[float], mode: str) -> float | None:
    if mode == "count":
        return float(len(values))
    if not values:
        return None
    if mode == "sum":
        return sum(values)
    if mode == "mean":
        return statistics.fmean(values)
    if mode == "minimum":
        return min(values)
    if mode == "maximum":
        return max(values)
    if mode == "last":
        return values[-1]
    raise ValueError(f"unsupported aggregation: {mode}")


def _pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 2:
        return None
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    dx = [x - mx for x in xs]
    dy = [y - my for y in ys]
    denominator = math.sqrt(sum(x*x for x in dx) * sum(y*y for y in dy))
    return None if denominator == 0 else sum(x*y for x, y in zip(dx, dy)) / denominator


def _ranks(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        rank = (i + j + 2) / 2.0
        for k in range(i, j + 1):
            ranks[order[k]] = rank
        i = j + 1
    return ranks


def _series(rows, *, time_column: str, value_column: str, period: str, aggregation: str):
    grouped: dict[str, list[float]] = defaultdict(list)
    excluded = 0
    for row in rows:
        if not isinstance(row, Mapping) or time_column not in row:
            excluded += 1
            continue
        try:
            key = _bucket(row[time_column], period)
        except Exception:
            excluded += 1
            continue
        if aggregation == "count":
            grouped[key].append(1.0)
            continue
        value = _numeric(row.get(value_column))
        if value is None:
            excluded += 1
            continue
        grouped[key].append(value)
    return {key: _aggregate(values, aggregation) for key, values in grouped.items()}, excluded


def temporal_correlation(evidence_payloads: Mapping[str, object], parameters: Mapping[str, Any]) -> Mapping[str, Any]:
    left_id = str(parameters["left_evidence_id"])
    right_id = str(parameters["right_evidence_id"])
    try:
        left_rows = tuple(evidence_payloads[left_id])
        right_rows = tuple(evidence_payloads[right_id])
    except KeyError as exc:
        raise ValueError(f"requested evidence id not supplied: {exc.args[0]}") from exc

    period = str(parameters["period"])
    left, left_excluded = _series(
        left_rows,
        time_column=str(parameters["left_time_column"]),
        value_column=str(parameters["left_value_column"]),
        period=period,
        aggregation=str(parameters["left_aggregation"]),
    )
    right, right_excluded = _series(
        right_rows,
        time_column=str(parameters["right_time_column"]),
        value_column=str(parameters["right_value_column"]),
        period=period,
        aggregation=str(parameters["right_aggregation"]),
    )
    keys = sorted(set(left) & set(right))
    paired = [(key, left[key], right[key]) for key in keys if left[key] is not None and right[key] is not None]
    xs = [float(item[1]) for item in paired]
    ys = [float(item[2]) for item in paired]
    correlation_type = str(parameters["correlation_type"])
    correlation = _pearson(_ranks(xs), _ranks(ys)) if correlation_type == "spearman" else _pearson(xs, ys)
    return {
        "left_evidence_id": left_id,
        "right_evidence_id": right_id,
        "period": period,
        "left_aggregation": str(parameters["left_aggregation"]),
        "right_aggregation": str(parameters["right_aggregation"]),
        "paired_period_count": len(paired),
        "excluded_left_rows": left_excluded,
        "excluded_right_rows": right_excluded,
        "correlation_type": correlation_type,
        "correlation": correlation,
        "paired_observations": [{"period": key, "left": x, "right": y} for key, x, y in paired],
        "interpretation_boundary": "TEMPORAL_ALIGNMENT_AND_ASSOCIATION_ONLY_NOT_CAUSATION",
    }


def cross_evidence_method_spec() -> MethodSpec:
    aggregations = ("sum", "mean", "count", "minimum", "maximum", "last")
    return MethodSpec(
        method_id=METHOD_ID,
        artifact_types=("NORMALIZED_DATASET",),
        description=("Temporally align two RD-selected series, from the same or different supplied evidence datasets, aggregate each with RD-selected fields/rules, and measure Pearson or Spearman association. No causal or directional interpretation is supplied."),
        parameters=(
            ParameterContract("left_evidence_id", True, (str,), meaning="RD-selected first evidence id; must also appear in request evidence_ids; may equal right_evidence_id when both series come from the same dataset"),
            ParameterContract("right_evidence_id", True, (str,), meaning="RD-selected second evidence id; must also appear in request evidence_ids; may equal left_evidence_id when both series come from the same dataset"),
            ParameterContract("left_time_column", True, (str,), meaning="RD-selected timestamp/date field in first evidence"),
            ParameterContract("right_time_column", True, (str,), meaning="RD-selected timestamp/date field in second evidence"),
            ParameterContract("left_value_column", True, (str,), meaning="RD-selected numeric field; ignored when left_aggregation=count"),
            ParameterContract("right_value_column", True, (str,), meaning="RD-selected numeric field; ignored when right_aggregation=count"),
            ParameterContract("period", True, (str,), allowed_values=("day", "week"), meaning="RD-selected temporal alignment grain"),
            ParameterContract("left_aggregation", True, (str,), allowed_values=aggregations, meaning="RD-selected mechanical aggregation"),
            ParameterContract("right_aggregation", True, (str,), allowed_values=aggregations, meaning="RD-selected mechanical aggregation"),
            ParameterContract("correlation_type", True, (str,), allowed_values=("pearson", "spearman"), meaning="RD-selected association statistic"),
        ),
        minimum_sample=2,
        exploration_allowed=True,
        validation_allowed=True,
        metadata={"scientific_selection": "none", "cross_evidence": True},
    )


def cross_evidence_analysis_method() -> RegisteredAnalysisMethod:
    return RegisteredAnalysisMethod(METHOD_ID, temporal_correlation)
