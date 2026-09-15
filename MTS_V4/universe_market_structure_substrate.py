from __future__ import annotations

from dataclasses import replace
from itertools import combinations
import math
import statistics
from typing import Any, Mapping, Sequence

from .analysis import RegisteredAnalysisMethod
from .contracts import AnalysisRequest, AnalysisResult, EvidenceDescriptor, ResearchPhase, SubjectMetadata
from .method_catalog import MethodSpec, ParameterContract


METHOD_ID = "analysis.substrate.universe_market_structure"
LOGICAL_ANALYSIS_ID = "analysis:neutral-universe-market-structure:v1"
SUBSTRATE_VERSION = 1

STANDARD_FEATURE_COLUMNS = (
    "return_1__v1", "return_3__v1", "return_5__v1", "return_10__v1",
    "return_20__v1", "return_63__v1",
    "return_126__v1", "return_252__v1", "return_252_skip_20__v1",
    "close_to_sma_20__v1", "close_to_sma_50__v1", "close_to_sma_200__v1",
    "sma20_slope_5__v1", "rsi_14__v1", "natr_14__v1", "natr_20__v1",
    "realized_vol_20__v1", "realized_vol_63__v1", "relative_volume_20__v1",
    "gap_return__v1", "intraday_return__v1", "candle_range_fraction__v1",
    "close_location__v1", "drawdown_252__v1",
    "range_position_20__v1", "range_position_50__v1", "range_position_252__v1",
    "return_252_percentile__v1", "return_126_percentile__v1",
    "return_252_skip_20_percentile__v1", "relative_volume_20_percentile__v1",
    "natr_20_percentile__v1", "sector_return_252_percentile__v1",
)

BREADTH_COLUMNS = ("breadth_above_sma_200__v1", "breadth_positive_20__v1")
PERSISTENCE_COLUMNS = (
    "return_252_percentile__v1", "return_126_percentile__v1",
    "return_252_skip_20_percentile__v1", "relative_volume_20_percentile__v1",
)
WINDOWS = (5, 20, 63, 126, 252)
SUMMARY_FIELDS = (
    "n", "missing", "mean", "standard_deviation", "p10", "p25", "median",
    "p75", "p90", "minimum", "maximum",
)
WINDOW_TRANSPORT_FIELDS = (
    "n", "mean", "standard_deviation", "p10", "median", "p90",
    "start_value", "end_value", "change",
)


def required_feature_columns() -> tuple[str, ...]:
    """Return the frozen predictor-only input schema for this substrate."""
    return tuple(dict.fromkeys((*STANDARD_FEATURE_COLUMNS, *BREADTH_COLUMNS)))


def _finite(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        number = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _quantile(ordered: Sequence[float], probability: float) -> float | None:
    if not ordered:
        return None
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def _summary(values: Sequence[float], *, expected: int | None = None) -> Mapping[str, object]:
    ordered = sorted(values)
    n = len(ordered)
    return {
        "n": n,
        "missing": None if expected is None else expected - n,
        "mean": statistics.fmean(ordered) if ordered else None,
        "standard_deviation": statistics.stdev(ordered) if n > 1 else None,
        "p10": _quantile(ordered, 0.10),
        "p25": _quantile(ordered, 0.25),
        "median": _quantile(ordered, 0.50),
        "p75": _quantile(ordered, 0.75),
        "p90": _quantile(ordered, 0.90),
        "minimum": ordered[0] if ordered else None,
        "maximum": ordered[-1] if ordered else None,
    }


def _pearson(pairs: Sequence[tuple[float, float]]) -> float | None:
    if len(pairs) < 3:
        return None
    xs, ys = zip(*pairs)
    mean_x, mean_y = statistics.fmean(xs), statistics.fmean(ys)
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in pairs)
    denominator = math.sqrt(
        sum((x - mean_x) ** 2 for x in xs) * sum((y - mean_y) ** 2 for y in ys)
    )
    return None if denominator == 0 else numerator / denominator


