"""Reproduce historical frozen53 returns with instrumented full engine; extract peak-trough exposures."""
import json,pathlib,concurrent.futures,collections
import pandas as pd
from ga5_chromosome_contract import Genome
from ga5_redesign.guarded_evaluator_niche_single_exit import PreparedSessions
from ga6.structural_dd_instrumented_20261022 import evaluate
R=pathlib.Path('/opt/mts');S=R/'ga6/runs/post_v3_comparison_20261022';O=R/'ga6/runs/certification_gate_20261022';F=None;P=None;D=None;EXPECTED=None
def setup(frame,policy,defs,expected):
 global F,P,D,EXPECTED
 F=PreparedSessions(frame);P=policy;D=defs;EXPECTED=expected
def run(key):
 d=D[key];r=evaluate(F,Genome(**d['genome']),entry_tree=d['entry_tree'],**P);e=EXPECTED[key]
 if abs(r['cagr_diagnostic']-e['cagr'])>1e-9 or abs(r['mdd_diagnostic']-e['mdd'])>1e-9:raise RuntimeError('Instrumentation mismatch '+key)
 peak=100000.;pdte='';worst={'drawdown':0.};daily=r['diagnostic_daily']
 for row in daily:
  if row['nav']>peak:peak=row['nav'];pdte=row['date']
  dd=row['nav']/peak-1
  if dd<worst['drawdown']:worst={'drawdown':dd,'peak':pdte,'trough':row['date'],'peak_nav':peak,'trough_nav':row['nav']}
 if 'trough' not in worst:return {'hash':key,'worst':worst,'largest_losers':[],'exposure_at_trough':[]}
 trades=[t for t in r['diagnostic_trades'] if t.get('entry_date','')<=worst['trough'] and t.get('exit_date','9999')>=worst['peak']]
 sample=next(x for x in daily if x['date']==worst['trough']);holdings=sample['holdings'];exposure=sorted([{'ticker':t,'value':v['shares']*v['close'],'entry_price':v['entry_price'],'unrealized_pct':v['close']/v['entry_price']-1} for t,v in holdings.items()],key=lambda x:x['value']*x['unrealized_pct'])
 return {'hash':key,'worst':worst,'overlapping_trades':len(trades),'largest_losers':sorted(trades,key=lambda x:x.get('net_pnl',x.get('realized_pnl',0)))[:10],'exposure_at_trough':exposure[:20]}
def main():
 names=['2006_2010','2016_2020'];rank=pd.read_csv(S/'dev87_53_survivors_ranked.csv');keys=set(rank.definition_hash);defs={}
 for line in (S/'unique_chromosome_definitions.jsonl').open():
  j=json.loads(line)
  if j.get('system')=='structural_v3' and j.get('definition_hash') in keys:defs[j['definition_hash']]=j['definition']
 f=pd.read_parquet(R/'ga5_redesign/exploratory79_ga4_enriched.parquet');raw=json.loads((R/'ga5_redesign/exploratory79_policy.json').read_text());tickers=set(f.ticker)
 for name in names:
  start,end=('2006-01-01','2011-01-01') if name=='2006_2010' else ('2016-01-01','2021-01-01');out=O/('DRAWDOWN_AUTOPSY_'+name+'.jsonl');done={json.loads(line)['hash'] for line in out.open()} if out.exists() else set();base=pd.read_csv(O/('FROZEN53_'+name+'.csv'));expected={r['hash']:{'cagr':r['cagr'],'mdd':r['mdd']} for r in base.to_dict('records')};todo=sorted(keys-done);frame=f[(f.date>=start)&(f.date<end)];dates=set(str(x)[:10] for x in frame.date.unique());policy={'membership':{(d,t):v for d,t,v in raw['membership'] if d in dates and t in tickers},'risk_veto':{d:v for d,v in raw['risk_veto'].items() if d in dates},'blocked':{t:frozenset(v) for t,v in raw['blocked'].items()},'annual_cash_yield':raw['cash_proxy_annual_yield']}
  print('START',name,len(todo),flush=True)
  with concurrent.futures.ProcessPoolExecutor(max_workers=8,initializer=setup,initargs=(frame,policy,defs,expected)) as pool:
   for i,row in enumerate(pool.map(run,todo),1):
    with out.open('a') as fd:fd.write(json.dumps(row)+'\n')
    if i%10==0:print('PROGRESS',name,i,'/',len(todo),flush=True)
  results=[json.loads(line) for line in out.open()];print('COMPLETE',name,'COUNT',len(results),'TROUGH_MONTHS',collections.Counter(r['worst'].get('trough','')[:7] for r in results).most_common(8),flush=True)
if __name__=='__main__':main()
