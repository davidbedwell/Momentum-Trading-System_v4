"""Incremental fill observer: replay ledger -> FIFO outcome ledger -> calibrator.
Caller supplies immutable owner/context for each BUY fill. No future outcomes.
"""
from position_outcome_ledger import PositionOutcomeLedger
from causal_calibration import Calibrator

class ReplayLearningAdapter:
    def __init__(self,min_samples=5):
        self.positions=PositionOutcomeLedger()
        self.calibrator=Calibrator(min_samples)
        self.cursor=0
    def consume(self,replay_ledger,session,ownership):
        """Consume only new fills. ownership maps ticker to (chromosome,context)
        as recorded at decision time; never infer ownership from future positions.
        """
        if self.cursor>len(replay_ledger):raise ValueError("ledger truncated")
        created=[]
        for row in replay_ledger[self.cursor:]:
            date,ticker,side,qty,price,fee=row
            if side=="BUY":
                if ticker not in ownership:raise ValueError("missing buy provenance")
                cid,context=ownership[ticker]
                self.positions.fill(session,ticker,side,qty,price,fee,cid,context)
            else:
                created.extend(self.positions.fill(session,ticker,side,qty,price,fee))
        self.cursor=len(replay_ledger)
        for outcome in created:self.calibrator.record(outcome)
        return created