def _correlations(rows: Sequence[Mapping[str, object]], columns: Sequence[str]) -> list[Mapping[str, object]]:
    output: list[Mapping[str, object]] = []
    for left, right in combinations(columns, 2):
        pairs = [
            (x, y) for row in rows
            if (x := _finite(row.get(left))) is not None
            and (y := _finite(row.get(right))) is not None
        ]
        output.append({"left": left, "right": right, "n": len(pairs), "pearson": _pearson(pairs)})
    return output


def _cross_section(rows: Sequence[Mapping[str, object]], columns: Sequence[str]) -> Mapping[str, object]:
    return {
        column: _summary(
            [value for row in rows if (value := _finite(row.get(column))) is not None],
            expected=len(rows),
        )
        for column in columns
    }


def _ordered_window_summary(rows: Sequence[Mapping[str, object]], column: str) -> Mapping[str, object]:
    values = [value for row in rows if (value := _finite(row.get(column))) is not None]
    summary = dict(_summary(values))
    summary.update({
        "start_value": values[0] if values else None,
        "end_value": values[-1] if values else None,
        "change": (values[-1] - values[0]) if len(values) > 1 else None,
    })
    return summary


def _pack_named_measurements(
    measurements: Mapping[str, object], fields: Sequence[str]
) -> Mapping[str, object]:
    return {
        "schema": ["measurement", *fields],
        "rows": [
            [name, *(value.get(field) for field in fields)]
            for name, value in measurements.items()
            if isinstance(value, Mapping)
        ],
    }


def _pack_correlations(records: object) -> Mapping[str, object]:
    usable = records if isinstance(records, (list, tuple)) else ()
    return {
        "schema": ["left", "right", "n", "pearson"],
        "rows": [
            [item.get("left"), item.get("right"), item.get("n"), item.get("pearson")]
            for item in usable if isinstance(item, Mapping)
        ],
    }


def compact_for_ai_transport(outputs: Mapping[str, object]) -> Mapping[str, object]:
    """Encode complete neutral context compactly without selecting scientific results.

    The full Analysis output remains authoritative and unchanged. This view keeps
    every feature, sector, horizon, correlation pair, and persistence record while
    eliminating repeated JSON field names. Multi-window distributions use one
    human-authorized descriptive schema uniformly for every measurement.
    """
    compact = {
        key: value for key, value in outputs.items()
        if key not in {
            "derived_datasets", "derived_dataset_catalog", "current_market_structure",
            "multi_horizon_context", "rank_persistence",
            "historical_daily_structure_correlations",
        }
    }
    current = outputs.get("current_market_structure", {})
    if not isinstance(current, Mapping):
        current = {}
    sectors = current.get("sector_measurements", {})
    if not isinstance(sectors, Mapping):
        sectors = {}
    compact["current_market_structure"] = {
        "effective_date": current.get("effective_date"),
        "security_count": current.get("security_count"),
        "breadth": current.get("breadth", {}),
        "participation": current.get("participation", {}),
        "cross_sectional_measurements": _pack_named_measurements(
            current.get("cross_sectional_measurements", {}), SUMMARY_FIELDS
        ),
        "sector_measurements": {
            str(sector): {
                "security_count": value.get("security_count"),
                "measurements": _pack_named_measurements(
                    value.get("measurements", {}), SUMMARY_FIELDS
                ),
            }
            for sector, value in sectors.items() if isinstance(value, Mapping)
        },
        "feature_correlations": _pack_correlations(current.get("feature_correlations", ())),
    }
    windows = outputs.get("multi_horizon_context", {})
    if not isinstance(windows, Mapping):
        windows = {}
    compact["multi_horizon_context"] = {
        str(window): {
            "observed_sessions": value.get("observed_sessions"),
            "start_date": value.get("start_date"),
            "end_date": value.get("end_date"),
            "measurements": _pack_named_measurements(
                value.get("measurements", {}), WINDOW_TRANSPORT_FIELDS
            ),
        }
        for window, value in windows.items() if isinstance(value, Mapping)
    }
    persistence = outputs.get("rank_persistence", ())
    compact["rank_persistence"] = {
        "schema": [
            "column", "lag_sessions", "prior_date", "current_date",
            "matched_securities", "pearson_rank_persistence",
        ],
        "rows": [
            [
                item.get("column"), item.get("lag_sessions"), item.get("prior_date"),
                item.get("current_date"), item.get("matched_securities"),
                item.get("pearson_rank_persistence"),
            ]
            for item in persistence if isinstance(item, Mapping)
        ] if isinstance(persistence, (list, tuple)) else [],
    }
    compact["historical_daily_structure_correlations"] = _pack_correlations(
        outputs.get("historical_daily_structure_correlations", ())
    )
    compact["transport_encoding"] = {
        "format": "MTS_V4_NEUTRAL_UNIVERSE_AI_TRANSPORT_V1",
        "scientific_selection_or_ranking": False,
        "all_features_sectors_horizons_and_correlation_pairs_retained": True,
        "full_analysis_output_unchanged": True,
        "large_reproducible_datasets_excluded": True,
        "derived_dataset_catalog_supplied_separately_by_campaign_result_catalog": True,
        "multi_window_fields_retained_uniformly": list(WINDOW_TRANSPORT_FIELDS),
        "multi_window_fields_available_only_in_full_analysis": [
            "missing", "p25", "p75", "minimum", "maximum",
        ],
    }
    return compact


