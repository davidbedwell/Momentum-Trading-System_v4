from __future__ import annotations

from dataclasses import replace
import math
import statistics
import warnings
from typing import Any, Mapping, Sequence

from scipy import stats

from .analysis import RegisteredAnalysisMethod
from .contracts import AnalysisRequest, AnalysisResult, EvidenceDescriptor, ResearchPhase, SubjectMetadata
from .discovery_methods import deterministic_family_measurements
from .method_catalog import MethodSpec, ParameterContract
from .standard_methods import forward_path_measurement


METHOD_ID = "analysis.substrate.standard_ohlcv"
LOGICAL_ANALYSIS_ID = "analysis:neutral-standard-ohlcv-substrate:v1"
STANDARD_FAMILIES = (
    "PRICE_CANDLE",
    "TREND",
    "MOMENTUM",
    "VOLATILITY",
    "VOLUME_LIQUIDITY",
    "MARKET_STRUCTURE",
)
STANDARD_HORIZONS = (1, 3, 5, 10, 20)
STANDARD_PREDICTORS = (
    "bollinger_width_20",
    "gap_over_atr14",
    "gap_pct",
    "gap_x_intraday_response",
    "moving_average_compression",
    "normalized_slope",
    "range_position_20_centered",
    "relative_volume_mean_20",
    "return_intraday",
    "roc5_atr20_x_range_position20",
    "roc5_over_atr20",
)


