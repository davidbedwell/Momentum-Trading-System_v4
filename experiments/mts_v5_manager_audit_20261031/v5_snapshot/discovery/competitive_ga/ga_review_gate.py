"""Causal GA review trigger and champion/challenger promotion gate.
No trading orders, evolution launch, or automatic promotion occur here.
"""
from dataclasses import dataclass
from datetime import datetime
from math import isfinite
from zoneinfo import ZoneInfo

NY=ZoneInfo('America/New_York')

@dataclass(frozen=True)
class ReviewDecision:
    review: bool
    reason: str
    evolve: bool


def review_due(now, dramatic_regime_change=False, drift_confirmed=False):
    """Only caller-verified as-of-time regime and drift flags are accepted.
    Friday 18:00 New York or later is the scheduled review window.
    Scheduler must deduplicate repeated calls using an external review ledger.
    """
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError('timezone-aware datetime required')
    local=now.astimezone(NY)
    friday=local.weekday()==4 and local.hour>=18
    if dramatic_regime_change:
        return ReviewDecision(True,'DRAMATIC_REGIME_CHANGE',bool(drift_confirmed))
    if friday:
        return ReviewDecision(True,'FRIDAY_POST_CLOSE',bool(drift_confirmed))
    return ReviewDecision(False,'NONE',False)

@dataclass(frozen=True)
class ValidationEvidence:
    champion_net_return: float
    challenger_net_return: float
    champion_mdd: float
    challenger_mdd: float
    independent_chronological: bool
    sealed_holdout_untouched: bool
    calibrated: bool
    costs_included: bool
    uncertainty_margin: float
    tail_risk_acceptable: bool


def eligible_for_promotion(e):
    """Fail closed: advisory gate only, never performs promotion."""
    vals=(e.champion_net_return,e.challenger_net_return,e.champion_mdd,
          e.challenger_mdd,e.uncertainty_margin)
    if not all(isfinite(x) for x in vals) or e.uncertainty_margin<0:
        return False
    if not all((e.independent_chronological,e.sealed_holdout_untouched,
                e.calibrated,e.costs_included,e.tail_risk_acceptable)):
        return False
    if e.challenger_mdd>e.champion_mdd or e.challenger_mdd>0.20:
        return False
    return e.challenger_net_return>e.champion_net_return+e.uncertainty_margin