def universe_market_structure(
    evidence_payloads: Mapping[str, object], parameters: Mapping[str, Any]
) -> Mapping[str, Any]:
    """Create neutral, as-of-safe universe structure measurements for later AI interpretation."""
    if len(evidence_payloads) != 1:
        raise ValueError(f"{METHOD_ID} requires exactly one predictor panel")
    raw = next(iter(evidence_payloads.values()))
    rows = tuple(raw)  # type: ignore[arg-type]
    if not rows or not all(isinstance(row, Mapping) for row in rows):
        raise ValueError("universe market structure input must contain row mappings")
    if any(str(key).startswith("forward_") for key in rows[0]):
        raise ValueError("neutral market-structure substrate prohibits historical outcome columns")

    as_of_date = str(parameters.get("as_of_date") or "").strip()
    as_of_time = str(parameters.get("as_of_time") or "DAILY_CLOSE").strip().upper()
    if as_of_time != "DAILY_CLOSE":
        raise ValueError("daily derived evidence supports only as_of_time=DAILY_CLOSE")
    available_dates = sorted({str(row.get("effective_date", ""))[:10] for row in rows})
    if not available_dates or not available_dates[0]:
        raise ValueError("effective_date is required")
    cutoff = as_of_date or available_dates[-1]
    eligible_rows = tuple(
        row for row in rows
        if str(row.get("effective_date", ""))[:10] <= cutoff and bool(row.get("eligible", True))
    )
    dates = sorted({str(row["effective_date"])[:10] for row in eligible_rows})
    if not dates:
        raise ValueError("no eligible observations exist at or before the requested as_of_date")
    effective_as_of = dates[-1]
    columns = tuple(column for column in STANDARD_FEATURE_COLUMNS if column in rows[0])
    missing_columns = tuple(column for column in STANDARD_FEATURE_COLUMNS if column not in rows[0])

    by_date: dict[str, list[Mapping[str, object]]] = {}
    for row in eligible_rows:
        by_date.setdefault(str(row["effective_date"])[:10], []).append(row)

    daily_panel: list[dict[str, object]] = []
    daily_columns = tuple(column for column in columns if column not in PERSISTENCE_COLUMNS)
    for effective_date in dates:
        date_rows = by_date[effective_date]
        record: dict[str, object] = {"effective_date": effective_date, "security_count": len(date_rows)}
        for breadth in BREADTH_COLUMNS:
            values = [value for row in date_rows if (value := _finite(row.get(breadth))) is not None]
            record[breadth] = statistics.median(values) if values else None
        participation_rules = {
            "fraction_positive_return_1": ("return_1__v1", 0.0),
            "fraction_positive_return_3": ("return_3__v1", 0.0),
            "fraction_positive_return_5": ("return_5__v1", 0.0),
            "fraction_positive_return_10": ("return_10__v1", 0.0),
            "fraction_positive_return_20": ("return_20__v1", 0.0),
            "fraction_positive_return_63": ("return_63__v1", 0.0),
            "fraction_positive_return_126": ("return_126__v1", 0.0),
            "fraction_positive_return_252": ("return_252__v1", 0.0),
            "fraction_above_sma_20": ("close_to_sma_20__v1", 0.0),
            "fraction_above_sma_50": ("close_to_sma_50__v1", 0.0),
            "fraction_above_sma_200": ("close_to_sma_200__v1", 0.0),
            "fraction_positive_sma20_slope_5": ("sma20_slope_5__v1", 0.0),
            "fraction_rsi_above_50": ("rsi_14__v1", 50.0),
        }
        for label, (column, threshold) in participation_rules.items():
            values = [value for row in date_rows if (value := _finite(row.get(column))) is not None]
            record[label] = None if not values else sum(value > threshold for value in values) / len(values)
        for column in daily_columns:
            values = [value for row in date_rows if (value := _finite(row.get(column))) is not None]
            summary = _summary(values)
            record[f"{column}__median"] = summary["median"]
            record[f"{column}__dispersion"] = summary["standard_deviation"]
            record[f"{column}__p10"] = summary["p10"]
            record[f"{column}__p90"] = summary["p90"]
        daily_panel.append(record)

    latest_rows = tuple(by_date[effective_as_of])
    security_attributes = parameters.get("security_attributes", {})
    if not isinstance(security_attributes, Mapping):
        raise ValueError("security_attributes must be a mapping keyed by security_id")

    def attributes_for(row: Mapping[str, object]) -> Mapping[str, object]:
        value = security_attributes.get(str(row["security_id"]), {})
        return value if isinstance(value, Mapping) else {}

    attribute_label_count = sum(bool(attributes_for(row).get("ticker")) for row in latest_rows)
    sector_label_count = sum(bool(attributes_for(row).get("sector_id")) for row in latest_rows)

    security_snapshot = [
        {
            "security_id": row.get("security_id"),
            "ticker": attributes_for(row).get("ticker"),
            "sector_id": attributes_for(row).get("sector_id"),
            "industry_id": attributes_for(row).get("industry_id"),
            **{key: row.get(key) for key in (*columns, *BREADTH_COLUMNS)},
        }
        for row in latest_rows
    ]
    latest_cross_section = _cross_section(latest_rows, columns)

    sector_snapshot: dict[str, object] = {}
    for sector in sorted({str(attributes_for(row).get("sector_id") or "UNCLASSIFIED") for row in latest_rows}):
        sector_rows = [
            row for row in latest_rows
            if str(attributes_for(row).get("sector_id") or "UNCLASSIFIED") == sector
        ]
        sector_snapshot[sector] = {
            "security_count": len(sector_rows),
            "measurements": _cross_section(
                sector_rows,
                tuple(column for column in columns if column in {
                    "return_3__v1", "return_5__v1", "return_10__v1", "return_20__v1",
                    "return_63__v1", "return_252__v1",
                    "return_252_skip_20__v1", "sma20_slope_5__v1", "natr_20__v1",
                    "relative_volume_20__v1", "drawdown_252__v1",
                }),
            ),
        }

    window_context: dict[str, object] = {}
    for window in WINDOWS:
        sample = daily_panel[-window:]
        numeric_keys = tuple(key for key in daily_panel[-1] if key != "effective_date")
        window_context[str(window)] = {
            "observed_sessions": len(sample),
            "start_date": sample[0]["effective_date"],
            "end_date": sample[-1]["effective_date"],
            "measurements": {
                key: _ordered_window_summary(sample, key)
                for key in numeric_keys
            },
        }

    persistence: list[Mapping[str, object]] = []
    latest_by_security = {str(row["security_id"]): row for row in latest_rows}
    for lag in WINDOWS:
        if len(dates) <= lag:
            continue
        prior_date = dates[-lag - 1]
        prior_by_security = {str(row["security_id"]): row for row in by_date[prior_date]}
        for column in PERSISTENCE_COLUMNS:
            pairs = []
            for security_id in sorted(set(latest_by_security) & set(prior_by_security)):
                current = _finite(latest_by_security[security_id].get(column))
                prior = _finite(prior_by_security[security_id].get(column))
                if current is not None and prior is not None:
                    pairs.append((prior, current))
            persistence.append({
                "column": column, "lag_sessions": lag, "prior_date": prior_date,
                "current_date": effective_as_of, "matched_securities": len(pairs),
                "pearson_rank_persistence": _pearson(pairs),
            })

    correlation_columns = columns

    return {
        "substrate_version": SUBSTRATE_VERSION,
        "policy": {
            "human_authorized_neutral_infrastructure": True,
            "predictor_time_information_only": True,
            "historical_outcomes_consumed": False,
            "deterministic_scientific_selection_or_ranking": False,
            "findings_created": False,
            "hypotheses_created": False,
            "ai_rd_retains_interpretation_and_research_direction_authority": True,
        },
        "observation_clock": {
            "requested_as_of_date": as_of_date or None,
            "effective_as_of_date": effective_as_of,
            "as_of_time": "DAILY_CLOSE",
            "frequency": "DAILY",
            "intraday_state_available": False,
        },
        "coverage": {
            "first_date": dates[0], "last_date": dates[-1], "observed_sessions": len(dates),
            "input_rows": len(rows), "eligible_rows_through_cutoff": len(eligible_rows),
            "unique_securities": len({str(row["security_id"]) for row in eligible_rows}),
            "latest_security_count": len(latest_rows),
            "daily_security_count": _summary([float(len(by_date[item])) for item in dates]),
            "current_attribute_labels_available": attribute_label_count,
            "current_sector_labels_available": sector_label_count,
        },
        "capability_manifest": {
            "current_cross_section": True, "multi_horizon_returns": True,
            "trend_level_and_slope": True, "momentum": True, "volatility": True,
            "volume_participation": True, "breadth": True, "dispersion": True,
            "sector_structure": sector_label_count > 0, "rank_persistence": True,
            "feature_dependence": True, "drawdown_and_range_position": True,
            "intraday_market_structure": False, "future_outcome_relationships": False,
            "path_executable_trade_outcomes": False, "market_cap_weighting": False,
        },
        "feature_inventory": {"available": list(columns), "missing": list(missing_columns)},
        "current_market_structure": {
            "effective_date": effective_as_of,
            "security_count": len(latest_rows),
            "breadth": {column: latest_rows[0].get(column) for column in BREADTH_COLUMNS},
            "participation": {
                key: value for key, value in daily_panel[-1].items()
                if key.startswith("fraction_")
            },
            "cross_sectional_measurements": latest_cross_section,
            "sector_measurements": sector_snapshot,
            "feature_correlations": _correlations(latest_rows, correlation_columns),
        },
        "multi_horizon_context": window_context,
        "rank_persistence": persistence,
        "historical_daily_structure_correlations": _correlations(
            daily_panel,
            tuple(key for key in daily_panel[-1] if key.endswith("__median")),
        ),
        "limitations": (
            "CURRENT_CONSTITUENT_CALIBRATION_UNIVERSE; FORMER_CONSTITUENTS_ABSENT",
            "HISTORICAL_CROSS_SECTIONS_ARE_NOT_AUTHORITATIVE_S_AND_P_500_PIT_RECONSTRUCTIONS",
            "DAILY_COMPLETED_OBSERVATIONS_ONLY; NO_INTRADAY_T_TIME_STATE",
            "CURRENT_SECTOR_ATTRIBUTES_ARE_NOT_AUTHORITATIVE_HISTORICAL_PIT_CLASSIFICATIONS",
            "NO_HISTORICAL_OUTCOMES_OR_PREDICTIVE_CLAIMS_IN_THIS_SUBSTRATE",
        ),
        "derived_dataset_catalog": {
            "daily_market_structure_panel": {
                "row_count": len(daily_panel), "schema": list(daily_panel[-1]),
                "output_path": ["derived_datasets", "daily_market_structure_panel"], "temporary": True,
            },
            "current_security_snapshot": {
                "row_count": len(security_snapshot), "schema": list(security_snapshot[0]),
                "output_path": ["derived_datasets", "current_security_snapshot"], "temporary": True,
            },
        },
        "derived_datasets": {
            "daily_market_structure_panel": daily_panel,
            "current_security_snapshot": security_snapshot,
        },
        "interpretation_boundary": "NEUTRAL_MARKET_STRUCTURE_MEASUREMENTS_ONLY_AI_RD_INTERPRETS",
    }


