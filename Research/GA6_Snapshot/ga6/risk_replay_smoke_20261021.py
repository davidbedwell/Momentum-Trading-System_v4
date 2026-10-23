"""Single chromosome controlled baseline/risk replay. No production changes."""
import sys,json
from pathlib import Path
sys.path.insert(0,'/opt/mts')
sys.path.insert(0,'/opt/mts/ga5_redesign')
import pandas as pd
from ga5_chromosome_contract import Genome
from ga5_redesign.guarded_evaluator_niche_single_exit import PreparedSessions
from ga6.guarded_evaluator_ga6 import evaluate as baseline
from ga6.guarded_evaluator_risk_experiment_20261021 import evaluate as risk
root=Path('/opt/mts')
frame=pd.read_parquet(root/'ga5_redesign/exploratory79_ga4_enriched.parquet')
frame=frame[(frame.date>='2005-09-14')&(frame.date<'2026-09-15')]
prepared=PreparedSessions(frame)
policy=json.loads((root/'ga5_redesign/exploratory79_policy.json').read_text())
membership={(d,t):v for d,t,v in policy['membership']}
blocked={t:frozenset(v) for t,v in policy['blocked'].items()}
data=[json.loads(s) for s in (root/'ga6/runs/ga6_production_200_v1/all_evaluations.jsonl').open()]
best=max(data,key=lambda x:x['fitness'])
g=Genome(**best['genome'])
args=dict(blocked=blocked,membership=membership,risk_veto=policy['risk_veto'],annual_cash_yield=policy['cash_proxy_annual_yield'])
print('START',g.identity(),flush=True)
a=baseline(prepared,g,**args)
print('BASELINE',a['cagr_diagnostic'],a['mdd_diagnostic'],flush=True)
b=risk(prepared,g,**args)
print('RISK',b['cagr_diagnostic'],b['mdd_diagnostic'],len(b['ga6_position_risk_events']),flush=True)
out=root/'ga6/runs/GA6_DUAL_TRACK_REDESIGN_20261021/risk_replay_smoke.json'
out.write_text(json.dumps({'chromosome':g.identity(),'baseline':{'cagr':a['cagr_diagnostic'],'mdd':a['mdd_diagnostic']},'risk':{'cagr':b['cagr_diagnostic'],'mdd':b['mdd_diagnostic'],'events':b['ga6_position_risk_events']}},indent=2))
