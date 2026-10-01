from __future__ import annotations

from dataclasses import dataclass
import math
import statistics
from typing import Any, Mapping, Sequence


class TradePathError(RuntimeError):
    pass


def _finite(value: Any) -> float | None:
    try:
        x=float(value)
    except (TypeError,ValueError):
        return None
    return x if math.isfinite(x) else None


@dataclass(frozen=True, slots=True)
class TradePath:
    signal_date: str
    entry_date: str
    exit_date: str
    entry_price: float
    exit_price: float
    horizon_sessions: int
    fixed_horizon_return: float
    mae_return: float
    mfe_return: float
    stop_results: Mapping[str, Mapping[str, Any]]


def simulate_long_path(*, bars: Sequence[Mapping[str, Any]], signal_index: int, horizon_sessions: int, stop_fractions: Sequence[float]) -> TradePath:
    """Execute after a completed signal bar: next-session open entry, horizon-session close exit.

    Daily bars cannot establish intraday ordering between high and low. A long stop
    is therefore evaluated only from the stop itself: a gap through the stop fills
    at the next observed open; otherwise a low touching the stop fills at the stop.
    No profit target is mixed into the same bar, so no stop/target ordering is invented.
    """
    if horizon_sessions < 1:
        raise TradePathError("horizon_sessions must be >= 1")
    entry_i=signal_index+1
    exit_i=signal_index+horizon_sessions
    if signal_index < 0 or exit_i >= len(bars):
        raise TradePathError("insufficient future bars for requested trade path")
    entry=_finite(bars[entry_i].get("open"))
    exit_price=_finite(bars[exit_i].get("close"))
    if entry is None or entry <= 0 or exit_price is None:
        raise TradePathError("missing/nonpositive entry open or missing exit close")
    path=bars[entry_i:exit_i+1]
    lows=[_finite(b.get("low")) for b in path]
    highs=[_finite(b.get("high")) for b in path]
    if any(x is None for x in lows+highs):
        raise TradePathError("missing high/low inside trade path")
    mae=min(x/entry-1.0 for x in lows if x is not None)
    mfe=max(x/entry-1.0 for x in highs if x is not None)
    stops={}
    for fraction in stop_fractions:
        fraction=float(fraction)
        if not 0.0 < fraction < 1.0:
            raise TradePathError("stop fractions must be between 0 and 1")
        stop_price=entry*(1.0-fraction)
        stopped=False; fill=None; fill_date=None
        for bar in path:
            op=_finite(bar.get("open")); lo=_finite(bar.get("low"))
            if op is None or lo is None:
                raise TradePathError("missing open/low inside stop path")
            if op <= stop_price:
                stopped=True; fill=op; fill_date=str(bar["date"]); break
            if lo <= stop_price:
                stopped=True; fill=stop_price; fill_date=str(bar["date"]); break
        realized=(fill/entry-1.0) if stopped else (exit_price/entry-1.0)
        stops[f"{fraction:.6f}"]={
            "stop_fraction":fraction,"stopped":stopped,"fill_price":fill,
            "fill_date":fill_date,"realized_return":realized,
            "r_multiple":realized/fraction,
        }
    return TradePath(
        signal_date=str(bars[signal_index]["date"]),entry_date=str(bars[entry_i]["date"]),
        exit_date=str(bars[exit_i]["date"]),entry_price=entry,exit_price=exit_price,
        horizon_sessions=horizon_sessions,fixed_horizon_return=exit_price/entry-1.0,
        mae_return=mae,mfe_return=mfe,stop_results=stops,
    )


def summarize_paths(paths: Sequence[TradePath]) -> Mapping[str, Any]:
    def stats(values):
        vals=list(values); n=len(vals)
        return {
            "count":n,
            "mean":statistics.fmean(vals) if vals else None,
            "median":statistics.median(vals) if vals else None,
            "positive_fraction":None if not vals else sum(v>0 for v in vals)/n,
        }
    result={
        "trade_count":len(paths),
        "fixed_horizon_return":stats(p.fixed_horizon_return for p in paths),
        "mae_return":stats(p.mae_return for p in paths),
        "mfe_return":stats(p.mfe_return for p in paths),
        "stop_scenarios":{},
    }
    keys=sorted({k for p in paths for k in p.stop_results})
    for key in keys:
        rows=[p.stop_results[key] for p in paths]
        result["stop_scenarios"][key]={
            "stop_fraction":rows[0]["stop_fraction"],
            "stopped_count":sum(bool(r["stopped"]) for r in rows),
            "stop_rate":sum(bool(r["stopped"]) for r in rows)/len(rows) if rows else None,
            "realized_return":stats(float(r["realized_return"]) for r in rows),
            "r_multiple":stats(float(r["r_multiple"]) for r in rows),
            "gross_ev_r":statistics.fmean(float(r["r_multiple"]) for r in rows) if rows else None,
            "net_ev_r":"UNAVAILABLE_REQUIRES_ESTIMATED_ALL_IN_COST_INPUT",
        }
    return result
