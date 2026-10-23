"""Shared-account chromosome ownership and strict decision-time admission.

This component is an execution integration primitive, not a portfolio replay.
A selected chromosome owns a position until the last share is sold; ranking
updates cannot silently swap its scale or exit genome.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Selection:
    chromosome: str
    decision_date: str
    evidence_cutoff: str

class PositionOwners:
    def __init__(self):
        self._owners={}
        self._shares={}

    def choose_entry(self, *, symbol, decision_date, candidates, scores):
        if symbol in self._owners:
            raise ValueError("position already has a chromosome owner")
        eligible=[]
        for candidate in candidates:
            if candidate["symbol"]!=symbol: continue
            if candidate["decision_date"]!=decision_date:
                raise ValueError("decision date mismatch")
            if candidate["evidence_cutoff"]>decision_date:
                raise ValueError("future candidate evidence")
            chromosome=str(candidate["chromosome"])
            if chromosome in scores:
                eligible.append((float(scores[chromosome]),chromosome,candidate))
        if not eligible:
            return None
        # Stable deterministic tie-breaking; never infer unavailable scores.
        return max(eligible,key=lambda x:(x[0],x[1]))[2]

    def record_fill(self, *, symbol, side, quantity, chromosome=None):
        if not isinstance(quantity,int) or quantity<=0:
            raise ValueError("invalid fill quantity")
        if side=="BUY":
            if symbol not in self._owners:
                if chromosome is None: raise ValueError("entry missing owner")
                self._owners[symbol]=str(chromosome)
                self._shares[symbol]=0
            elif chromosome is not None and str(chromosome)!=self._owners[symbol]:
                raise ValueError("cannot scale in using different chromosome")
            self._shares[symbol]+=quantity
        elif side=="SELL":
            if symbol not in self._owners or quantity>self._shares[symbol]:
                raise ValueError("sell exceeds owned inventory")
            self._shares[symbol]-=quantity
            if self._shares[symbol]==0:
                del self._owners[symbol]
                del self._shares[symbol]
        else:
            raise ValueError("invalid fill side")

    def owner(self,symbol):
        return self._owners.get(symbol)

    def inventory(self):
        return dict(self._shares)

    def reconcile(self,holdings):
        expected={k:int(v) for k,v in holdings.items() if v}
        if expected!=self._shares:
            raise ValueError("shared ledger and chromosome ownership diverged")
