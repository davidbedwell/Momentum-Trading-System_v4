import sys;sys.path[:0]=["/opt/mts","/opt/mts/ga5_redesign"]
from pathlib import Path
import json,random,sqlite3
import pandas as pd
from ga5_redesign.niche_seeds import initial
from ga5_redesign.optimizer_v3 import NICHES
from ga5_redesign.guarded_evaluator_niche_single_exit import PreparedSessions
from ga6.structural_independent_v2_20261022.structural_population import random_tree
from ga6.structural_independent_v2_20261022.structural_candidate import StructuralCandidate
from ga6.crash_defense_A_v2_adapter import build_revised_daily_state
root=Path('/opt/mts');out=root/'ga6/runs/A_v2_matched_control_20261022';out.mkdir(parents=True,exist_ok=True)
source=root/'ga5_redesign/exploratory79_ga4_enriched.parquet'
frame=pd.read_parquet(source);frame=frame[(frame.date>='2019-01-01')&(frame.date<'2026-09-15')]
prepared=PreparedSessions(frame)
j=json.loads((root/'ga5_redesign/exploratory79_policy.json').read_text())
membership={(d,t):v for d,t,v in j['membership'] if d in prepared.dates}
blocked={t:frozenset(v) for t,v in j['blocked'].items()}
baseline={d:v for d,v in j['risk_veto'].items() if d in prepared.dates}
state=build_revised_daily_state().set_index('date');state.index=state.index.strftime('%Y-%m-%d')
revised={d:bool(baseline[d] is True and not state.iloc[state.index.get_loc(d)-1].defensive) for d in prepared.dates}
rng=random.Random(6106)
members=[StructuralCandidate(initial(n),random_tree(rng)) for n in NICHES for _ in range(2)]
assert len(members)==26
db=sqlite3.connect(str(root/'ga6/runs/A_v2_end_to_end_20261022/structural_manifest.sqlite'))
print('manifest schema',db.execute("select name,sql from sqlite_master where type='table'").fetchall(),flush=True)
data=[]
for k,c in enumerate(members):
 r=c.replay(prepared,blocked=blocked,membership=membership,risk_veto=baseline,annual_cash_yield=j['cash_proxy_annual_yield'])
 data.append(dict(index=k,niche=c.genome.niche,identity=c.identity(),cagr=r['cagr_diagnostic'],mdd=r['mdd_diagnostic'],final_nav=r['final_nav'],completed=r['ga6_completed_position_metrics']['completed_trades'],win_rate=r['ga6_completed_position_metrics']['win_rate']))
 print(k+1,'/',len(members),c.genome.niche,round(r['cagr_diagnostic']*100,2),round(r['mdd_diagnostic']*100,2),flush=True)
 (out/'baseline_results.json').write_text(json.dumps(data,indent=2))
print('DONE',flush=True)
