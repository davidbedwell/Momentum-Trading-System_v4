from __future__ import annotations

import math
import statistics
from collections import defaultdict
from typing import Any, Mapping, Sequence

from .derived_market_store import DerivedFeatureDefinition, DerivedFeatureSetDefinition


PREDICTOR_FEATURE_SET_ID = "mts_market_predictors"
PREDICTOR_FEATURE_SET_VERSION = "v1"
OUTCOME_FEATURE_SET_ID = "mts_historical_outcomes"
OUTCOME_FEATURE_SET_VERSION = "v1"

RETURN_WINDOWS = (1, 3, 5, 10, 20, 63, 126, 252)
RANGE_WINDOWS = (20, 50, 252)
SMA_WINDOWS = (20, 50, 200)
REALIZED_VOL_WINDOWS = (20, 63)
FORWARD_HORIZONS = (1, 3, 5, 10, 20, 63)


def _feature(feature_id: str, description: str, lookback: int, *, dependencies=("OHLCV",), classification="PREDICTOR") -> DerivedFeatureDefinition:
    return DerivedFeatureDefinition(
        feature_id=feature_id,
        version="v1",
        description=description,
        dependencies=tuple(dependencies),
        required_lookback_sessions=lookback,
        classification=classification,
    )


def standard_predictor_feature_set() -> DerivedFeatureSetDefinition:
    features: list[DerivedFeatureDefinition] = []
    for window in RETURN_WINDOWS:
        features.append(_feature(f"return_{window}", f"Close-to-close trailing {window}-session return", window))
    for window in SMA_WINDOWS:
        features.extend((
            _feature(f"sma_{window}", f"Simple moving average of close over {window} sessions", window),
            _feature(f"close_to_sma_{window}", f"Close divided by SMA{window} minus one", window),
        ))
    features.extend((
        _feature("sma20_slope_5", "Five-session fractional change in SMA20", 25),
        _feature("atr_14", "Wilder-style simple-window true-range average over 14 sessions", 15),
        _feature("atr_20", "Simple-window true-range average over 20 sessions", 21),
        _feature("natr_14", "ATR14 divided by close", 15),
        _feature("natr_20", "ATR20 divided by close", 21),
        _feature("relative_volume_20", "Current volume divided by prior-20-session mean volume", 21),
        _feature("turnover", "Current volume divided by point-in-time shares outstanding when available", 1, dependencies=("OHLCV", "POINT_IN_TIME_SHARES")),
        _feature("turnover_relative_20", "Current turnover divided by prior-20-session mean turnover when point-in-time shares are available", 21, dependencies=("OHLCV", "POINT_IN_TIME_SHARES")),
        _feature("rsi_14", "Wilder RSI over 14 close changes", 15),
        _feature("gap_return", "Open divided by prior close minus one", 1),
        _feature("intraday_return", "Close divided by open minus one", 0),
        _feature("candle_range_fraction", "High-low range divided by close", 0),
        _feature("close_location", "Close location within same-session high-low range", 0),
        _feature("drawdown_252", "Close divided by trailing 252-session high minus one", 252),
    ))
    for window in REALIZED_VOL_WINDOWS:
        features.append(_feature(f"realized_vol_{window}", f"Annualized standard deviation of daily log returns over {window} sessions", window + 1))
    for window in RANGE_WINDOWS:
        features.append(_feature(f"range_position_{window}", f"Close position within trailing {window}-session low/high range", window))
    # Expensive/inherently contemporaneous measurements worth retaining.
    features.extend((
        _feature("return_252_percentile", "Point-in-time universe percentile of trailing 252-session return", 252, dependencies=("OHLCV", "POINT_IN_TIME_UNIVERSE")),
        _feature("return_126_percentile", "Point-in-time universe percentile of trailing 126-session return", 126, dependencies=("OHLCV", "POINT_IN_TIME_UNIVERSE")),
        _feature("relative_volume_20_percentile", "Point-in-time universe percentile of relative volume 20", 21, dependencies=("OHLCV", "POINT_IN_TIME_UNIVERSE")),
        _feature("natr_20_percentile", "Point-in-time universe percentile of normalized ATR20", 21, dependencies=("OHLCV", "POINT_IN_TIME_UNIVERSE")),
        _feature("sector_return_252_percentile", "Point-in-time sector percentile of trailing 252-session return", 252, dependencies=("OHLCV", "POINT_IN_TIME_UNIVERSE", "POINT_IN_TIME_SECTOR")),
        _feature("breadth_above_sma_200", "Point-in-time eligible-universe fraction closing above SMA200", 200, dependencies=("OHLCV", "POINT_IN_TIME_UNIVERSE")),
        _feature("breadth_positive_20", "Point-in-time eligible-universe fraction with positive 20-session return", 20, dependencies=("OHLCV", "POINT_IN_TIME_UNIVERSE")),
    ))
    return DerivedFeatureSetDefinition(
        feature_set_id=PREDICTOR_FEATURE_SET_ID,
        version=PREDICTOR_FEATURE_SET_VERSION,
        description="Versioned reusable point-in-time market predictor/context substrate; measurements, not conclusions.",
        features=tuple(features),
        attributes={"future_information": False, "scientific_selection": "none"},
    )


