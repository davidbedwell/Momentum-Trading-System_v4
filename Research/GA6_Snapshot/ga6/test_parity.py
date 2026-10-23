import sys,json
from pathlib import Path
sys.path.insert(0,'/opt/mts')
sys.path.insert(0,'/opt/mts/ga5_redesign')
import pandas as pd
from ga5_redesign.niche_seeds import initial
from ga5_redesign.guarded_evaluator_niche_single_exit import evaluate as old,PreparedSessions
from ga6.evaluator_adapter import evaluate as new

def test_replay_parity():
 p=Path('/opt/mts/ga5_redesign')
 df=pd.read_parquet(p/'exploratory79_ga4_enriched.parquet')
 days=sorted(df.date.unique())
 prep=PreparedSessions(df[df.date.isin(days[:120])])
 policy=json.loads((p/'exploratory79_policy.json').read_text())
 kw=dict(blocked={t:frozenset(v) for t,v in policy['blocked'].items()},membership={(d,t):v for d,t,v in policy['membership']},risk_veto=policy['risk_veto'],annual_cash_yield=policy['cash_proxy_annual_yield'])
 for niche in ('NICHE-0001','NICHE-0002','NICHE-0003'):
  g=initial(niche)
  a=old(prep,g,**kw);b=new(prep,g,**kw)
  for key in a:
   assert a[key]==b[key],(niche,key)
  assert 'ga6_trade_metrics' in b
