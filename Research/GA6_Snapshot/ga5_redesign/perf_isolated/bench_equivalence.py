import sys,time,json,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pandas as pd
from ga5_chromosome_contract import Genome
from guarded_evaluator_niche_single_exit import evaluate as baseline,PreparedSessions
from ga5_redesign.perf_isolated.evaluator_optimized import evaluate as optimized,PreparedSessions as OptimizedPreparedSessions
root=Path(__file__).resolve().parents[1]
frame=pd.read_parquet(root/'exploratory79_ga4_enriched.parquet');frame=frame[(frame.date>='2005-09-14')&(frame.date<'2026-09-15')]
# Use earliest 400 sessions for a representative, bounded equivalence test.
frame=frame[frame.date.isin(sorted(frame.date.unique())[:400])]
prep=PreparedSessions(frame)
optimized_prep=OptimizedPreparedSessions(frame)
p=json.loads((root/'exploratory79_policy.json').read_text())
labels=pd.read_parquet(root/'dev79_niche_ga_v1'/'labels.parquet')
labels={(str(r.date)[:10],r.ticker):r.research_niche for r in labels.itertuples(index=False)}
for k in prep.membership_keys:labels.setdefault(k,None)
kw=dict(blocked={t:frozenset(v) for t,v in p['blocked'].items()},membership={(d,t):v for d,t,v in p['membership']},risk_veto=p['risk_veto'],annual_cash_yield=p['cash_proxy_annual_yield'],niche_labels=labels)
ledger=root/'dev79_niche_origin_500x1000_20261019'/'all_evaluations.jsonl'
selected={}
with ledger.open() as f:
 for line in f:
  x=json.loads(line)
  if x['origin_niche'] in ('NICHE-0001','NICHE-0013') and x['origin_niche'] not in selected:selected[x['origin_niche']]=Genome(**x['genome'])
for niche,g in selected.items():
 t=time.perf_counter();a=baseline(prep,g,**kw);ta=time.perf_counter()-t
 t=time.perf_counter();b=optimized(optimized_prep,g,**kw);tb=time.perf_counter()-t
 if a!=b:
  print('MISMATCH',niche,[(k,a[k],b[k]) for k in a if a[k]!=b[k]][:2],flush=True);raise SystemExit(2)
 print('PASS',niche,'sessions',a['sessions'],'fills',a['fills'],'shadow_trades',a['shadow']['closed_trades'],'baseline_sec',round(ta,3),'optimized_sec',round(tb,3),'speedup',round(ta/tb,3),flush=True)
print('ALL_PASS',flush=True)
