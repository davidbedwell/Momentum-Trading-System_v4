import sys,json,collections
from pathlib import Path
sys.path[:0]=['/opt/mts','/opt/mts/ga5_redesign']
import pandas as pd
from niche_seeds import initial
from optimizer_v3 import NICHES
from ga5_redesign.guarded_evaluator_niche_single_exit import PreparedSessions
from ga6.guarded_evaluator_risk_40session_20261021 import evaluate
r=Path('/opt/mts')
f=pd.read_parquet(r/'ga5_redesign/exploratory79_ga4_enriched.parquet')
f=f[(f.date>='2005-09-14')&(f.date<'2026-09-15')]
p=PreparedSessions(f)
policy=json.loads((r/'ga5_redesign/exploratory79_policy.json').read_text())
g=initial(NICHES[0])
a=evaluate(p,g,blocked={t:frozenset(v) for t,v in policy['blocked'].items()},membership={(d,t):v for d,t,v in policy['membership']},risk_veto=policy['risk_veto'],annual_cash_yield=policy['cash_proxy_annual_yield'])
print(json.dumps({'chromosome':g.identity(),'cagr':a['cagr_diagnostic'],'mdd':a['mdd_diagnostic'],'risk_events':dict(collections.Counter(e['event'] for e in a['ga6_position_risk_events'])),'shadow_max_sessions':max((t['sessions'] for t in a['shadow']['trades']),default=None),'fills':a['fills']}),flush=True)
