import sys,json,random,hashlib,os
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import pandas as pd
sys.path[:0]=['/opt/mts','/opt/mts/ga5_redesign']
from ga5_chromosome_contract import Genome
from niche_portfolio_breeder_v1 import breed_niche_portfolio
from pareto_trade_objectives import breed_pareto as original_breed
from fitness_niche_loss_control import fitness
from canonical_engine import ResultCache
from guarded_evaluator_niche_single_exit import evaluate,PreparedSessions
p=Path('/opt/mts/ga5_redesign/dev79_niche_origin_500x1000_20261019')
root=Path('/opt/mts/ga5_redesign')
out=p/'all13_niche_screen'/'matched_offspring_portfolio_20261020'
out.mkdir(exist_ok=True)
state=json.loads((p/'checkpoint_unified.json').read_text())
members=[Genome(**x) for x in state['members']]
cache=ResultCache(p/'evaluations.sqlite')
scored=[]
for g in members:
 k=cache.key(g,state['data'],'DEV79_FULL','unified:'+state['policy']+':'+state['code'])
 r=cache.get(k)
 if r is not None:scored.append((fitness(r),g,r))
cache.close()
print('CACHED_PARENTS',len(scored),flush=True)
if len(scored)<300:raise RuntimeError('Insufficient cached parent evaluations')
old,_=original_breed(scored,random.Random(1700),500)
new,_=breed_niche_portfolio(scored,random.Random(1700),500)
existing={g.identity():r for _,g,r in scored}
needed={}
for g in old+new:
 if g.identity() not in existing:needed[g.identity()]=g
print('UNIQUE_NOVEL_TO_EVALUATE',len(needed),flush=True)
frame=pd.read_parquet(root/'exploratory79_ga4_enriched.parquet')
frame=frame[(frame.date>='2005-09-14')&(frame.date<'2026-09-15')]
prepared=PreparedSessions(frame)
label_frame=pd.read_parquet(root/'dev79_niche_ga_v1/labels.parquet')
labels={(str(r.date)[:10],r.ticker):r.research_niche for r in label_frame.itertuples(index=False)}
for key in prepared.membership_keys:labels.setdefault(key,None)
policy=json.loads((root/'exploratory79_policy.json').read_text())
membership={(d,t):v for d,t,v in policy['membership']}
veto=policy['risk_veto'];blocked={t:frozenset(v) for t,v in policy['blocked'].items()}
args=(blocked,membership,veto,policy['cash_proxy_annual_yield'],labels)
def init(prep,arguments):
 global _PREP,_ARGS
 _PREP=prep;_ARGS=arguments
def worker(g):
 blocked,membership,veto,cash_yield,labels=_ARGS
 return evaluate(_PREP,g,blocked=blocked,membership=membership,risk_veto=veto,annual_cash_yield=cash_yield,niche_labels=labels)
genomes=list(needed.values())
with ProcessPoolExecutor(max_workers=8,initializer=init,initargs=(prepared,args)) as pool:
 with (out/'novel_evaluations.jsonl').open('a') as f:
  for i,(g,r) in enumerate(zip(genomes,pool.map(worker,genomes)),1):
   existing[g.identity()]=r
   f.write(json.dumps(dict(id=g.identity(),niche=g.niche,result=r),default=str)+'\n')
   if i%25==0:
    f.flush();print('EVALUATED',i,'/',len(genomes),flush=True)
rows=[]
for method,children in [('original',old),('corrected',new)]:
 for g in children:
  r=existing.get(g.identity())
  if r is None:continue
  shadow=r.get('shadow',{})
  rows.append(dict(method=method,niche=g.niche,id=g.identity(),novel=g.identity() in needed,cagr=r.get('cagr_diagnostic'),mdd=r.get('mdd_diagnostic'),calmar=r.get('calmar_diagnostic'),fills=r.get('fills'),win_rate=shadow.get('win_rate'),mean_net_return=shadow.get('mean_net_return'),closed_trades=shadow.get('closed_trades')))
df=pd.DataFrame(rows)
df.to_csv(out/'all13_offspring_portfolio_comparison.csv',index=False)
report=df.groupby(['niche','method']).agg(count=('id','count'),novel=('novel','sum'),median_cagr=('cagr','median'),best_cagr=('cagr','max'),median_mdd=('mdd','median'),median_calmar=('calmar','median'),median_win_rate=('win_rate','median')).reset_index()
report.to_csv(out/'all13_offspring_summary.csv',index=False)
print('COMPLETE',out,flush=True)
print(report.to_string(index=False),flush=True)
