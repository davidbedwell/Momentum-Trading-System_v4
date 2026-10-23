import json,sys,csv
from pathlib import Path
import pandas as pd
root=Path(__file__).resolve().parent
sys.path[:0]=[str(root),str(root.parent)]
from ga5_chromosome_contract import Genome
from guarded_evaluator_niche_single_exit import PreparedSessions
src=(root/'guarded_evaluator_niche_single_exit.py').read_text()
needle=' return {"status":"GUARDED_RESEARCH_ONLY"'
assert src.count(needle)==1
src=src.replace(needle,' globals()["_CAPTURE"]={"nav":nav,"fills":ledger.fills,"shadow_trades":shadow.closed,"shadow_events":shadow.events}\n'+needle)
ns={'__name__':'ga5_niche_research_capture'}
exec(compile(src,str(root/'guarded_evaluator_niche_single_exit.py'),'exec'),ns)
out=root/'dev79_niche_origin_500x1000_20261019'
unique={}
for line in (out/'all_evaluations.jsonl').open():
 x=json.loads(line)
 if x['origin_niche']=='NICHE-0001':unique[x['chromosome_id']]=x
eligible=sorted((x for x in unique.values() if x['result']['shadow']['closed_trades']>=50 and x['result']['fills']>=20),key=lambda x:x['result']['cagr_diagnostic'])
groups={'bottom':eligible[:len(eligible)//3],'middle':eligible[len(eligible)//3:2*len(eligible)//3],'top':eligible[2*len(eligible)//3:]}
selected=[(name,items[len(items)//2]) for name,items in groups.items()]
print('SELECTED',[(n,x['chromosome_id'][:12]) for n,x in selected],flush=True)
frame=pd.read_parquet(root/'exploratory79_ga4_enriched.parquet')
frame=frame[(frame.date>='2005-09-14')&(frame.date<'2026-09-15')]
prepared=PreparedSessions(frame)
policy=json.loads((root/'exploratory79_policy.json').read_text())
labels=pd.read_parquet(root/'dev79_niche_ga_v1/labels.parquet')
label_map={(str(r.date)[:10],r.ticker):r.research_niche for r in labels.itertuples(index=False)}
for key in prepared.membership_keys:label_map.setdefault(key,None)
membership={(d,t):v for d,t,v in policy['membership']}
blocked={t:frozenset(v) for t,v in policy['blocked'].items()}
dest=out/'niche0001_trade_replay';dest.mkdir(exist_ok=True)
for name,x in selected:
 result=ns['evaluate'](frame,Genome(**x['genome']),blocked=blocked,membership=membership,risk_veto=policy['risk_veto'],annual_cash_yield=policy['cash_proxy_annual_yield'],niche_labels=label_map)
 cap=ns['_CAPTURE']
 assert abs(result['cagr_diagnostic']-x['result']['cagr_diagnostic'])<1e-9
 assert abs(result['mdd_diagnostic']-x['result']['mdd_diagnostic'])<1e-9
 (dest/(name+'_shadow_trades.jsonl')).write_text(''.join(json.dumps(t,default=str)+'\n' for t in cap['shadow_trades']))
 (dest/(name+'_fills.jsonl')).write_text(''.join(json.dumps(t,default=str)+'\n' for t in cap['fills']))
 with (dest/(name+'_nav.csv')).open('w') as f:
  w=csv.writer(f);w.writerow(['date','nav']);w.writerows(cap['nav'])
 print('RECONCILED',name,'trades',len(cap['shadow_trades']),'fills',len(cap['fills']),'cagr',result['cagr_diagnostic'],'mdd',result['mdd_diagnostic'],flush=True)
print('COMPLETE',dest,flush=True)
