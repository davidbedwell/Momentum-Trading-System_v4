"""Non-selecting Stage 2 evidence annotation; regime attribution belongs downstream.

This function never ranks, rejects, promotes, or alters the evolutionary fitness.
"""
from __future__ import annotations
import math

def annotate_discovery(record):
    points=record["daily_horizon_evidence"]
    if [p["horizon"] for p in points] != list(range(1,64)):
        raise ValueError("Full 63-horizon record required")
    annotated=dict(record)
    annotated["discovery_evidence"]={
        "bank_status":"PROVISIONAL_UNTIL_INDEPENDENTLY_VALIDATED",
        "retention":"RETAIN_WITH_UNCERTAINTY",
        "fitness_unchanged":True,
        "regime_classification":"DEFER_TO_LATER_ANALYSIS",
        "crash_episode_validation":"DEFER_TO_STAGE_9",
        "correlation_scope":"security-year cluster SE; shared calendar shock dependence not established",
        "per_horizon":[{
            "horizon":p["horizon"],
            "raw_n":p.get("n"),
            "security_year_cluster_n":p.get("effective_n"),
            "lcb95":p.get("lcb95") if isinstance(p.get("lcb95"),(int,float)) and math.isfinite(p["lcb95"]) else None,
            "uncertainty_status":"ESTIMATED_NOT_MARKET_SHOCK_CERTIFIED" if isinstance(p.get("lcb95"),(int,float)) and math.isfinite(p["lcb95"]) else "INSUFFICIENT_EVIDENCE",
        } for p in points]
    }
    return annotated
