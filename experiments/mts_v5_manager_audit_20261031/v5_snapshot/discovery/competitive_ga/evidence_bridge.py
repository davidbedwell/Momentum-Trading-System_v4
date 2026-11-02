"""Chronological evidence promotion for progressive portfolio scaling.

Only matured, previously recorded trade outcomes may qualify a chromosome.
Research gate; independent validation must be supplied explicitly.
"""
from dataclasses import dataclass
from datetime import date
from math import isfinite
from .progressive_scaling import ScaleEvidence

@dataclass(frozen=True)
class MaturedTrade:
    chromosome_id: str
    decision_date: str
    matured_at: str
    net_return: float
    fold: str

@dataclass(frozen=True)
class DatedDrawdown:
    value: float
    measured_through: str
    chromosome_id: str
    source_hash: str

@dataclass(frozen=True)
class EvidenceSnapshot:
    chromosome_id: str
    as_of: str
    matured_trades: int
    forward_folds: int
    net_ev: float
    historical_mdd: float
    independently_confirmed: bool
    evidence_cutoff: str

def build_snapshot(chromosome_id,as_of,trades,*,historical_mdd,independently_confirmed):
    today=date.fromisoformat(as_of)
    if not isfinite(historical_mdd) or not 0<=historical_mdd<=1:raise ValueError("invalid drawdown")
    eligible=[]
    for t in trades:
        if t.chromosome_id!=chromosome_id:continue
        if not isfinite(t.net_return):raise ValueError("nonfinite outcome")
        decision=date.fromisoformat(t.decision_date)
        matured=date.fromisoformat(t.matured_at)
        if decision>matured:raise ValueError("outcome before decision")
        if matured<today:eligible.append(t)
    if not eligible:raise ValueError("no historical matured evidence")
    return EvidenceSnapshot(chromosome_id,as_of,len(eligible),
        len({t.fold for t in eligible}),sum(t.net_return for t in eligible)/len(eligible),
        historical_mdd,bool(independently_confirmed),max(t.matured_at for t in eligible))

def to_scale_evidence(snapshot,*,signal_confirmed,position_profitable):
    return ScaleEvidence(snapshot.matured_trades,snapshot.forward_folds,
        snapshot.net_ev>0,snapshot.historical_mdd,bool(signal_confirmed),
        bool(position_profitable),snapshot.independently_confirmed)
