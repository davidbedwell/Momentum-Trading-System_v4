from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable
import importlib.util
import math
import numpy as np
import pandas as pd

MAX_HORIZON = 63
REFERENCE_NOTIONAL = 100_000.0
SPREAD_FLOOR_BPS = 2.0
SPREAD_CAP_BPS = 50.0
IMPACT_COEFFICIENT_BPS = 10.0
SHORT_BORROW_BASELINE_ANNUAL = 0.003

_COST_SOURCE = Path(__file__).resolve().parents[2] / "Reconstruction/Certified-Stage2-Source-20261007/Core/conforming_ga/costs.py"
_spec = importlib.util.spec_from_file_location("mts_stage2_frozen_costs", _COST_SOURCE)
_frozen_costs = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_frozen_costs)


@dataclass(frozen=True)
class ExecutionPaths:
    """Outcome-only matrices aligned to decision rows.

    `endpoint_return[:, h-1]` is adjusted-open T+1 to adjusted-open T+1+h.
    `low_excursion` and `high_excursion` are running gross excursions while the
    hypothetical position is open, using adjusted intraday lows/highs.
    """
    endpoint_return: np.ndarray
    low_excursion: np.ndarray
    high_excursion: np.ndarray
    calendar_days: np.ndarray


@dataclass(frozen=True)
class ProspectiveCosts:
    long_roundtrip: np.ndarray
    short_roundtrip: np.ndarray
    spread_bps: np.ndarray
    impact_bps: np.ndarray
    adv_dollars: np.ndarray
    regulatory_sell_fraction: np.ndarray


def _require_columns(frame: pd.DataFrame, cols: Iterable[str]) -> None:
    missing = sorted(set(cols) - set(frame.columns))
    if missing:
        raise ValueError(f"missing required columns: {missing}")


def _adjusted_ohlc(group: pd.DataFrame) -> tuple[np.ndarray,np.ndarray,np.ndarray,np.ndarray]:
    close = group["close"].to_numpy(float)
    adj = group["adj_close"].to_numpy(float)
    factor = np.divide(adj, close, out=np.full_like(adj, np.nan), where=np.isfinite(close) & (close != 0))
    return (
        group["open"].to_numpy(float) * factor,
        group["high"].to_numpy(float) * factor,
        group["low"].to_numpy(float) * factor,
        factor,
    )


def build_execution_paths(raw: pd.DataFrame, *, max_horizon: int = MAX_HORIZON) -> ExecutionPaths:
    """Build all integer-horizon executable outcome paths without look-ahead in predictors.

    Input row order is preserved. Each row is a close-T decision observation.
    Hypothetical execution enters at T+1 open and exits at T+1+h open.
    """
    _require_columns(raw, ("security_id","date","open","high","low","close","adj_close"))
    if max_horizon < 1:
        raise ValueError("max_horizon must be >=1")
    n = len(raw)
    endpoint = np.full((n,max_horizon), np.nan, dtype=np.float32)
    low_exc = np.full_like(endpoint, np.nan)
    high_exc = np.full_like(endpoint, np.nan)
    cal_days = np.zeros((n,max_horizon), dtype=np.int16)

    # Keep caller row alignment while sorting within each security for temporal operations.
    work = raw.reset_index(drop=False).rename(columns={"index":"__row"})
    for _, g0 in work.groupby("security_id", sort=False):
        g = g0.sort_values("date")
        rows = g["__row"].to_numpy(int)
        dates = pd.to_datetime(g["date"]).to_numpy(dtype="datetime64[D]")
        aopen, ahigh, alow, _ = _adjusted_ohlc(g)
        L = len(g)
        if L < 3:
            continue
        # For decision d, entry is e=d+1. Intraday path offsets k=0..h-1;
        # exit open is e+h. Build cumulative excursions incrementally.
        running_low = np.full(L, np.inf, dtype=float)
        running_high = np.full(L, -np.inf, dtype=float)
        valid_entry = np.isfinite(aopen[1:]) & (aopen[1:] > 0)
        entry = aopen[1:]
        decision_count = L - 1
        for h in range(1, max_horizon + 1):
            k = h - 1
            # Update excursion with session e+k == d+1+k.
            future_idx = np.arange(1, L) + k
            usable = future_idx < L
            if not np.any(usable):
                break
            uix = np.flatnonzero(usable)
            fi = future_idx[usable]
            lo_ret = np.divide(alow[fi], entry[usable], out=np.full(len(fi), np.nan), where=valid_entry[usable]) - 1.0
            hi_ret = np.divide(ahigh[fi], entry[usable], out=np.full(len(fi), np.nan), where=valid_entry[usable]) - 1.0
            # running arrays indexed by decision-local position 0..L-2
            rl = running_low[:decision_count]
            rh = running_high[:decision_count]
            good_lo = np.isfinite(lo_ret)
            good_hi = np.isfinite(hi_ret)
            rl[uix[good_lo]] = np.minimum(rl[uix[good_lo]], lo_ret[good_lo])
            rh[uix[good_hi]] = np.maximum(rh[uix[good_hi]], hi_ret[good_hi])

            exit_idx = np.arange(1, L) + h
            valid = exit_idx < L
            if not np.any(valid):
                continue
            di = np.flatnonzero(valid)
            ex = exit_idx[valid]
            ok = valid_entry[valid] & np.isfinite(aopen[ex]) & (aopen[ex] > 0)
            if not np.any(ok):
                continue
            dloc = di[ok]
            global_rows = rows[dloc]
            r = aopen[ex[ok]] / entry[valid][ok] - 1.0
            endpoint[global_rows,h-1] = r.astype(np.float32)
            low_exc[global_rows,h-1] = rl[dloc].astype(np.float32)
            high_exc[global_rows,h-1] = rh[dloc].astype(np.float32)
            days = (dates[ex[ok]] - dates[dloc + 1]).astype("timedelta64[D]").astype(int)
            cal_days[global_rows,h-1] = np.maximum(days,1).astype(np.int16)
    return ExecutionPaths(endpoint, low_exc, high_exc, cal_days)