def method_spec() -> MethodSpec:
    return MethodSpec(
        METHOD_ID, ("TABULAR",),
        "Human-authorized neutral full-universe predictor-time market-structure substrate before AI interpretation.",
        (
            ParameterContract("as_of_date", False, (str,)),
            ParameterContract("as_of_time", False, (str,)),
            ParameterContract("security_attributes", False, (dict,)),
        ),
        minimum_sample=1,
        exploration_allowed=True,
        validation_allowed=False,
        allows_future_information=False,
        metadata={"scientific_selection": "none", "human_authorized_infrastructure": True,
                  "future_information": False, "reusable_derived_dataset": True},
    )


def analysis_method() -> RegisteredAnalysisMethod:
    return RegisteredAnalysisMethod(METHOD_ID, universe_market_structure)


def build_for_universe(
    *, subject: SubjectMetadata, evidence: Sequence[EvidenceDescriptor], cache, analysis,
    as_of_date: str | None = None, security_attributes: Mapping[str, Mapping[str, object]] | None = None,
) -> Mapping[str, AnalysisResult]:
    candidates = [
        item for item in evidence
        if item.evidence_type == "DERIVED_MARKET_PANEL"
        and not bool(item.provenance.get("contains_future_outcomes"))
    ]
    if len(candidates) != 1:
        raise RuntimeError("neutral universe substrate requires exactly one predictor-only derived panel")
    descriptor = candidates[0]
    request = AnalysisRequest(
        request_id=f"neutral-universe-substrate:{subject.subject_id}:v1",
        subject_id=subject.subject_id,
        question="Human-authorized neutral as-of market-structure representation.",
        method_id=METHOD_ID,
        evidence_ids=(descriptor.evidence_id,),
        parameters={
            "as_of_date": as_of_date or "", "as_of_time": "DAILY_CLOSE",
            "security_attributes": dict(security_attributes or {}),
        },
        research_phase=ResearchPhase.EXPLORATION,
        rationale="Represent observable universe structure before AI scientific interpretation.",
    )
    result = analysis.execute(request, {descriptor.evidence_id: cache.get(descriptor.cache_key)})
    if result.execution_metadata.get("execution_status") != "SUCCESS":
        raise RuntimeError(f"neutral universe Analysis substrate failed: {result.outputs.get('execution_error')}")
    return {LOGICAL_ANALYSIS_ID: replace(result, limitations=tuple(result.outputs.get("limitations", ())))}