def standard_outcome_feature_set() -> DerivedFeatureSetDefinition:
    features = tuple(
        _feature(
            f"forward_return_{horizon}",
            f"Close-to-close forward {horizon}-session historical outcome",
            0,
            classification="OUTCOME",
        )
        for horizon in FORWARD_HORIZONS
    )
    return DerivedFeatureSetDefinition(
        feature_set_id=OUTCOME_FEATURE_SET_ID,
        version=OUTCOME_FEATURE_SET_VERSION,
        description="Historical future outcomes stored separately and published only after each observation is mature.",
        features=features,
        attributes={"future_information": True, "live_predictor_access": "PROHIBITED"},
    )


def _finite(value: object) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _ratio(a: float | None, b: float | None, *, subtract_one: bool = False) -> float | None:
    if a is None or b is None or b == 0:
        return None
    value = a / b
    return value - 1.0 if subtract_one else value


def _mean(values: Sequence[float | None]) -> float | None:
    usable = [value for value in values if value is not None]
    return statistics.fmean(usable) if usable and len(usable) == len(values) else None


def _percentile_assign(rows: list[dict[str, Any]], column: str, output: str, *, group_column: str | None = None) -> None:
    groups: dict[object, list[tuple[int, float]]] = defaultdict(list)
    for index, row in enumerate(rows):
        value = _finite(row.get(column))
        if value is None or not row.get("eligible", True):
            row[output] = None
            continue
        key = row.get(group_column) if group_column else "__ALL__"
        if group_column and key in (None, ""):
            row[output] = None
            continue
        groups[key].append((index, value))
    for observations in groups.values():
        observations.sort(key=lambda item: item[1])
        n = len(observations)
        pos = 0
        while pos < n:
            end = pos + 1
            while end < n and observations[end][1] == observations[pos][1]:
                end += 1
            rank = ((pos + 1) + end) / 2.0
            percentile = 1.0 if n == 1 else (rank - 1.0) / (n - 1.0)
            for offset in range(pos, end):
                rows[observations[offset][0]][output] = percentile
            pos = end


