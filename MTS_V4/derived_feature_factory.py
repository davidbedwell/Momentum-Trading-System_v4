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
    features.extend((
        _feature("return_252_skip_20", "Close-to-close return from 252 sessions ago through 20 sessions ago; excludes the most recent 20 sessions for a canonical medium-term momentum control", 252),
        _feature("return_252_skip_20_percentile", "Point-in-time universe percentile of 252-to-20-session skipped-month return", 252, dependencies=("OHLCV", "POINT_IN_TIME_UNIVERSE")),
    ))
    for window in SMA_WINDOWS:
        features.extend((
            _feature(f"sma_{window}", f"Simple moving average of close over {window} sessions", window),
            _feature(f"close_to_sma_{window}", f"Close divided by SMA{window} minus one", window),
        ))
    features.extend((
        _feature("sma20_slope_5", "Five-session fractional change in SMA20", 25),
        _feature("sma50_slope_10", "Ten-session fractional change in SMA50", 60),
        _feature("sma200_slope_20", "Twenty-session fractional change in SMA200", 220),
        _feature("trend_above_sma200_duration", "Consecutive sessions close has remained above SMA200; negative count when below", 200),
        _feature("pullback_from_high_20", "Close divided by prior 20-session high minus one", 21),
        _feature("prior_high_break_distance_20", "Close divided by prior 20-session high minus one; excludes current session from high", 21),
        _feature("prior_high_break_distance_50", "Close divided by prior 50-session high minus one; excludes current session from high", 51),
        _feature("range_width_20", "Prior/current 20-session high-low width divided by close", 20),
        _feature("range_width_ratio_20_63", "20-session range width divided by 63-session range width", 63),
        _feature("price_zscore_20", "Close z-score relative to trailing 20-session close distribution", 20),
        _feature("signed_return_streak", "Signed consecutive-session close-to-close return streak", 1),
        _feature("volatility_ratio_20_63", "Realized volatility 20 divided by realized volatility 63", 64),
        _feature("dollar_volume", "Close multiplied by volume", 0),
        _feature("dollar_volume_relative_20", "Current dollar volume divided by prior-20-session mean dollar volume", 21),
        _feature("amihud_illiquidity_20", "Mean absolute daily return divided by dollar volume over 20 sessions", 21),
        _feature("high_low_spread_proxy", "Same-session high-low spread proxy divided by midrange", 0),
        _feature("volume_slope_20", "Linear slope of volume over 20 sessions normalized by mean volume", 20),
        _feature("up_down_volume_balance_20", "Signed up-day minus down-day volume divided by total volume over 20 sessions", 21),
        _feature("adx_14", "14-session Average Directional Index from OHLC directional movement and true range", 28),
        _feature("compression_duration", "Consecutive sessions with 20/63 range-width ratio below 0.75", 63),
        _feature("volatility_contraction_duration", "Consecutive sessions with realized-volatility 20/63 ratio below 0.75", 64),
        _feature("volatility_expansion_transition", "Current realized-volatility 20/63 ratio minus its value five sessions earlier", 69),
        _feature("failed_breakout_20", "One when prior session closed above its prior-20 high and current close is back below that prior breakout level", 22),
        _feature("breakout_reentry_20", "One when current close reclaims prior-20 high after a failed-breakout observation in the prior five sessions", 27),
        _feature("exhaustion_score", "Signed displacement composite of price z-score, RSI and close location", 20),
        _feature("relative_strength_change_20", "Twenty-session change in point-in-time 126-session return percentile", 146, dependencies=("OHLCV", "POINT_IN_TIME_UNIVERSE")),
        _feature("sector_vs_universe_return_63", "Security 63-session return minus same-date eligible-universe median 63-session return", 63, dependencies=("OHLCV", "POINT_IN_TIME_UNIVERSE")),
        _feature("advance_decline_breadth", "Point-in-time eligible-universe fraction advancing minus fraction declining on the session", 1, dependencies=("OHLCV", "POINT_IN_TIME_UNIVERSE")),
        _feature("new_high_low_breadth_252", "Point-in-time fraction at new 252-session highs minus fraction at new 252-session lows", 252, dependencies=("OHLCV", "POINT_IN_TIME_UNIVERSE")),
        _feature("realized_vol_20_percentile", "Point-in-time universe percentile of realized volatility 20", 21, dependencies=("OHLCV", "POINT_IN_TIME_UNIVERSE")),
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
        dollar_volumes = [None if closes[i] is None or volumes[i] is None else closes[i] * volumes[i] for i in range(len(ordered))]
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
            row["return_252_skip_20__v1"] = _ratio(
                closes[i - 20] if i >= 252 else None,
                closes[i - 252] if i >= 252 else None,
                subtract_one=True,
            )
            for window in SMA_WINDOWS:
                sma = _mean(closes[i - window + 1:i + 1]) if i + 1 >= window else None
                sma_cache[window].append(sma)
                row[f"sma_{window}__v1"] = sma
                row[f"close_to_sma_{window}__v1"] = _ratio(close, sma, subtract_one=True)
            current_sma20 = sma_cache[20][i]
            prior_sma20 = sma_cache[20][i - 5] if i >= 5 else None
            row["sma20_slope_5__v1"] = _ratio(current_sma20, prior_sma20, subtract_one=True)
            row["sma50_slope_10__v1"] = _ratio(sma_cache[50][i], sma_cache[50][i - 10] if i >= 10 else None, subtract_one=True)
            row["sma200_slope_20__v1"] = _ratio(sma_cache[200][i], sma_cache[200][i - 20] if i >= 20 else None, subtract_one=True)
            relation = row["close_to_sma_200__v1"]
            if relation is None:
                row["trend_above_sma200_duration__v1"] = None
            else:
                sign = 1 if relation > 0 else -1 if relation < 0 else 0
                duration = 0
                j = i
                while j >= 0:
                    sma_j = sma_cache[200][j]
                    rel_j = _ratio(closes[j], sma_j, subtract_one=True)
                    sign_j = None if rel_j is None else (1 if rel_j > 0 else -1 if rel_j < 0 else 0)
                    if sign_j != sign:
                        break
                    duration += 1
                    j -= 1
                row["trend_above_sma200_duration__v1"] = float(sign * duration)
            prior_high20 = max((v for v in highs[max(0, i - 20):i] if v is not None), default=None) if i >= 20 else None
            prior_high50 = max((v for v in highs[max(0, i - 50):i] if v is not None), default=None) if i >= 50 else None
            row["pullback_from_high_20__v1"] = _ratio(close, prior_high20, subtract_one=True)
            row["prior_high_break_distance_20__v1"] = row["pullback_from_high_20__v1"]
            row["prior_high_break_distance_50__v1"] = _ratio(close, prior_high50, subtract_one=True)
            def range_width(window: int) -> float | None:
                if i + 1 < window or close in (None, 0):
                    return None
                hs, ls = highs[i-window+1:i+1], lows[i-window+1:i+1]
                if any(v is None for v in (*hs, *ls)):
                    return None
                return (max(hs) - min(ls)) / close
            width20, width63 = range_width(20), range_width(63)
            row["range_width_20__v1"] = width20
            row["range_width_ratio_20_63__v1"] = _ratio(width20, width63)
            if i + 1 >= 20 and close is not None:
                sample_close = closes[i-19:i+1]
                if all(v is not None for v in sample_close):
                    mean_close = statistics.fmean(sample_close)
                    sd_close = statistics.stdev(sample_close)
                    row["price_zscore_20__v1"] = None if sd_close == 0 else (close - mean_close) / sd_close
                else:
                    row["price_zscore_20__v1"] = None
            else:
                row["price_zscore_20__v1"] = None
            streak = 0
            j = i
            while j > 0 and closes[j] is not None and closes[j-1] is not None:
                delta = closes[j] - closes[j-1]
                current_sign = 1 if delta > 0 else -1 if delta < 0 else 0
                if current_sign == 0:
                    break
                if streak == 0:
                    streak = current_sign
                elif (streak > 0) != (current_sign > 0):
                    break
                else:
                    streak += current_sign
                j -= 1
            row["signed_return_streak__v1"] = float(streak)
            def linear_slope(values: Sequence[float | None]) -> float | None:
                if not values or any(v is None for v in values):
                    return None
                ys = [float(v) for v in values]
                mean_y = statistics.fmean(ys)
                if mean_y == 0:
                    return None
                mean_x = (len(ys) - 1) / 2.0
                denom = sum((x - mean_x) ** 2 for x in range(len(ys)))
                return sum((x - mean_x) * (y - mean_y) for x, y in enumerate(ys)) / denom / mean_y
            row["volume_slope_20__v1"] = linear_slope(volumes[i-19:i+1]) if i >= 19 else None
            if i >= 20:
                signed_volume = []
                total_volume = 0.0
                valid = True
                for j in range(i-19, i+1):
                    if volumes[j] is None or closes[j] is None or closes[j-1] is None:
                        valid = False
                        break
                    direction = 1.0 if closes[j] > closes[j-1] else -1.0 if closes[j] < closes[j-1] else 0.0
                    signed_volume.append(direction * volumes[j])
                    total_volume += volumes[j]
                row["up_down_volume_balance_20__v1"] = None if not valid or total_volume == 0 else sum(signed_volume) / total_volume
            else:
                row["up_down_volume_balance_20__v1"] = None
            atr14 = _mean(true_ranges[i - 13:i + 1]) if i >= 13 else None
            atr20 = _mean(true_ranges[i - 19:i + 1]) if i >= 19 else None
            row["atr_14__v1"] = atr14
            row["atr_20__v1"] = atr20
            row["natr_14__v1"] = _ratio(atr14, close)
            row["natr_20__v1"] = _ratio(atr20, close)
            midrange = None if highs[i] is None or lows[i] is None else (highs[i] + lows[i]) / 2.0
            row["high_low_spread_proxy__v1"] = _ratio((highs[i] - lows[i]) if highs[i] is not None and lows[i] is not None else None, midrange)
            if i >= 14:
                plus_dm, minus_dm, trs = [], [], []
                for j in range(i-13, i+1):
                    if j == 0 or highs[j] is None or highs[j-1] is None or lows[j] is None or lows[j-1] is None or true_ranges[j] is None:
                        plus_dm = []; break
                    up = highs[j] - highs[j-1]
                    down = lows[j-1] - lows[j]
                    plus_dm.append(up if up > down and up > 0 else 0.0)
                    minus_dm.append(down if down > up and down > 0 else 0.0)
                    trs.append(true_ranges[j])
                tr_mean = _mean(trs)
                p = None if not plus_dm or tr_mean in (None,0) else 100.0 * statistics.fmean(plus_dm) / tr_mean
                m = None if not minus_dm or tr_mean in (None,0) else 100.0 * statistics.fmean(minus_dm) / tr_mean
                row["adx_14__v1"] = None if p is None or m is None or p + m == 0 else 100.0 * abs(p-m)/(p+m)
            else:
                row["adx_14__v1"] = None
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
            row["volatility_ratio_20_63__v1"] = _ratio(row["realized_vol_20__v1"], row["realized_vol_63__v1"])
            current_vr = row["volatility_ratio_20_63__v1"]
            prior_vr = None
            if i >= 5:
                sample20 = log_returns[i-5-20+1:i-5+1] if i-5 >= 20 else []
                sample63 = log_returns[i-5-63+1:i-5+1] if i-5 >= 63 else []
                rv20p = statistics.stdev(sample20)*math.sqrt(252.0) if len(sample20)==20 and all(v is not None for v in sample20) else None
                rv63p = statistics.stdev(sample63)*math.sqrt(252.0) if len(sample63)==63 and all(v is not None for v in sample63) else None
                prior_vr = _ratio(rv20p, rv63p)
            row["volatility_expansion_transition__v1"] = None if current_vr is None or prior_vr is None else current_vr-prior_vr
            contraction = 0
            if current_vr is not None and current_vr < 0.75:
                j=i
                while j>=63:
                    s20=log_returns[j-19:j+1]; s63=log_returns[j-62:j+1]
                    if not (all(v is not None for v in s20) and all(v is not None for v in s63)): break
                    ratio=_ratio(statistics.stdev(s20)*math.sqrt(252.0),statistics.stdev(s63)*math.sqrt(252.0))
                    if ratio is None or ratio>=0.75: break
                    contraction+=1; j-=1
            row["volatility_contraction_duration__v1"]=float(contraction)
            row["dollar_volume__v1"] = dollar_volumes[i]
            prior_dv = _mean(dollar_volumes[i-20:i]) if i >= 20 else None
            row["dollar_volume_relative_20__v1"] = _ratio(dollar_volumes[i], prior_dv)
            if i >= 20:
                illiq = []
                for j in range(i-19, i+1):
                    dv = dollar_volumes[j]
                    ret = _ratio(closes[j], closes[j-1] if j else None, subtract_one=True)
                    illiq.append(None if dv in (None, 0) or ret is None else abs(ret) / dv)
                row["amihud_illiquidity_20__v1"] = _mean(illiq)
            else:
                row["amihud_illiquidity_20__v1"] = None
            compression = 0
            if row["range_width_ratio_20_63__v1"] is not None and row["range_width_ratio_20_63__v1"] < 0.75:
                j=i
                while j>=62:
                    def rw_at(k:int,w:int):
                        if k+1<w or closes[k] in (None,0): return None
                        hs=highs[k-w+1:k+1]; ls=lows[k-w+1:k+1]
                        if any(v is None for v in (*hs,*ls)): return None
                        return (max(hs)-min(ls))/closes[k]
                    rr=_ratio(rw_at(j,20),rw_at(j,63))
                    if rr is None or rr>=0.75: break
                    compression+=1; j-=1
            row["compression_duration__v1"]=float(compression)
            prior_break = None
            if i>=21 and closes[i-1] is not None:
                ph=max(v for v in highs[i-21:i-1] if v is not None) if all(v is not None for v in highs[i-21:i-1]) else None
                prior_break=ph
            row["failed_breakout_20__v1"] = 1.0 if prior_break is not None and closes[i-1] > prior_break and close is not None and close < prior_break else 0.0
            recent_failed=False
            if i>=25:
                for k in range(max(21,i-5),i):
                    ph=max(v for v in highs[k-21:k-1] if v is not None) if all(v is not None for v in highs[k-21:k-1]) else None
                    if ph is not None and closes[k-1] is not None and closes[k] is not None and closes[k-1]>ph and closes[k]<ph:
                        recent_failed=True; break
            current_prior20=max((v for v in highs[i-20:i] if v is not None),default=None) if i>=20 else None
            row["breakout_reentry_20__v1"]=1.0 if recent_failed and current_prior20 is not None and close is not None and close>current_prior20 else 0.0
            z=row["price_zscore_20__v1"]; rsi=row["rsi_14__v1"]; loc=row["close_location__v1"]
            row["exhaustion_score__v1"]=None if z is None or rsi is None or loc is None else z + (rsi-50.0)/25.0 + (loc-0.5)*2.0
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
        _percentile_assign(date_rows, "return_252_skip_20__v1", "return_252_skip_20_percentile__v1")
        _percentile_assign(date_rows, "return_126__v1", "return_126_percentile__v1")
        _percentile_assign(date_rows, "relative_volume_20__v1", "relative_volume_20_percentile__v1")
        _percentile_assign(date_rows, "natr_20__v1", "natr_20_percentile__v1")
        _percentile_assign(date_rows, "realized_vol_20__v1", "realized_vol_20_percentile__v1")
        _percentile_assign(date_rows, "return_252__v1", "sector_return_252_percentile__v1", group_column="sector_id")
        eligible = [row for row in date_rows if row.get("eligible", True)]
        breadth_sma = [row for row in eligible if row.get("close_to_sma_200__v1") is not None]
        breadth_ret = [row for row in eligible if row.get("return_20__v1") is not None]
        one_day = [row for row in eligible if row.get("return_1__v1") is not None]
        universe_ret63 = sorted(row["return_63__v1"] for row in eligible if row.get("return_63__v1") is not None)
        median_ret63 = statistics.median(universe_ret63) if universe_ret63 else None
        highlow = [row for row in eligible if row.get("range_position_252__v1") is not None]
        above = None if not breadth_sma else sum(row["close_to_sma_200__v1"] > 0 for row in breadth_sma) / len(breadth_sma)
        positive = None if not breadth_ret else sum(row["return_20__v1"] > 0 for row in breadth_ret) / len(breadth_ret)
        advdec = None if not one_day else (sum(row["return_1__v1"] > 0 for row in one_day)-sum(row["return_1__v1"] < 0 for row in one_day))/len(one_day)
        nhnl = None if not highlow else (sum(row["range_position_252__v1"] >= 1.0 for row in highlow)-sum(row["range_position_252__v1"] <= 0.0 for row in highlow))/len(highlow)
        for row in date_rows:
            row["breadth_above_sma_200__v1"] = above
            row["breadth_positive_20__v1"] = positive
            row["advance_decline_breadth__v1"] = advdec
            row["new_high_low_breadth_252__v1"] = nhnl
            row["sector_vs_universe_return_63__v1"] = None if median_ret63 is None or row.get("return_63__v1") is None else row["return_63__v1"]-median_ret63
    by_security_output: dict[str,list[dict[str,Any]]] = defaultdict(list)
    for row in output:
        by_security_output[row["security_id"]].append(row)
    for security_rows in by_security_output.values():
        security_rows.sort(key=lambda row: row["effective_date"])
        for i,row in enumerate(security_rows):
            current=row.get("return_126_percentile__v1")
            prior=security_rows[i-20].get("return_126_percentile__v1") if i>=20 else None
            row["relative_strength_change_20__v1"] = None if current is None or prior is None else current-prior
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
