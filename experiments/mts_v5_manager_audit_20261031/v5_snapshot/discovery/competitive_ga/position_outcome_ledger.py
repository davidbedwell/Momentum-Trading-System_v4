"""Position accounting for causal manager learning.
FIFO cost basis, partial exits, scale-ins, and per-fill fees.
Realized partial exits mature at their sell session. Open lots are not scored.
"""
from collections import defaultdict,deque
from causal_calibration import TradeOutcome

class PositionOutcomeLedger:
    def __init__(self):
        self.lots=defaultdict(deque)
        self.outcomes=[]
    def fill(self,session,ticker,side,qty,price,fee,chromosome_id=None,context=None):
        if qty<=0 or price<=0 or fee<0:raise ValueError("invalid fill")
        if side=="BUY":
            if not chromosome_id or context is None:raise ValueError("owner/context required")
            self.lots[ticker].append([float(qty),float(price)+fee/qty,
                                     int(session),chromosome_id,tuple(context)])
            return []
        if side!="SELL":raise ValueError("invalid side")
        available=sum(lot[0] for lot in self.lots[ticker])
        if qty>available+1e-8:raise ValueError("oversell")
        remaining=float(qty)
        created=[]
        while remaining>1e-9:
            lot=self.lots[ticker][0]
            take=min(remaining,lot[0])
            cost=take*lot[1]
            net=take*price-fee*(take/qty)
            if session<=lot[2]:raise ValueError("nonpositive holding period")
            obs=TradeOutcome(lot[3],lot[4],lot[2],int(session),net/cost-1.,"actual")
            created.append(obs)
            lot[0]-=take
            remaining-=take
            if lot[0]<1e-9:self.lots[ticker].popleft()
        self.outcomes.extend(created)
        return created
