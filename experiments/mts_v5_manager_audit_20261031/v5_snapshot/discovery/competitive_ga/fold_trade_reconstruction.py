"""Construct fold metrics from dated, matured, net trade outcomes.
Trade-level compounding is a diagnostic proxy, not portfolio NAV drawdown.
"""
from dataclasses import dataclass
from math import isfinite, prod
from .causal_scaling_evidence import FoldRecord

@dataclass(frozen=True)
class FoldTrade:
    trade_id: str
    entry_session: int
    exit_session: int
    net_return: float
    source: str

def reconstruct(family, chromosome_id, fold_id, validation_start, validation_end,
                maturity_session, trades, provenance_id):
    trades=tuple(trades)
    if not trades or not provenance_id or not fold_id:
        raise ValueError('fold requires trade data and provenance')
    if validation_start<0 or validation_end<validation_start or maturity_session<=validation_end:
        raise ValueError('invalid fold chronology')
    if len({t.trade_id for t in trades})!=len(trades):
        raise ValueError('duplicate trade IDs')
    for t in trades:
        if not t.trade_id or t.source not in ('actual','shadow'):
            raise ValueError('invalid trade provenance')
        if not validation_start<=t.entry_session<t.exit_session<=validation_end:
            raise ValueError('trade outside fold or not matured')
        if not isfinite(t.net_return) or t.net_return<=-1:
            raise ValueError('invalid net return')
    sources={t.source for t in trades}
    if len(sources)!=1:raise ValueError('mixed trade sources')
    equity=peak=1.
    worst=0.
    for t in sorted(trades,key=lambda x:(x.exit_session,x.trade_id)):
        equity*=1+t.net_return
        peak=max(peak,equity)
        worst=max(worst,1-equity/peak)
    return FoldRecord(family,chromosome_id,fold_id,validation_start,maturity_session,
                      equity-1,worst,len(trades),sources.pop(),True,
                      validation_start,validation_end,provenance_id)
