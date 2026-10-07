from __future__ import annotations

import math
import statistics
from typing import Any, Mapping, Sequence


def _stats(values: Sequence[float]) -> Mapping[str, Any]:
    vals=[float(v) for v in values if math.isfinite(float(v))]
    return {
        "count":len(vals),
        "mean":statistics.fmean(vals) if vals else None,
        "median":statistics.median(vals) if vals else None,
        "positive_fraction":sum(v > 0 for v in vals)/len(vals) if vals else None,
        "min":min(vals) if vals else None,
        "max":max(vals) if vals else None,
    }


def _trimmed_mean(values: Sequence[float]) -> float | None:
    vals=sorted(float(v) for v in values)
    if not vals:
        return None
    trim=max(1, math.floor(len(vals)*0.10)) if len(vals) >= 10 else 0
    kept=vals[trim:len(vals)-trim] if trim and len(vals) > 2*trim else vals
    return statistics.fmean(kept)


def _winner_concentration(values: Sequence[float]) -> Mapping[str, Any]:
    vals=[float(v) for v in values]
    positive_total=sum(v for v in vals if v > 0)
    ranked=sorted((v for v in vals if v > 0), reverse=True)
    out={"positive_return_sum":positive_total}
    for n in (1,2,3):
        top=sum(ranked[:n])
        out[f"top_{n}_positive_return_sum"]=top
        out[f"top_{n}_share_of_positive_returns"]=top/positive_total if positive_total > 0 else None
    return out


def _leave_one_out(values: Sequence[float]) -> Mapping[str, Any]:
    vals=[float(v) for v in values]
    if len(vals) < 2:
        return {"available":False,"reason":"REQUIRES_AT_LEAST_TWO_TRADES"}
    means=[statistics.fmean(vals[:i]+vals[i+1:]) for i in range(len(vals))]
    return {"available":True,"mean_min":min(means),"mean_max":max(means),"means":means}


def _chronological_segments(paths: Sequence[Mapping[str, Any]], segments: int=3) -> list[Mapping[str, Any]]:
    ordered=sorted(paths,key=lambda p:str(p["entry_date"]))
    n=len(ordered)
    if not n:
        return []
    result=[]
    for j in range(segments):
        lo=(j*n)//segments; hi=((j+1)*n)//segments
        rows=ordered[lo:hi]
        vals=[float(p["fixed_horizon_return"]) for p in rows]
        result.append({
            "segment":j+1,
            "start_entry_date":rows[0]["entry_date"] if rows else None,
            "end_entry_date":rows[-1]["entry_date"] if rows else None,
            "statistics":_stats(vals),
        })
    return result


def analyze_frozen_candidate(candidate: Mapping[str, Any]) -> Mapping[str, Any]:
    paths=list(candidate.get("paths",()))
    vals=[float(p["fixed_horizon_return"]) for p in paths]
    return {
        "candidate_id":candidate.get("candidate_id"),
        "family_id":candidate.get("family_id"),
        "genome":candidate.get("genome"),
        "trade_count":len(paths),
        "chronological_trades":[{
            "signal_date":p["signal_date"],"entry_date":p["entry_date"],"exit_date":p["exit_date"],
            "fixed_horizon_return":p["fixed_horizon_return"],"mae_return":p["mae_return"],
            "mfe_return":p["mfe_return"],"stop_results":p.get("stop_results",{}),
        } for p in sorted(paths,key=lambda x:str(x["entry_date"]))],
        "fixed_horizon_statistics":_stats(vals),
        "trimmed_mean":_trimmed_mean(vals),
        "winner_concentration":_winner_concentration(vals),
        "leave_one_out":_leave_one_out(vals),
        "chronological_thirds":_chronological_segments(paths,3),
        "mae_statistics":_stats([float(p["mae_return"]) for p in paths]),
        "mfe_statistics":_stats([float(p["mfe_return"]) for p in paths]),
    }


def pairwise_candidate_overlap(candidates: Mapping[str, Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    keys=list(candidates)
    rows=[]
    for i,a in enumerate(keys):
        da={str(p["entry_date"]) for p in candidates[a].get("paths",())}
        for b in keys[i+1:]:
            db={str(p["entry_date"]) for p in candidates[b].get("paths",())}
            inter=da & db; union=da | db
            rows.append({
                "candidate_a":a,"candidate_b":b,
                "same_entry_date_count":len(inter),
                "jaccard_same_entry_dates":len(inter)/len(union) if union else None,
                "share_of_smaller_candidate":len(inter)/min(len(da),len(db)) if da and db else None,
                "same_entry_dates":sorted(inter),
            })
    return rows
