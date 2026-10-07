from __future__ import annotations
from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class NullGateMetrics:
    final_median_gap: float
    mean_median_gap: float
    real_wins_generations: int
    generations: int
    real_win_fraction: float
    final_best_gap: float
    matched_budget: bool
    finite: bool

def summarize_matched_pilot(payload: dict) -> NullGateMetrics:
    arms={a["arm"]:a for a in payload["arms"]}
    real=arms["real"]
    null=arms["matched_temporal_block_null"]
    rg=real["ledger"]
    ng=null["ledger"]
    if len(rg)!=len(ng):
        raise ValueError("real/null generation counts differ")
    rmed=np.array([x["median_mean"] for x in rg],float)
    nmed=np.array([x["median_mean"] for x in ng],float)
    rbest=np.array([x["best"]["mean"] for x in rg],float)
    nbest=np.array([x["best"]["mean"] for x in ng],float)
    vals=np.concatenate([rmed,nmed,rbest,nbest])
    matched=(real["ticker_evaluations"]==null["ticker_evaluations"] and bool(payload.get("matched_budget")))
    wins=int(np.sum(rmed>nmed))
    n=len(rg)
    return NullGateMetrics(
        final_median_gap=float(rmed[-1]-nmed[-1]),
        mean_median_gap=float(np.mean(rmed-nmed)),
        real_wins_generations=wins,
        generations=n,
        real_win_fraction=float(wins/n if n else 0.0),
        final_best_gap=float(rbest[-1]-nbest[-1]),
        matched_budget=matched,
        finite=bool(np.isfinite(vals).all()),
    )

def authorization_state(metrics: NullGateMetrics) -> str:
    # Deliberately no numeric pass threshold here. Thresholds require explicit freeze/approval.
    if not metrics.matched_budget or not metrics.finite:
        return "INVALID_PILOT"
    return "THRESHOLD_NOT_FROZEN_NO_PRODUCTION_AUTHORIZATION"
