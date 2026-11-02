"""Reconstruct completed validation folds at their maturity session.
The supplied trade stream must originate from an independently audited ledger.
"""
from dataclasses import dataclass
from .fold_trade_reconstruction import reconstruct

@dataclass(frozen=True)
class FoldBatch:
    family: str
    chromosome_id: str
    fold_id: str
    validation_start: int
    validation_end: int
    maturity_session: int
    provenance_id: str
    trades: tuple

def schedule(batches):
    result={}
    for b in batches:
        if not isinstance(b,FoldBatch):raise TypeError('fold batch required')
        record=reconstruct(b.family,b.chromosome_id,b.fold_id,b.validation_start,
                           b.validation_end,b.maturity_session,b.trades,b.provenance_id)
        result.setdefault(b.maturity_session,[]).append(record)
    return result
