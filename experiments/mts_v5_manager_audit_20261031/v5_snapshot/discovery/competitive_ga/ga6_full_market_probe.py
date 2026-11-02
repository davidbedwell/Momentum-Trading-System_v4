"""Real GA6 native decisions across 500 synthetic stocks at one causal close.
Diagnostic only: no execution, GA7, chromosome-library completeness, or PIT certification.
"""
import json,sqlite3,sys
from pathlib import Path
sys.path.insert(0,"/opt/mts")
sys.path.insert(0,"/opt/Momentum-Trading-System_v5-alpha")
import numpy as np,pandas as pd
from ga6.structural_evolution_v3_20261022.structural_candidate import StructuralCandidate
from ga6.native_position_decision_adapter import native_action
from ga5_redesign.ga4_registry import GA4_COLUMNS
from discovery.competitive_ga.full_market_matcher import match_all

root=Path("/opt/mts/synthetic-market-lab/runs/causal_native_features")
family=pd.read_parquet(root/"universe_1_eight_family.parquet")
ga4=pd.read_parquet(root/"universe_1_ga4_native.parquet")
day=str(family.date.max())[:10]
family=family[family.date.astype(str).str[:10]==day].copy()
ga4=ga4[ga4.date.astype(str).str[:10]==day].copy()
ga4=ga4[["ticker",*GA4_COLUMNS]].copy()
for c in GA4_COLUMNS:
    ga4["ga4_"+c]=np.tanh(pd.to_numeric(ga4[c],errors="coerce").clip(-1e8,1e8))
ga4=ga4.drop(columns=list(GA4_COLUMNS))
joined=family.merge(ga4,on="ticker",validate="one_to_one")
rows={str(r["ticker"]):r for r in joined.to_dict("records")}
db=sqlite3.connect("/opt/mts/ga6/runs/frozen_four_run_20261024/catalogue.sqlite")
ids=[r[0] for r in db.execute("SELECT id FROM chromosomes LIMIT 100")]
class IndexedCandidate:
    def __init__(self,sid,native):self.chromosome_id=sid;self.native=native
candidates=[]
for sid in ids:
    definition=db.execute("SELECT definition FROM chromosomes WHERE id=?",(sid,)).fetchone()[0]
    c=StructuralCandidate.restore(json.loads(definition))
    candidates.append(IndexedCandidate(sid,c))
counter={"no_data":0,"no_entry":0,"enter":0}
def native(c,row,held,asof):
    action,weight=native_action(c.native,row,held,1000)
    counter[action.lower()]=counter.get(action.lower(),0)+1
    return action,weight
matches,counts=match_all(day,rows,candidates,lambda c,row,t:True,native)
result={"status":"RESEARCH_DIAGNOSTIC","date":day,"chromosomes":len(candidates),
        "stocks":len(rows),"counts":counts,"native_actions":counter,
        "limitations":"100 GA6 sampled, one synthetic close, no GA7, no native ledger or portfolio allocation"}
out=Path("/opt/mts/synthetic-market-lab/reports/ga6_full_market_probe.json")
out.write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
