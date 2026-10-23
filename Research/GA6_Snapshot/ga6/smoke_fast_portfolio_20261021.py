import sys,json
from pathlib import Path
sys.path[:0]=['/opt/mts','/opt/mts/ga5_redesign']
import pandas as pd
from niche_seeds import initial
from optimizer_v3 import NICHES
from ga5_redesign.guarded_evaluator_niche_single_exit import PreparedSessions
from ga6.fast_portfolio_evaluator_20261021 import evaluate
from ga6.portfolio_pareto_20261021 import fitness,rank_scored
r=Path('/opt/mts');f=pd.read_parquet(r/'ga5_redesign/exploratory79_ga4_enriched.parquet')
f=f[(f.date>='2005-09-14')&(f.date<'2026-09-15')]
p=PreparedSessions(f);policy=json.loads((r/'ga5_redesign/exploratory79_policy.json').read_text())
g=initial(NICHES[0])
a=evaluate(p,g,blocked={t:frozenset(v) for t,v in policy['blocked'].items()},membership={(d,t):v for d,t,v in policy['membership']},risk_veto=policy['risk_veto'],annual_cash_yield=policy['cash_proxy_annual_yield'])
assert 'shadow' not in a and 'ga6_trade_metrics' not in a
assert rank_scored([(fitness(a),g,a)])[0][1]==g
print(json.dumps({'status':'FAST_EVALUATOR_SMOKE_PASSED','cagr':a['cagr_diagnostic'],'mdd':a['mdd_diagnostic'],'fills':a['fills'],'risk_pending_at_end':a['ga6_risk_pending_at_end'],'shadow_absent':True}),flush=True)