def _finite(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        number = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _summary(values: Sequence[float]) -> Mapping[str, object]:
    return {
        "n": len(values),
        "mean": statistics.fmean(values) if values else None,
        "median": statistics.median(values) if values else None,
        "minimum": min(values) if values else None,
        "maximum": max(values) if values else None,
    }


def _association(rows: Sequence[Mapping[str, object]], x: str, y: str) -> Mapping[str, object]:
    pairs = [
        (left, right)
        for row in rows
        if (left := _finite(row.get(x))) is not None
        and (right := _finite(row.get(y))) is not None
    ]
    if len(pairs) < 3:
        return {"n": len(pairs), "spearman": None, "spearman_p": None, "pearson": None, "pearson_p": None}
    xs, ys = zip(*pairs)
    if len(set(xs)) < 2 or len(set(ys)) < 2:
        return {"n": len(pairs), "spearman": None, "spearman_p": None, "pearson": None, "pearson_p": None}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        spearman = stats.spearmanr(xs, ys)
        pearson = stats.pearsonr(xs, ys)
    return {
        "n": len(pairs),
        "spearman": _finite(spearman.statistic),
        "spearman_p": _finite(spearman.pvalue),
        "pearson": _finite(pearson.statistic),
        "pearson_p": _finite(pearson.pvalue),
    }


def standard_ohlcv_substrate(
    evidence_payloads: Mapping[str, object],
    parameters: Mapping[str, Any],
) -> Mapping[str, Any]:
    """Compute an exhaustive, unranked standard OHLCV measurement substrate.

    The human-approved substrate calculates every governed measurement column
    against every standard forward-path outcome. It does not select candidates,
    rank results, form hypotheses, or call any relationship a finding.
    """
    families = tuple(str(item) for item in parameters["families"])
    horizons = tuple(int(item) for item in parameters["horizons"])
    if families != STANDARD_FAMILIES or horizons != STANDARD_HORIZONS:
        raise ValueError("standard OHLCV substrate requires the versioned exhaustive policy grid")

    measured = deterministic_family_measurements(evidence_payloads, {"families": list(families)})
    measurement_rows = list(measured["derived_datasets"]["deterministic_measurements"])
    measurement_columns = tuple(str(item) for item in measured["measurement_columns"])
    panel = [dict(row) for row in measurement_rows]
    for row in panel:
        gap = _finite(row.get("gap_pct"))
        intraday = _finite(row.get("return_intraday"))
        atr14 = _finite(row.get("atr_pct_14"))
        atr20 = _finite(row.get("atr_pct_20"))
        roc5 = _finite(row.get("roc_5"))
        position = _finite(row.get("range_position_20"))
        row["gap_over_atr14"] = None if gap is None or atr14 in (None, 0.0) else gap / atr14
        row["gap_x_intraday_response"] = None if gap is None or intraday is None else gap * intraday
        row["roc5_over_atr20"] = None if roc5 is None or atr20 in (None, 0.0) else roc5 / atr20
        row["range_position_20_centered"] = None if position is None else position - 0.5
        normalized_roc = _finite(row["roc5_over_atr20"])
        centered = _finite(row["range_position_20_centered"])
        row["roc5_atr20_x_range_position20"] = (
            None if normalized_roc is None or centered is None else normalized_roc * centered
        )
    outcome_columns: list[str] = []
    forward_summaries: dict[str, object] = {}

    for horizon in horizons:
        forward = forward_path_measurement(
            evidence_payloads,
            {"price_column": "close", "horizon": horizon, "direction": "LONG"},
        )
        forward_summaries[f"h{horizon}"] = {
            key: value
            for key, value in forward.items()
            if key not in {"derived_datasets", "derived_dataset_catalog"}
        }
        source_rows = forward["derived_datasets"]["forward_path_observations"]
        for source in source_rows:
            index = int(source["index"])
            if index >= len(panel):
                continue
            mapping = {
                f"h{horizon}_terminal_return": source["terminal_directional_return"],
                f"h{horizon}_max_favorable": source["max_favorable_directional_return"],
                f"h{horizon}_max_adverse": source["max_adverse_directional_return"],
                f"h{horizon}_bars_to_max_favorable": source["bars_to_max_favorable"],
                f"h{horizon}_bars_to_max_adverse": source["bars_to_max_adverse"],
                f"h{horizon}_excursion_balance": (
                    float(source["max_favorable_directional_return"])
                    + float(source["max_adverse_directional_return"])
                ),
                f"h{horizon}_adverse_minus_favorable_timing": (
                    float(source["bars_to_max_adverse"])
                    - float(source["bars_to_max_favorable"])
                ),
            }
            panel[index].update(mapping)
            for name in mapping:
                if name not in outcome_columns:
                    outcome_columns.append(name)

    split = len(panel) // 2
    relationships = []
    available_predictors = tuple(column for column in STANDARD_PREDICTORS if column in panel[0]) if panel else ()
    for predictor in available_predictors:
        for outcome in outcome_columns:
            relationships.append(
                {
                    "predictor": predictor,
                    "outcome": outcome,
                    "full": _association(panel, predictor, outcome),
                    "chronological_first_half": _association(panel[:split], predictor, outcome),
                    "chronological_second_half": _association(panel[split:], predictor, outcome),
                }
            )

    descriptive = {}
    for column in (*available_predictors, *outcome_columns):
        values = [number for row in panel if (number := _finite(row.get(column))) is not None]
        descriptive[column] = {**_summary(values), "missing": len(panel) - len(values)}

    calendar: dict[str, object] = {}
    for component, extractor in (
        ("month", lambda text: int(text[5:7])),
        ("weekday", lambda text: __import__("datetime").date.fromisoformat(text[:10]).weekday()),
    ):
        groups: dict[int, list[Mapping[str, object]]] = {}
        for row in panel:
            text = str(row.get("date", ""))
            try:
                key = extractor(text)
            except (ValueError, IndexError):
                continue
            groups.setdefault(key, []).append(row)
        calendar[component] = {
            str(key): {
                outcome: _summary(
                    [number for row in rows if (number := _finite(row.get(outcome))) is not None]
                )
                for outcome in outcome_columns
            }
            for key, rows in groups.items()
        }

    schema = list(panel[0]) if panel else []
    return {
        "substrate_version": 1,
        "policy": {
            "human_authorized_neutral_infrastructure": True,
            "exhaustive_governed_measurement_columns": True,
            "standard_horizons": list(horizons),
            "predictor_grid_basis": (
                "UNRANKED_RECURRING_PRELIMINARY_DIRECTIONS_FROM_THE_AUDITED_AAPL_SOL_PROGRAM; "
                "NONEXCLUSIVE_AND_DOES_NOT_LIMIT_NEW_AI_AUTHORED_RELATIONSHIPS"
            ),
            "deterministic_scientific_selection_or_ranking": False,
            "findings_created": False,
            "rd_may_use_challenge_reformulate_or_ignore_any_measurement": True,
        },
        "families": list(families),
        "measurement_columns": list(measurement_columns),
        "precomputed_predictor_columns": list(available_predictors),
        "outcome_columns": outcome_columns,
        "row_count": len(panel),
        "descriptive_measurements": descriptive,
        "forward_path_summaries": forward_summaries,
        "unranked_relationship_measurements": relationships,
        "calendar_outcome_summaries": calendar,
        "derived_dataset_catalog": {
            "standard_ohlcv_panel": {
                "row_count": len(panel),
                "schema": schema,
                "output_path": ["derived_datasets", "standard_ohlcv_panel"],
                "temporary": True,
            }
        },
        "derived_datasets": {"standard_ohlcv_panel": panel},
        "interpretation_boundary": "NEUTRAL_MEASUREMENT_SUBSTRATE_ONLY_AI_RD_INTERPRETS_AND_SELECTS_SCIENCE",
    }


def method_spec() -> MethodSpec:
    return MethodSpec(
        METHOD_ID,
        ("NORMALIZED_DATASET",),
        "Human-authorized neutral infrastructure: calculate the complete versioned standard OHLCV measurement/outcome grid before AI scientific selection.",
        (
            ParameterContract("families", True, (list, tuple), exact_length=len(STANDARD_FAMILIES)),
            ParameterContract("horizons", True, (list, tuple), exact_length=len(STANDARD_HORIZONS)),
        ),
        2,
        True,
        False,
        True,
        {
            "scientific_selection": "none",
            "human_authorized_infrastructure": True,
            "deterministic_ranking": False,
            "reusable_derived_dataset": True,
            "derived_dataset_name": "standard_ohlcv_panel",
        },
    )


def analysis_method() -> RegisteredAnalysisMethod:
    return RegisteredAnalysisMethod(METHOD_ID, standard_ohlcv_substrate)


def build_for_subject(
    *,
    subject: SubjectMetadata,
    evidence: Sequence[EvidenceDescriptor],
    cache,
    analysis,
) -> Mapping[str, AnalysisResult]:
    candidates = [
        item
        for item in evidence
        if item.evidence_type == "OHLCV"
        and {"date", "open", "high", "low", "close", "volume"}.issubset(item.schema)
    ]
    if len(candidates) != 1:
        return {}
    descriptor = candidates[0]
    request = AnalysisRequest(
        request_id=f"neutral-substrate:{subject.subject_id}:v1",
        subject_id=subject.subject_id,
        question="Versioned exhaustive neutral OHLCV measurement substrate authorized by the human operator.",
        method_id=METHOD_ID,
        evidence_ids=(descriptor.evidence_id,),
        parameters={"families": list(STANDARD_FAMILIES), "horizons": list(STANDARD_HORIZONS)},
        research_phase=ResearchPhase.EXPLORATION,
        rationale="Precompute recurring objective measurements before AI scientific interpretation; no ranking or finding creation.",
    )
    result = analysis.execute(request, {descriptor.evidence_id: cache.get(descriptor.cache_key)})
    if result.execution_metadata.get("execution_status") != "SUCCESS":
        raise RuntimeError(f"neutral Analysis substrate failed: {result.outputs.get('execution_error')}")
    result = replace(
        result,
        execution_metadata={
            **result.execution_metadata,
            "future_information": {
                "contains_future_information": True,
                "direct_method_allows_future_information": True,
                "inherited_from_result_ids": [],
                "policy": "EXPLORATION_LOOKAHEAD_SUBSTRATE_ONLY_RD_DECIDES_SCIENTIFIC_USE",
            },
        },
    )
    return {LOGICAL_ANALYSIS_ID: result}
