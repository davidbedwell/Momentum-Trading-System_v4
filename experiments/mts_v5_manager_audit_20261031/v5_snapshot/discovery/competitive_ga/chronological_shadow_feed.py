"""Chronological GA6 shadow outcome feed for manager calibration.
Uses native replay with immutable per-fill owner, processes each fill on its
actual execution session. Query returns only prior-session matured outcomes.
"""
import json
from collections import defaultdict
from discovery.competitive_ga.ga6_native_position_replay import run
from discovery.competitive_ga.position_outcome_ledger import PositionOutcomeLedger
from discovery.competitive_ga.causal_calibration import Calibrator

class ShadowFeed:
    def __init__(self,attributed_fills,min_samples=5):
        self.events=defaultdict(list)
        for item in attributed_fills:self.events[item["session"]].append(item)
        self.positions=PositionOutcomeLedger()
        self.calibrator=Calibrator(min_samples)
        self.last_session=-1
    def advance(self,session):
        if session<=self.last_session:raise ValueError("nonmonotonic session")
        matured=[]
        for i in range(self.last_session+1,session+1):
            for item in self.events.get(i,()):
                _,ticker,side,qty,price,fee=item["fill"]
                cid=item["chromosome_id"]
                if side=="BUY":
                    self.positions.fill(i,ticker,side,qty,price,fee,cid,("GA6_ENTRY",))
                else:
                    matured.extend(self.positions.fill(i,ticker,side,qty,price,fee))
        for outcome in matured:self.calibrator.record(outcome)
        self.last_session=session
        return matured
    def estimate(self,chromosome_id,session):
        if session!=self.last_session:raise ValueError("advance to session first")
        return self.calibrator.estimate(chromosome_id,("GA6_ENTRY",),session)

def audit():
    _,fills=run(output="ATTRIBUTED")
    feed=ShadowFeed(fills)
    first=None
    calibrated_first=None
    for i in range(253):
        new=feed.advance(i)
        if new and first is None:first=i
        for cid in {x["chromosome_id"] for x in fills}:
            if feed.estimate(cid,i) and calibrated_first is None:
                calibrated_first=i
    return {"native_fills":len(fills),"realized_outcomes":len(feed.calibrator.outcomes),
            "first_realized_session":first,"first_calibrated_session_min5":calibrated_first,
            "warmup_sessions":21,"status":"CHRONOLOGICAL_SHADOW_FEED_TEST"}
if __name__=="__main__":print(json.dumps(audit(),indent=2))
