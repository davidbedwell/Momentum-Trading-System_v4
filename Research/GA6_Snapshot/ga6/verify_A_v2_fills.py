from pathlib import Path
import json,random
import pandas as pd
from ga5_redesign.niche_seeds import initial
from ga5_redesign.optimizer_v3 import NICHES
from ga5_redesign.guarded_evaluator_niche_single_exit import PreparedSessions
from ga6.structural_independent_v2_20261022.structural_candidate import StructuralCandidate
from ga6.structural_independent_v2_20261022.structural_population import random_tree
from ga6.crash_defense_A_v2_adapter import build_revised_daily_state
import ga6.structural_independent_v2_20261022.structural_portfolio_evaluator as ev
root=Path('/opt/mts'); out=root/'ga6/runs/A_v2_fill_parity_20261022';out.mkdir(parents=True,exist_ok=True)
frame=pd.read_parquet(root/'ga5_redesign/exploratory79_ga4_enriched.parquet')
frame=frame[(frame.date>='2020-02-01')&(frame.date<'2020-04-15')]
prepared=PreparedSessions(frame)
j=json.loads((root/'ga5_redesign/exploratory79_policy.json').read_text())
membership={(d,t):v for d,t,v in j['membership'] if d in prepared.dates}
blocked={t:frozenset(v) for t,v in j['blocked'].items()}
base={d:v for d,v in j['risk_veto'].items() if d in prepared.dates}
state=build_revised_daily_state().set_index('date');state.index=state.index.strftime('%Y-%m-%d')
revised={d:bool(base[d] is True and not state.iloc[state.index.get_loc(d)-1].defensive) for d in prepared.dates}
assert base['2020-03-04'] is True and revised['2020-03-04'] is False
original=ev.SettledLedger
captured=[]
class Capture(original):
 def __init__(self,*a,**kw):
  super().__init__(*a,**kw);captured.append(self)
ev.SettledLedger=Capture
rng=random.Random(6106)
candidate=StructuralCandidate(initial('NICHE-0013'),random_tree(rng))
results={}
for name,veto in [('baseline',base),('revised',revised)]:
 before=len(captured)
 r=candidate.replay(prepared,blocked=blocked,membership=membership,risk_veto=veto,annual_cash_yield=j['cash_proxy_annual_yield'])
 assert len(captured)==before+1
 fills=captured[-1].fills
 rows=[{'date':str(f.get('execution_date',f.get('date',''))),'side':f['side'],'ticker':f['security'],'shares':f['shares'],'price':f['price']} for f in fills]
 print(name,'example',fills[0] if fills else None)
 results[name]=dict(fills=rows,result=r)
ev.SettledLedger=original
(out/'fill_comparison.json').write_text(json.dumps(results,indent=2,default=str))
print('RESULT',out/'fill_comparison.json')
