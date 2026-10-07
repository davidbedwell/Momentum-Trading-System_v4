from __future__ import annotations

import math
import statistics
from collections import defaultdict
from typing import Any, Mapping, Sequence

from .analysis import RegisteredAnalysisMethod
from .method_catalog import MethodSpec, ParameterContract


METHOD_ID = "analysis.cross_sectional.association"


def _finite(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _average_ranks(values: Sequence[float]) -> list[float]:
    ordered = sorted(enumerate(values), key=lambda item: item[1])
    ranks = [0.0] * len(values)
    position = 0
    while position < len(ordered):
        tie_end = position + 1
        while tie_end < len(ordered) and ordered[tie_end][1] == ordered[position][1]:
            tie_end += 1
        average_rank = ((position + 1) + tie_end) / 2.0
        for offset in range(position, tie_end):
            ranks[ordered[offset][0]] = average_rank
        position = tie_end
    return ranks


def _pearson(left: Sequence[float], right: Sequence[float]) -> float | None:
    if len(left) < 3 or len(left) != len(right):
        return None
    mean_left = statistics.fmean(left)
    mean_right = statistics.fmean(right)
    numerator = sum(
        (left_value - mean_left) * (right_value - mean_right)
        for left_value, right_value in zip(left, right)
    )
    denominator = math.sqrt(
        sum((value - mean_left) ** 2 for value in left)
        * sum((value - mean_right) ** 2 for value in right)
    )
    return None if denominator == 0 else numerator / denominator


def _newey_west_mean(values: Sequence[float], max_lag: int) -> Mapping[str, float | int | None]:
    n = len(values)
    if n == 0:
        return {"n_dates": 0, "mean": None, "standard_error": None, "t_statistic": None}
    mean = statistics.fmean(values)
    if n == 1:
        return {"n_dates": 1, "mean": mean, "standard_error": None, "t_statistic": None, "max_lag": 0}
    centered = [value - mean for value in values]
    long_run_variance = sum(value * value for value in centered) / n
    lag_limit = min(max_lag, n - 1)
    for lag in range(1, lag_limit + 1):
        covariance = sum(
            centered[index] * centered[index - lag] for index in range(lag, n)
        ) / n
        long_run_variance += 2.0 * (1.0 - lag / (lag_limit + 1.0)) * covariance
    standard_error = math.sqrt(max(0.0, long_run_variance / n))
    return {
        "n_dates": n,
        "mean": mean,
        "standard_error": standard_error,
        "t_statistic": None if standard_error == 0 else mean / standard_error,
        "max_lag": lag_limit,
    }


def cross_sectional_association(
    evidence_payloads: Mapping[str, object], parameters: Mapping[str, Any]
) -> Mapping[str, Any]:
    """Measure an RD-selected within-date association and temporal stability.

    The Research Director selects the predictor, outcome, cross-section identity,
    association statistic, and temporal-dependence lag. Analysis calculates one
    association per cross-section and summarizes that dated series without
    pooling security-date rows as independent observations.
    """
    if len(evidence_payloads) != 1:
        raise ValueError(f"{METHOD_ID} requires exactly one row dataset")
    rows = tuple(next(iter(evidence_payloads.values())))  # type: ignore[arg-type]
    if not all(isinstance(row, Mapping) for row in rows):
        raise ValueError("cross_sectional.association input must be row mappings")

    predictor_column = str(parameters.get("predictor_column", "")).strip()
    outcome_column = str(parameters.get("outcome_column", "")).strip()
    date_column = str(parameters.get("date_column", "")).strip()
    association_type = str(parameters.get("association_type", "")).strip().lower()
    max_lag = int(parameters.get("newey_west_max_lag", 0))
    if not predictor_column or not outcome_column or not date_column:
        raise ValueError("predictor_column, outcome_column, and date_column are required")
    if association_type not in {"pearson", "spearman"}:
        raise ValueError("association_type must be pearson or spearman")
    if max_lag < 0 or max_lag > 252:
        raise ValueError("newey_west_max_lag must be in [0,252]")

    by_date: dict[str, list[tuple[float, float]]] = defaultdict(list)
    excluded = 0
    for row in rows:
        missing = [
            column
            for column in (predictor_column, outcome_column, date_column)
            if column not in row
        ]
        if missing:
            raise ValueError(f"required column is missing from input row: {missing[0]!r}")
        predictor = _finite(row[predictor_column])
        outcome = _finite(row[outcome_column])
        if predictor is None or outcome is None:
            excluded += 1
            continue
        by_date[str(row[date_column])].append((predictor, outcome))

    dated_associations: list[Mapping[str, object]] = []
    usable: list[float] = []
    for effective_date in sorted(by_date):
        pairs = by_date[effective_date]
        left = [pair[0] for pair in pairs]
        right = [pair[1] for pair in pairs]
        if association_type == "spearman":
            left = _average_ranks(left)
            right = _average_ranks(right)
        association = _pearson(left, right)
        dated_associations.append(
            {"effective_date": effective_date, "n": len(pairs), "association": association}
        )
        if association is not None:
            usable.append(association)

    yearly: dict[str, list[float]] = defaultdict(list)
    for item in dated_associations:
        value = item["association"]
        if isinstance(value, float):
            yearly[str(item["effective_date"])[:4]].append(value)

    return {
        "predictor_column": predictor_column,
        "outcome_column": outcome_column,
        "date_column": date_column,
        "association_type": association_type,
        "input_rows": len(rows),
        "excluded_rows": excluded,
        "cross_sections_total": len(dated_associations),
        "cross_sections_with_defined_association": len(usable),
        "equal_date_association": _newey_west_mean(usable, max_lag),
        "sign_fraction": None if not usable else sum(value > 0 for value in usable) / len(usable),
        "year_stability": {
            year: {
                "n_dates": len(values),
                "mean_association": statistics.fmean(values),
                "positive_fraction": sum(value > 0 for value in values) / len(values),
            }
            for year, values in sorted(yearly.items())
        },
        "derived_dataset_catalog": {
            "dated_cross_sectional_associations": {
                "row_count": len(dated_associations),
                "schema": ["effective_date", "n", "association"],
                "output_path": ["derived_datasets", "dated_cross_sectional_associations"],
                "temporary": True,
            }
        },
        "derived_datasets": {
            "dated_cross_sectional_associations": dated_associations,
        },
        "dependence_boundary": (
            "PRIMARY_ESTIMATE_IS_THE_EQUAL_DATE_SERIES_WITH_NEWEY_WEST_TEMPORAL_UNCERTAINTY; "
            "SECURITY_DATE_ROWS_ARE_NOT_TREATED_AS_INDEPENDENT_TRIALS"
        ),
        "interpretation_boundary": (
            "RD_SELECTS_PREDICTOR_OUTCOME_DATE_STATISTIC_AND_HAC_LAG; ANALYSIS_ONLY_EXECUTES"
        ),
    }


def method_spec() -> MethodSpec:
    return MethodSpec(
        METHOD_ID,
        ("TABULAR", "NORMALIZED_DATASET"),
        (
            "Measure an exact RD-selected predictor/outcome association separately within each "
            "RD-selected cross-section, then report equal-date mean association, Newey-West temporal "
            "uncertainty, sign consistency, and yearly stability. Security-date rows are not pooled as iid."
        ),
        (
            ParameterContract("predictor_column", True, (str,)),
            ParameterContract("outcome_column", True, (str,)),
            ParameterContract("date_column", True, (str,)),
            ParameterContract(
                "association_type", True, (str,), allowed_values=("pearson", "spearman")
            ),
            ParameterContract(
                "newey_west_max_lag", True, (int,), minimum_value=0, maximum_value=252
            ),
        ),
        1,
        metadata={
            "scientific_selection": "AI_RESEARCH_DIRECTOR_ONLY",
            "cross_sectional": True,
            "dependence_aware": True,
            "row_pooling_as_iid": False,
            "multiple_testing_correction": False,
            "reusable_derived_dataset": True,
            "derived_dataset_name": "dated_cross_sectional_associations",
        },
    )


def analysis_method() -> RegisteredAnalysisMethod:
    return RegisteredAnalysisMethod(METHOD_ID, cross_sectional_association)
