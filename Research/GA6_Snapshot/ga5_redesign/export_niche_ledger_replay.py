"""Independent targeted GA5 ledger replay. Does not modify the production evaluator."""
import json,sys,csv,hashlib
from pathlib import Path
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parent))
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from ga5_chromosome_contract import Genome
from guarded_evaluator_niche_single_exit import PreparedSessions
root=Path(__file__).resolve().parent
src=(root/'guarded_evaluator_niche_single_exit.py').read_text()
needle=' return {"status":"GUARDED_RESEARCH_ONLY"'
assert src.count(needle)==1
src=src.replace(needle,' globals()["_CAPTURE"]={"nav":nav,"fills":ledger.fills}\n'+needle)
ns={'__name__':'ga5_replay_capture'}
exec(compile(src,str(root/'guarded_evaluator_niche_single_exit.py'),'exec'),ns)
evaluate=ns['evaluate']
out=root/'dev79_niche_origin_500x1000_20261019'
selected={}
for line in (out/'all_evaluations.jsonl').open():
 x=json.loads(line);r=x['result'];n=x['origin_niche']
 if r['fills']<100:continue
 if n not in selected or r['cagr_diagnostic']>selected[n]['result']['cagr_diagnostic']:selected[n]=x
print('selected',len(selected),flush=True)
frame=pd.read_parquet(root/'exploratory79_ga4_enriched.parquet')
frame=frame[(frame.date>='2005-09-14')&(frame.date<'2026-09-15')]
prepared=PreparedSessions(frame)
policy=json.loads((root/'exploratory79_policy.json').read_text())
labels=pd.read_parquet(root/'dev79_niche_ga_v1/labels.parquet')
label_map={(str(r.date)[:10],r.ticker):r.research_niche for r in labels.itertuples(index=False)}
for key in prepared.membership_keys:label_map.setdefault(key,None)
membership={(d,t):v for d,t,v in policy['membership']}
blocked={t:frozenset(v) for t,v in policy['blocked'].items()}
dest=out/'ledger_replay_audit';dest.mkdir(exist_ok=True)
manifest=[]
for n,x in sorted(selected.items()):
 ns.pop('_CAPTURE',None)
 result=evaluate(prepared,Genome(**x['genome']),blocked=blocked,membership=membership,risk_veto=policy['risk_veto'],annual_cash_yield=policy['cash_proxy_annual_yield'],niche_labels=label_map)
 cap=ns['_CAPTURE']
 assert abs(result['cagr_diagnostic']-x['result']['cagr_diagnostic'])<1e-10,(n,'cagr mismatch')
 assert abs(result['mdd_diagnostic']-x['result']['mdd_diagnostic'])<1e-10,(n,'mdd mismatch')
 with (dest/(n+'_daily_nav.csv')).open('w') as f:
  w=csv.writer(f);w.writerow(['date','nav']);w.writerows(cap['nav'])
 with (dest/(n+'_fills.jsonl')).open('w') as f:
  for fill in cap['fills']:f.write(json.dumps(fill,default=str)+'\n')
 manifest.append({'niche':n,'chromosome_id':x['chromosome_id'],'cagr':result['cagr_diagnostic'],'mdd':result['mdd_diagnostic'],'fills':len(cap['fills']),'nav_sessions':len(cap['nav']),'reconciled':True})
 print('RECONCILED',n,round(result['cagr_diagnostic']*100,2),round(result['mdd_diagnostic']*100,2),flush=True)
(dest/'manifest.json').write_text(json.dumps(manifest,indent=2))
navs={m['niche']:pd.read_csv(dest/(m['niche']+'_daily_nav.csv'),index_col='date')['nav'].pct_change() for m in manifest}
returns=pd.DataFrame(navs).dropna()
returns.corr().to_csv(dest/'daily_return_correlation.csv')
for start,end,label in [('2007-10-01','2009-03-31','gfc'),('2020-02-01','2020-04-30','covid'),('2022-01-01','2022-12-31','bear2022')]:
 subset=returns.loc[start:end]
 subset.corr().to_csv(dest/(label+'_correlation.csv'))
 print(label,'mean pairwise correlation',round(subset.corr().where(~pd.DataFrame(__import__('numpy').eye(len(navs),dtype=bool),index=navs,columns=navs)).stack().mean(),3),flush=True)
print('DONE',dest,flush=True)
