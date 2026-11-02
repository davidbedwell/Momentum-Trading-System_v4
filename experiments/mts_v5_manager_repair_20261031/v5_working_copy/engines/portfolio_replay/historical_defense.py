"""Load frozen historical A_v2/B/B1/C/R-1 state tape causally.

The tape is historical evidence, not a live detector. Dates are signal-close
dates; the resulting defense state applies only on the next trading session.
"""
import csv
from datetime import date
from pathlib import Path
from .defense_router import DefenseDecision,DefenseRouter

DEFAULT_TAPE=Path("/opt/mts/ga6/data/crash_defense_A_v2/STATE_TAPE_HISTORICAL.csv")
def _flag(row,key):
    v=row[key]
    if v not in ("True","False"):raise ValueError("invalid flag "+key)
    return v=="True"

def load_tape(path=DEFAULT_TAPE):
    decisions=[]
    with open(path,newline="") as f:
        rows=list(csv.DictReader(f))
    last=None
    for i,row in enumerate(rows):
        d=date.fromisoformat(row["date"])
        if last is not None and d<=last:raise ValueError("unordered tape")
        last=d
        triggers=tuple(k for k,col in (("A_v2","A_v2"),("B","B"),("B1","B1"),("C","C")) if _flag(row,col))
        defensive=_flag(row,"defensive")
        entry=_flag(row,"entry");exit_=_flag(row,"exit")
        if entry and (not defensive or not triggers):raise ValueError("inconsistent entry")
        if exit_ and (defensive or triggers):raise ValueError("inconsistent recovery")
        if i+1<len(rows):
            # Effective next *recorded trading session*, never the same day.
            effective=rows[i+1]["date"]
            decisions.append(DefenseDecision(row["date"],effective,defensive,triggers,
                                              recovery_authorized=exit_))
    return decisions

class HistoricalDefense:
    def __init__(self,path=DEFAULT_TAPE):
        self.decisions=load_tape(path)
        self.router=DefenseRouter()
        self.index=0
    def state(self,session):
        while self.index<len(self.decisions) and self.decisions[self.index].effective_at<=session:
            d=self.decisions[self.index]
            self.router.apply(session,d)
            self.index+=1
        return self.router.defensive
