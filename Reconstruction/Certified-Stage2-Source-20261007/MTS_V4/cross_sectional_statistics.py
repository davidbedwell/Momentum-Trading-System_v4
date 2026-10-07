from __future__ import annotations

import math
import statistics
from collections import defaultdict
from typing import Any, Mapping

from .analysis import RegisteredAnalysisMethod
from .method_catalog import MethodSpec, ParameterContract


METHOD_ID = "analysis.cross_sectional.cohort_effect"


def _finite(value: object) -> float | None:
    if isinstance(value, bool):
        return float(value)
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _newey_west_mean(values: list[float], max_lag: int) -> Mapping[str, float | int | None]:
    n = len(values)
    if n == 0:
        return {"n_dates": 0, "mean": None, "standard_error": None, "t_statistic": None}
    mean = statistics.fmean(values)
    if n == 1:
        return {"n_dates": 1, "mean": mean, "standard_error": None, "t_statistic": None}
    centered = [value - mean for value in values]
    gamma0 = sum(value * value for value in centered) / n
    long_run = gamma0
    lag_limit = min(max_lag, n - 1)
    for lag in range(1, lag_limit + 1):
        covariance = sum(centered[t] * centered[t - lag] for t in range(lag, n)) / n
        weight = 1.0 - lag / (lag_limit + 1.0)
        long_run += 2.0 * weight * covariance
    variance_mean = max(0.0, long_run / n)
    se = math.sqrt(variance_mean)
    return {
        "n_dates": n,
        "mean": mean,
        "standard_error": se,
        "t_statistic": None if se == 0 else mean / se,
        "max_lag": lag_limit,
    }


def cohort_effect(evidence_payloads: Mapping[str, object], parameters: Mapping[str, Any]) -> Mapping[str, Any]:
    """Compare an RD-defined cohort with its complement without treating rows as iid.

    RD supplies the cohort column/threshold/direction, outcome, date identity and
    HAC lag. Deterministic Analysis reports row-level descriptives plus equal-date
    paired differences and Newey-West uncertainty across dates. It does not choose
    a signal, threshold, horizon, lag, or interpretation.
    """
    if len(evidence_payloads) != 1:
        raise ValueError(f"{METHOD_ID} requires exactly one row dataset")
    rows = tuple(next(iter(evidence_payloads.values())))  # type: ignore[arg-type]
    if not all(isinstance(row, Mapping) for row in rows):
        raise ValueError("cohort_effect input must be row mappings")
    cohort_column = str(parameters.get("cohort_column", "")).strip()
    outcome_column = str(parameters.get("outcome_column", "")).strip()
    date_column = str(parameters.get("date_column", "effective_date")).strip()
    threshold = _finite(parameters.get("threshold"))
    direction = str(parameters.get("direction", "GE")).upper()
    max_lag = int(parameters.get("newey_west_max_lag", 0))
    if not cohort_column or not outcome_column or not date_column or threshold is None:
        raise ValueError("cohort_column, outcome_column, date_column and numeric threshold are required")
    if direction not in {"GE", "GT", "LE", "LT"}:
        raise ValueError("direction must be GE, GT, LE, or LT")
    if max_lag < 0 or max_lag > 252:
        raise ValueError("newey_west_max_lag must be in [0,252]")

    def selected(value: float) -> bool:
        return {"GE": value >= threshold, "GT": value > threshold, "LE": value <= threshold, "LT": value < threshold}[direction]

    by_date: dict[str, dict[bool, list[float]]] = defaultdict(lambda: {True: [], False: []})
    selected_values: list[float] = []
    control_values: list[float] = []
    excluded = 0
    for row in rows:
        if cohort_column not in row or outcome_column not in row or date_column not in row:
            raise ValueError("required cohort/outcome/date column missing")
        cohort_value = _finite(row[cohort_column])
        outcome = _finite(row[outcome_column])
        if cohort_value is None or outcome is None:
            excluded += 1
            continue
        is_selected = selected(cohort_value)
        (selected_values if is_selected else control_values).append(outcome)
        by_date[str(row[date_column])][is_selected].append(outcome)

    paired: list[tuple[str, float]] = []
    for effective_date in sorted(by_date):
        groups = by_date[effective_date]
        if groups[True] and groups[False]:
            paired.append((effective_date, statistics.fmean(groups[True]) - statistics.fmean(groups[False])))
    differences = [value for _, value in paired]

    yearly: dict[str, list[float]] = defaultdict(list)
    for effective_date, value in paired:
        yearly[effective_date[:4]].append(value)

    selected_mean = statistics.fmean(selected_values) if selected_values else None
    control_mean = statistics.fmean(control_values) if control_values else None
    return {
        "cohort_definition": {"column": cohort_column, "threshold": threshold, "direction": direction},
        "outcome_column": outcome_column,
        "input_rows": len(rows),
        "excluded_rows": excluded,
        "selected_n": len(selected_values),
        "control_n": len(control_values),
        "selected_mean": selected_mean,
        "control_mean": control_mean,
        "naive_row_mean_difference": None if selected_mean is None or control_mean is None else selected_mean - control_mean,
        "equal_date_paired_difference": _newey_west_mean(differences, max_lag),
        "year_stability": {
            year: {"n_dates": len(values), "mean_date_difference": statistics.fmean(values)}
            for year, values in sorted(yearly.items())
        },
        "dependence_boundary": (
            "ROW_COUNTS_ARE_DESCRIPTIVE_NOT_INDEPENDENT_TRIAL_COUNTS; PRIMARY_UNCERTAINTY_IS_HAC_OVER_EQUAL_DATE_PAIRED_DIFFERENCES"
        ),
        "interpretation_boundary": "RD_SELECTED_COHORT_OUTCOME_THRESHOLD_DIRECTION_AND_HAC_LAG; ANALYSIS_ONLY_EXECUTES",
    }


def method_spec() -> MethodSpec:
    return MethodSpec(
        METHOD_ID,
        ("TABULAR", "NORMALIZED_DATASET"),
        "Compare an exact RD-defined cohort with its complement and report equal-date paired effects with Newey-West temporal uncertainty, avoiding an iid-row assumption.",
        (
            ParameterContract("cohort_column", True, (str,)),
            ParameterContract("outcome_column", True, (str,)),
            ParameterContract("threshold", True, (int, float)),
            ParameterContract("direction", True, (str,)),
            ParameterContract("date_column", False, (str,)),
            ParameterContract("newey_west_max_lag", False, (int,), minimum_value=0, maximum_value=252),
        ),
        1,
        metadata={
            "scientific_selection": "AI_RESEARCH_DIRECTOR_ONLY",
            "cross_sectional": True,
            "dependence_aware": True,
            "multiple_testing_correction": False,
        },
    )


def analysis_method() -> RegisteredAnalysisMethod:
    return RegisteredAnalysisMethod(METHOD_ID, cohort_effect)
