"""Strict four-family native signal boundary for portfolio learning.

No conversion of EV fractions to R multiples, no synthetic substitute signals.
"""
from dataclasses import dataclass
from datetime import date
from math import isfinite

@dataclass(frozen=True)
class NativeProposal:
    decision_date: str
    ticker: str
    family: str
    chromosome_id: str
    action: str
    target_weight: float
    native_score: float
    native_score_unit: str
    source_manifest_hash: str
    feature_snapshot_hash: str
    model_trained_through: str

    def __post_init__(self):
        if self.family not in ("GA4","HORIZONS","GA6","GA7"):raise ValueError("unsupported chromosome family")
        if self.action not in ("ENTER","ADD","HOLD","REDUCE","EXIT"):raise ValueError("invalid action")
        if not self.ticker or not self.chromosome_id or not self.source_manifest_hash or not self.feature_snapshot_hash:
            raise ValueError("missing signal provenance")
        if self.native_score_unit not in {"GA4":("native_horizon_score",),"HORIZONS":("native_horizon_score",),"GA6":("entry_equity_fraction",),"GA7":("r_multiple","net_return_fraction")}[self.family]:
            raise ValueError("native score unit mismatch")
        limit=1. if self.action in ('HOLD','REDUCE') else .30
        if not isfinite(self.native_score) or not isfinite(self.target_weight) or not 0<=self.target_weight<=limit:
            raise ValueError("invalid signal values")
        if self.action=="EXIT" and self.target_weight!=0:raise ValueError("exit must target zero")
        if date.fromisoformat(self.model_trained_through)>date.fromisoformat(self.decision_date):
            raise ValueError("future-trained signal model")

def normalize_proposals(proposals,as_of):
    """Validate chronology and provenance. Preserve family-native score units."""
    result=[]
    for p in proposals:
        if not isinstance(p,NativeProposal):raise TypeError("native proposal required")
        if p.decision_date!=as_of:raise ValueError("stale or future signal")
        result.append(p)
    return tuple(result)
