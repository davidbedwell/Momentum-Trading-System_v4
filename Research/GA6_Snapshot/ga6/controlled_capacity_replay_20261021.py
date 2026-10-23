import json,sys,time
from pathlib import Path
sys.path[:0]=['/opt/mts','/opt/mts/ga5_redesign']
import pandas as pd
from ga5_chromosome_contract import Genome
from ga5_redesign.guarded_evaluator_niche_single_exit import PreparedSessions
from ga6.guarded_evaluator_ga6 import evaluate
root=Path('/opt/mts')
src=root/'ga6/runs/ga6_production_200_v1/all_evaluations.jsonl'
rows=[json.loads(s) for s in src.open()]
gen=max(x['generation'] for x in rows)
group=[x for x in rows if x['generation']==gen]
best=max(group,key=lambda x:x['result']['cagr_diagnostic'])
policy=json.loads((root/'ga5_redesign/exploratory79_policy.json').read_text())
frame=pd.read_parquet(root/'ga5_redesign/exploratory79_ga4_enriched.parquet')
frame=frame[(frame.date>='2005-09-14')&(frame.date<'2026-09-15')]
prepared=PreparedSessions(frame)
membership={(d,t):v for d,t,v in policy['membership']}
blocked={t:frozenset(v) for t,v in policy['blocked'].items()}
genome=Genome(**best['genome'])
output=root/'ga6/runs/controlled_capacity_replay_20261021.jsonl'
for cap in (79,20,10,5):
 start=time.time()
 r=evaluate(prepared,genome,blocked=blocked,membership=membership,risk_veto=policy['risk_veto'],annual_cash_yield=policy['cash_proxy_annual_yield'],max_positions=cap)
 record={'generation':gen,'chromosome':best['chromosome_id'],'max_positions':cap,'cagr':r['cagr_diagnostic'],'mdd':r['mdd_diagnostic'],'final_nav':r['final_nav'],'executed_buys':r['signal_trace']['executed_buys'],'rejected_capacity':r['rejections']['capacity'],'seconds':round(time.time()-start,1)}
 with output.open('a') as f:f.write(json.dumps(record)+'\n')
 print(json.dumps(record),flush=True)