def _effective_rate_by_date(table, dates: pd.Series) -> np.ndarray:
    # table rows are sorted effective-date tuples; return numeric second field.
    d = pd.to_datetime(dates).dt.date.to_numpy()
    out = np.empty(len(d), dtype=float)
    for i, when in enumerate(d):
        out[i] = _frozen_costs._effective(table, when)[1]
    return out


def build_prospective_costs(raw: pd.DataFrame, paths: ExecutionPaths, *,
                            reference_notional: float = REFERENCE_NOTIONAL,
                            spread_floor_bps: float = SPREAD_FLOOR_BPS,
                            spread_cap_bps: float = SPREAD_CAP_BPS,
                            impact_coefficient_bps: float = IMPACT_COEFFICIENT_BPS,
                            short_borrow_annual: float = SHORT_BORROW_BASELINE_ANNUAL) -> ProspectiveCosts:
    """Build the frozen causal prospective cost model aligned to decision rows.

    HLC and trailing-20 ADV are known at close T. Execution date/price is T+1 open.
    The same prospective spread/impact estimate is applied to both hypothetical
    legs, matching the registered simulator's lifecycle hurdle semantics.
    """
    _require_columns(raw, ("security_id","date","open","high","low","close","volume"))
    if reference_notional <= 0:
        raise ValueError("reference_notional must be positive")
    n = len(raw); H = paths.endpoint_return.shape[1]
    adv = np.full(n, np.nan, dtype=float)
    next_open = np.full(n, np.nan, dtype=float)
    next_date = pd.Series([pd.NaT]*n, dtype="datetime64[ns]")
    work = raw.reset_index(drop=False).rename(columns={"index":"__row"})
    for _, g0 in work.groupby("security_id", sort=False):
        g = g0.sort_values("date"); rows=g["__row"].to_numpy(int)
        dv = g["close"].to_numpy(float) * g["volume"].to_numpy(float)
        adv[rows] = pd.Series(dv).rolling(20,min_periods=20).mean().to_numpy()
        op = g["open"].to_numpy(float); dt = pd.to_datetime(g["date"]).to_numpy()
        if len(rows)>1:
            next_open[rows[:-1]] = op[1:]
            next_date.iloc[rows[:-1]] = dt[1:]
    high=raw["high"].to_numpy(float);low=raw["low"].to_numpy(float);close=raw["close"].to_numpy(float)
    spread = 10000.0*(high-low)/close/2.0
    spread = np.clip(spread, spread_floor_bps, spread_cap_bps)
    spread[~(np.isfinite(high)&np.isfinite(low)&np.isfinite(close)&(close>0)&(high>=low))]=np.nan
    valid_adv = np.isfinite(adv) & (adv > 0)
    impact = np.full(n, np.nan, dtype=float)
    impact[valid_adv] = impact_coefficient_bps * np.sqrt(reference_notional / adv[valid_adv])

    # Regulatory sell fraction on the prospective T+1 execution date.
    reg = np.full(n,np.nan,dtype=float)
    valid_date = next_date.notna().to_numpy(); valid_px=np.isfinite(next_open)&(next_open>0)
    for i in np.flatnonzero(valid_date & valid_px):
        when = next_date.iloc[i].date(); px=float(next_open[i]); shares=reference_notional/px
        # Rate history starts 2005-12-22; never infer a pre-schedule SEC rate.
        # Mark these observations ineligible by preserving their NaN costs.
        if when < _frozen_costs._d(_frozen_costs.SEC31[0][0]):
            continue
        reg[i] = _frozen_costs.regulatory_sell_fee(when,reference_notional,shares,px)/reference_notional
    base = 2.0*(spread+impact)/10000.0 + reg
    long_cost = np.repeat(base[:,None],H,axis=1).astype(np.float32)
    borrow = short_borrow_annual * paths.calendar_days.astype(float)/365.0
    short_cost = (base[:,None] + borrow).astype(np.float32)
    invalid = ~np.isfinite(paths.endpoint_return)
    long_cost[invalid]=np.nan; short_cost[invalid]=np.nan
    return ProspectiveCosts(long_cost,short_cost,spread.astype(np.float32),impact.astype(np.float32),adv,reg.astype(np.float32))


def signed_excursions(paths: ExecutionPaths, side: str) -> tuple[np.ndarray,np.ndarray]:
    side=side.upper()
    if side=="LONG":
        return paths.low_excursion, paths.high_excursion
    if side=="SHORT":
        # Short loses on high excursions and gains on low excursions.
        return -paths.high_excursion, -paths.low_excursion
    raise ValueError("side must be LONG or SHORT")
