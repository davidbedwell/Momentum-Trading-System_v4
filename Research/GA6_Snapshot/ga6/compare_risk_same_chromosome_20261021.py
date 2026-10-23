import sys,json,collections
from pathlib import Path
sys.path[:0]=['/opt/mts','/opt/mts/ga5_redesign']
import pandas as pd
from ga5_chromosome_contract import Genome
from ga5_redesign.guarded_evaluator_niche_single_exit import PreparedSessions
from ga6.guarded_evaluator_risk_experiment_20261021 import evaluate
r=Path('/opt/mts')
f=pd.read_parquet(r/'ga5_redesign/exploratory79_ga4_enriched.parquet')
f=f[(f.date>='2005-09-14')&(f.date<'2026-09-15')]
p=PreparedSessions(f)
policy=json.loads((r/'ga5_redesign/exploratory79_policy.json').read_text())
target='33a3baa313664e4108d1f4506b640ee78ee86672c0537302adb03598068bbc0c'
g=next(Genome(**x['genome']) for line in (r/'ga6/runs/ga6_production_200_v1/all_evaluations.jsonl').open() if (x:=json.loads(line)) and Genome(**x['genome']).identity()==target)
a=evaluate(p,g,blocked={t:frozenset(v) for t,v in policy['blocked'].items()},membership={(d,t):v for d,t,v in policy['membership']},risk_veto=policy['risk_veto'],annual_cash_yield=policy['cash_proxy_annual_yield'])
out={'chromosome':target,'cagr':a['cagr_diagnostic'],'mdd':a['mdd_diagnostic'],'events_by_type':dict(collections.Counter(e['event'] for e in a['ga6_position_risk_events'])),'events':a['ga6_position_risk_events'],'pending_at_end':a['ga6_risk_pending_at_end']}
path=r/'ga6/runs/GA6_DUAL_TRACK_REDESIGN_20261021/risk_policy_same_chromosome_20261021.json'
path.write_text(json.dumps(out,indent=2,default=str))
print(json.dumps({k:v for k,v in out.items() if k!='events'},default=str),flush=True)
