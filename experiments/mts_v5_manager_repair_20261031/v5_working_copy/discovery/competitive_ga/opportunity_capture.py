"""Causal funding-availability audit; missed future profits are not knowable at decision time.

Use realized outcomes only in subsequent training/analysis, never in same-day decisions.
"""
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class FundingDecision:
    session: str
    ticker: str
    owner: tuple
    requested_weight: float
    funded_weight: float
    settled_cash_weight: float
    sgov_weight: float
    reason: str

    def __post_init__(self):
        vals=(self.requested_weight,self.funded_weight,self.settled_cash_weight,self.sgov_weight)
        if any(not isfinite(v) or not 0<=v<=1 for v in vals):
            raise ValueError('funding weights must be finite fractions')
        if self.funded_weight>self.requested_weight:
            raise ValueError('funded amount exceeds requested amount')
        if not self.session or not self.ticker or not self.owner or not self.reason:
            raise ValueError('missing funding provenance')

    @property
    def missed_weight(self):
        return self.requested_weight-self.funded_weight


def summarize(rows):
    rows=tuple(rows)
    demand=sum(r.requested_weight for r in rows)
    funded=sum(r.funded_weight for r in rows)
    misses=[r for r in rows if r.missed_weight>1e-12]
    return {'requests':len(rows),'underfunded_requests':len(misses),
            'requested_weight_sum':demand,'funded_weight_sum':funded,
            'capture_fraction':funded/demand if demand else None,
            'missed_weight_sum':sum(r.missed_weight for r in rows),
            'reasons':{reason:sum(r.reason==reason for r in misses)
                       for reason in sorted({r.reason for r in misses})}}
