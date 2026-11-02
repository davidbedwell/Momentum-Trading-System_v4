"""Chronological chromosome calibration from matured realized/shadow trades.
Conservative research estimates, not deployment-certified forecasts.
"""
from dataclasses import dataclass
from math import sqrt,isfinite
from collections import defaultdict

@dataclass(frozen=True)
class TradeOutcome:
    chromosome_id:str
    context:tuple
    decision_session:int
    maturity_session:int
    net_r:float
    source:str
    ticker:str|None=None
    family:str|None=None
    genome_hash:str|None=None

class Calibrator:
    def __init__(self,min_samples=5):
        self.outcomes=[]
        self.min_samples=min_samples
    def record(self,outcome):
        if outcome.maturity_session<=outcome.decision_session:
            raise ValueError("outcome must mature after decision")
        if not isfinite(outcome.net_r):raise ValueError("nonfinite return")
        if outcome.source not in ("actual","shadow"):raise ValueError("unverified source")
        self.outcomes.append(outcome)
    def estimate(self,chromosome_id,context,asof_session):
        # Strictly prior matured outcomes; context dimensions must match.
        rows=[o.net_r for o in self.outcomes
              if o.chromosome_id==chromosome_id
              and o.maturity_session<asof_session
              and o.context==tuple(context)]
        if len(rows)<self.min_samples:return None
        n=len(rows)
        mean=sum(rows)/n
        downside=sqrt(sum(min(0.,r)**2 for r in rows)/n)
        return {"edge":mean,"downside":downside,
                "confidence":min(.95,n/(n+10)),
                "matured_samples":n,"asof_session":asof_session}