def build_predictor_rows(raw_rows: Sequence[Mapping[str, Any]]) -> tuple[Mapping[str, Any], ...]:
    """Build deterministic point-in-time predictor rows from normalized daily source rows.

    Required raw columns: security_id,date,open,high,low,close,volume,eligible.
    Optional point-in-time columns: ticker,sector_id,industry_id,shares_outstanding.
    Input may include lookback rows before the publication window; callers decide
    which effective dates are ultimately appended to Nexus.
    """
    by_security: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for raw in raw_rows:
        by_security[str(raw["security_id"])].append(raw)
    output: list[dict[str, Any]] = []
    for security_id, source in by_security.items():
        ordered = sorted(source, key=lambda row: str(row["date"]))
        closes = [_finite(row.get("close")) for row in ordered]
        highs = [_finite(row.get("high")) for row in ordered]
        lows = [_finite(row.get("low")) for row in ordered]
        opens = [_finite(row.get("open")) for row in ordered]
        volumes = [_finite(row.get("volume")) for row in ordered]
        shares = [_finite(row.get("shares_outstanding")) for row in ordered]
        turnovers = [_ratio(volumes[i], shares[i]) for i in range(len(ordered))]
        true_ranges: list[float | None] = []
        log_returns: list[float | None] = []
        for i in range(len(ordered)):
            if highs[i] is None or lows[i] is None:
                true_ranges.append(None)
            elif i == 0 or closes[i - 1] is None:
                true_ranges.append(highs[i] - lows[i])
            else:
                true_ranges.append(max(highs[i] - lows[i], abs(highs[i] - closes[i - 1]), abs(lows[i] - closes[i - 1])))
            if i == 0 or closes[i] is None or closes[i - 1] is None or closes[i] <= 0 or closes[i - 1] <= 0:
                log_returns.append(None)
            else:
                log_returns.append(math.log(closes[i] / closes[i - 1]))

        sma_cache: dict[int, list[float | None]] = {window: [] for window in SMA_WINDOWS}
        for i, raw in enumerate(ordered):
            row: dict[str, Any] = {
                "security_id": security_id,
                "effective_date": str(raw["date"]),
                "eligible": bool(raw.get("eligible", True)),
                "ticker": raw.get("ticker"),
                "sector_id": raw.get("sector_id"),
                "industry_id": raw.get("industry_id"),
                "eligibility_reason": raw.get("eligibility_reason"),
            }
            close = closes[i]
            for window in RETURN_WINDOWS:
                row[f"return_{window}__v1"] = _ratio(close, closes[i - window] if i >= window else None, subtract_one=True)
            for window in SMA_WINDOWS:
                sma = _mean(closes[i - window + 1:i + 1]) if i + 1 >= window else None
                sma_cache[window].append(sma)
                row[f"sma_{window}__v1"] = sma
                row[f"close_to_sma_{window}__v1"] = _ratio(close, sma, subtract_one=True)
            current_sma20 = sma_cache[20][i]
            prior_sma20 = sma_cache[20][i - 5] if i >= 5 else None
            row["sma20_slope_5__v1"] = _ratio(current_sma20, prior_sma20, subtract_one=True)
            atr14 = _mean(true_ranges[i - 13:i + 1]) if i >= 13 else None
            atr20 = _mean(true_ranges[i - 19:i + 1]) if i >= 19 else None
            row["atr_14__v1"] = atr14
            row["atr_20__v1"] = atr20
            row["natr_14__v1"] = _ratio(atr14, close)
            row["natr_20__v1"] = _ratio(atr20, close)
            prior_vol = _mean(volumes[i - 20:i]) if i >= 20 else None
            row["relative_volume_20__v1"] = _ratio(volumes[i], prior_vol)
            row["turnover__v1"] = turnovers[i]
            prior_turnover = _mean(turnovers[i - 20:i]) if i >= 20 else None
            row["turnover_relative_20__v1"] = _ratio(turnovers[i], prior_turnover)
            if i >= 14:
                changes = [None if closes[j] is None or closes[j - 1] is None else closes[j] - closes[j - 1] for j in range(i - 13, i + 1)]
                if all(change is not None for change in changes):
                    gains = statistics.fmean(max(0.0, float(change)) for change in changes)
                    losses = statistics.fmean(max(0.0, -float(change)) for change in changes)
                    row["rsi_14__v1"] = 100.0 if losses == 0 else 100.0 - 100.0 / (1.0 + gains / losses)
                else:
                    row["rsi_14__v1"] = None
            else:
                row["rsi_14__v1"] = None
            row["gap_return__v1"] = _ratio(opens[i], closes[i - 1] if i else None, subtract_one=True)
            row["intraday_return__v1"] = _ratio(close, opens[i], subtract_one=True)
            row["candle_range_fraction__v1"] = _ratio((highs[i] - lows[i]) if highs[i] is not None and lows[i] is not None else None, close)
            if highs[i] is None or lows[i] is None or close is None or highs[i] == lows[i]:
                row["close_location__v1"] = None
            else:
                row["close_location__v1"] = (close - lows[i]) / (highs[i] - lows[i])
            trailing_high = max((value for value in highs[max(0, i - 251):i + 1] if value is not None), default=None) if i >= 251 else None
            row["drawdown_252__v1"] = _ratio(close, trailing_high, subtract_one=True)
            for window in REALIZED_VOL_WINDOWS:
                sample = log_returns[i - window + 1:i + 1] if i >= window else []
                row[f"realized_vol_{window}__v1"] = statistics.stdev(sample) * math.sqrt(252.0) if len(sample) == window and all(value is not None for value in sample) and window > 1 else None
            for window in RANGE_WINDOWS:
                if i + 1 < window:
                    row[f"range_position_{window}__v1"] = None
                else:
                    window_high = max(value for value in highs[i - window + 1:i + 1] if value is not None) if all(value is not None for value in highs[i - window + 1:i + 1]) else None
                    window_low = min(value for value in lows[i - window + 1:i + 1] if value is not None) if all(value is not None for value in lows[i - window + 1:i + 1]) else None
                    row[f"range_position_{window}__v1"] = None if close is None or window_high is None or window_low is None or window_high == window_low else (close - window_low) / (window_high - window_low)
            output.append(row)

    by_date: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in output:
        by_date[row["effective_date"]].append(row)
    for date_rows in by_date.values():
        _percentile_assign(date_rows, "return_252__v1", "return_252_percentile__v1")
        _percentile_assign(date_rows, "return_126__v1", "return_126_percentile__v1")
        _percentile_assign(date_rows, "relative_volume_20__v1", "relative_volume_20_percentile__v1")
        _percentile_assign(date_rows, "natr_20__v1", "natr_20_percentile__v1")
        _percentile_assign(date_rows, "return_252__v1", "sector_return_252_percentile__v1", group_column="sector_id")
        eligible = [row for row in date_rows if row.get("eligible", True)]
        breadth_sma = [row for row in eligible if row.get("close_to_sma_200__v1") is not None]
        breadth_ret = [row for row in eligible if row.get("return_20__v1") is not None]
        above = None if not breadth_sma else sum(row["close_to_sma_200__v1"] > 0 for row in breadth_sma) / len(breadth_sma)
        positive = None if not breadth_ret else sum(row["return_20__v1"] > 0 for row in breadth_ret) / len(breadth_ret)
        for row in date_rows:
            row["breadth_above_sma_200__v1"] = above
            row["breadth_positive_20__v1"] = positive
    return tuple(sorted(output, key=lambda row: (row["effective_date"], row["security_id"])))


def build_matured_outcome_rows(raw_rows: Sequence[Mapping[str, Any]]) -> tuple[Mapping[str, Any], ...]:
    """Build historical outcomes. Caller publishes only dates mature for max requested horizon."""
    by_security: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for raw in raw_rows:
        by_security[str(raw["security_id"])].append(raw)
    output: list[dict[str, Any]] = []
    for security_id, source in by_security.items():
        ordered = sorted(source, key=lambda row: str(row["date"]))
        closes = [_finite(row.get("close")) for row in ordered]
        for i, raw in enumerate(ordered):
            row = {
                "security_id": security_id,
                "effective_date": str(raw["date"]),
                "eligible": bool(raw.get("eligible", True)),
                "ticker": raw.get("ticker"),
                "sector_id": raw.get("sector_id"),
                "industry_id": raw.get("industry_id"),
                "eligibility_reason": raw.get("eligibility_reason"),
            }
            for horizon in FORWARD_HORIZONS:
                row[f"forward_return_{horizon}__v1"] = _ratio(closes[i + horizon] if i + horizon < len(closes) else None, closes[i], subtract_one=True)
            output.append(row)
    return tuple(sorted(output, key=lambda row: (row["effective_date"], row["security_id"])))
