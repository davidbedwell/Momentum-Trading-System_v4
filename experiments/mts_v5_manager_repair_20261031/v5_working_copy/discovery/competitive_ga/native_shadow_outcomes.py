"""Attribute native GA6 research replay fills to FIFO realized shadow outcomes.
Owner and context fixed at fill; no future outcomes exposed at decision time.
"""
import json
from collections import Counter
from discovery.competitive_ga.ga6_native_position_replay import run
from discovery.competitive_ga.position_outcome_ledger import PositionOutcomeLedger
from discovery.competitive_ga.causal_calibration import Calibrator

def audit():
    result,fills=run(output="ATTRIBUTED")
    ledger=PositionOutcomeLedger()
    cal=Calibrator(min_samples=5)
    for record in fills:
        date,ticker,side,qty,price,fee=record["fill"]
        session=record["session"]
        cid=record["chromosome_id"]
        context=("GA6_ENTRY",)
        if side=="BUY":
            created=ledger.fill(session,ticker,side,qty,price,fee,cid,context)
        else:
            created=ledger.fill(session,ticker,side,qty,price,fee)
        for obs in created:cal.record(obs)
    matured_after_warmup=[o for o in cal.outcomes if o.maturity_session<21]
    by_owner=Counter(o.chromosome_id for o in cal.outcomes)
    return {"fills":len(fills),"realized_lot_outcomes":len(cal.outcomes),
            "matured_by_session_21":len(matured_after_warmup),
            "outcomes_by_chromosome":dict(by_owner),
            "open_lots":sum(len(v) for v in ledger.lots.values()),
            "status":"RESEARCH_SHADOW_OUTCOME_AUDIT",
            "limitations":"3 native GA6 chromosomes, FIFO partial-lot returns, simplified research kernel; not GA6 native parity or certified PIT."}

if __name__=="__main__":print(json.dumps(audit(),indent=2))
