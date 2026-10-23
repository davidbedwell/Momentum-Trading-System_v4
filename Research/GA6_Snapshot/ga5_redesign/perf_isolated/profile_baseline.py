import sys,json,cProfile,pstats,io,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pandas as pd
from ga5_chromosome_contract import Genome
from guarded_evaluator_niche_single_exit import evaluate,PreparedSessions
root=Path(__file__).resolve().parents[1]
frame=pd.read_parquet(root/'exploratory79_ga4_enriched.parquet');frame=frame[(frame.date>='2005-09-14')&(frame.date<'2026-09-15')];frame=frame[frame.date.isin(sorted(frame.date.unique())[:200])]
prep=PreparedSessions(frame);p=json.loads((root/'exploratory79_policy.json').read_text())
labels=pd.read_parquet(root/'dev79_niche_ga_v1'/'labels.parquet');labels={(str(r.date)[:10],r.ticker):r.research_niche for r in labels.itertuples(index=False)}
for k in prep.membership_keys:labels.setdefault(k,None)
kw=dict(blocked={t:frozenset(v) for t,v in p['blocked'].items()},membership={(d,t):v for d,t,v in p['membership']},risk_veto=p['risk_veto'],annual_cash_yield=p['cash_proxy_annual_yield'],niche_labels=labels)
selected={}
with (root/'dev79_niche_origin_500x1000_20261019'/'all_evaluations.jsonl').open() as f:
 for line in f:
  x=json.loads(line)
  if x['origin_niche'] in ('NICHE-0001','NICHE-0013') and x['origin_niche'] not in selected:selected[x['origin_niche']]=Genome(**x['genome'])
for n,g in selected.items():
 pr=cProfile.Profile();t=time.perf_counter();pr.enable();result=evaluate(prep,g,**kw);pr.disable();dt=time.perf_counter()-t
 print('PROFILE',n,'seconds',round(dt,4),'fills',result['fills'],'shadow',result['shadow']['closed_trades'],flush=True)
 s=io.StringIO();pstats.Stats(pr,stream=s).strip_dirs().sort_stats('cumtime').print_stats(24);print(s.getvalue(),flush=True)
