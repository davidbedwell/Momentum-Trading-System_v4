from dataclasses import dataclass
from math import isfinite
from .progressive_scaling import ScaleEvidence

@dataclass(frozen=True)
class FoldRecord:
    family: str
    chromosome_id: str
    fold_id: str
    decision_session: int
    maturity_session: int
    net_return: float
    drawdown: float
    trades: int
    source: str
    independent: bool
    validation_start: int = -1
    validation_end: int = -1
    provenance_id: str = ''

class EvidenceBook:
    def __init__(self):
        self.records = []

    def add(self, record):
        if not isinstance(record, FoldRecord):
            raise TypeError('fold record required')
        if record.maturity_session <= record.decision_session or record.trades <= 0:
            raise ValueError('invalid fold chronology')
        if not isfinite(record.net_return) or not isfinite(record.drawdown) or not 0 <= record.drawdown <= 1:
            raise ValueError('invalid fold metrics')
        if record.source not in ('actual', 'shadow') or not all((record.family, record.chromosome_id, record.fold_id)):
            raise ValueError('invalid provenance')
        if any((r.family, r.chromosome_id, r.fold_id) == (record.family, record.chromosome_id, record.fold_id) for r in self.records):
            raise ValueError('duplicate fold')
        if record.independent:
            if record.validation_start < 0 or record.validation_end < record.validation_start:
                raise ValueError('independent fold requires validation boundaries')
            if record.validation_end >= record.maturity_session or not record.provenance_id:
                raise ValueError('independent fold requires causal provenance')
            for prior in self.records:
                if prior.family != record.family or prior.chromosome_id != record.chromosome_id:
                    continue
                if prior.provenance_id and prior.provenance_id == record.provenance_id:
                    raise ValueError('reused validation provenance')
                if prior.validation_start >= 0 and not (record.validation_end < prior.validation_start or prior.validation_end < record.validation_start):
                    raise ValueError('overlapping validation folds')
        self.records.append(record)

    def estimate(self, family, chromosome_id, asof_session, signal_confirmed=False, position_profitable=False):
        rows = [r for r in self.records if r.family == family and r.chromosome_id == chromosome_id and r.maturity_session < asof_session]
        if not rows:
            return None
        return ScaleEvidence(sum(r.trades for r in rows), len(rows), sum(r.net_return for r in rows) > 0,
                             max(r.drawdown for r in rows), bool(signal_confirmed), bool(position_profitable),
                             all(r.independent for r in rows))
