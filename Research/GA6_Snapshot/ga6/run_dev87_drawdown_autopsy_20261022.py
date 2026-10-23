import json,csv,pathlib,collections,hashlib
from concurrent.futures import ProcessPoolExecutor
import pandas as pd
from ga5_chromosome_contract import Genome
from ga5_redesign.guarded_evaluator_niche_single_exit import PreparedSessions
from ga6.structural_dd_instrumented_20261022 import evaluate
ROOT=pathlib.Path('/opt/mts');OUT=ROOT/'ga6/runs/post_v3_comparison_20261022';DATA=ROOT/'thunder-migration/mts-certification-20261011/dev87';FRAME=None;POLICY=None

def setup(frame,policy):
 global FRAME,POLICY
 FRAME=PreparedSessions(frame);POLICY=policy

def run(job):
 key,definition,expected=job;g=Genome(**definition['genome']);r=evaluate(FRAME,g,entry_tree=definition['entry_tree'],**POLICY)
 if abs(r['cagr_diagnostic']-expected['cagr'])>1e-9 or abs(r['mdd_diagnostic']-expected['mdd'])>1e-9 or r['ga6_completed_position_metrics']['completed_trades']!=expected['completed_trades']:raise RuntimeError('Instrumentation changed original metrics: '+key)
 nav=r['diagnostic_daily'];peak=100000.;peak_date='';max_dd=0.;trough=None
 for row in nav:
  if row['nav']>peak:peak=row['nav'];peak_date=row['date']
  dd=row['nav']/peak-1
  if dd<max_dd:max_dd=dd;trough={'peak_date':peak_date,'trough_date':row['date'],'drawdown':dd,'peak_nav':peak,'trough_nav':row['nav']}
 if trough is None:trough={'peak_date':'','trough_date':'','drawdown':0.,'peak_nav':100000.,'trough_nav':100000.}
 for t in r['diagnostic_trades']:
  t['chromosome']=key;t['portfolio_mdd']=r['mdd_diagnostic'];t['overlaps_peak_trough']=(t['entry_date']<=trough['trough_date'] and t['exit_date']>=trough['peak_date'])
 return {'hash':key,'trades':r['diagnostic_trades'],'daily':nav,'trough':trough,'open_positions':len(r['ga6_risk_pending_at_end'])}

def main():
 sel=pd.read_csv(OUT/'dev87_53_survivors_ranked.csv');defs={}
 for line in (OUT/'unique_chromosome_definitions.jsonl').open():
  j=json.loads(line)
  if j['system']=='structural_v3':defs[j['definition_hash']]=j['definition']
 jobs=[(r.definition_hash,defs[r.definition_hash],{'cagr':r.cagr_dev87,'mdd':r.mdd_dev87,'completed_trades':r.completed_trades_dev87}) for r in sel.itertuples(index=False)]
 f=pd.read_parquet(DATA/'dev87_ga6_enriched.parquet');f=f[(f.date>='2025-01-01')&(f.date<'2026-09-15')]
 raw=json.loads((DATA/'dev87_ga6_policy.json').read_text());dates=set(str(x)[:10] for x in f.date.unique());tickers=set(f.ticker)
 policy={'membership':{(d,t):v for d,t,v in raw['membership'] if d in dates and t in tickers},'risk_veto':{d:v for d,v in raw['risk_veto'].items() if d in dates},'blocked':{t:frozenset(v) for t,v in raw['blocked'].items()},'annual_cash_yield':raw['cash_proxy_annual_yield']}
 target=OUT/'dev87_drawdown_autopsy.jsonl';done=set()
 if target.exists():
  for line in target.open():done.add(json.loads(line)['hash'])
 jobs=[j for j in jobs if j[0] not in done]
 with ProcessPoolExecutor(max_workers=8,initializer=setup,initargs=(f,policy)) as pool:
  for i,result in enumerate(pool.map(run,jobs),1):
   with target.open('a') as out:out.write(json.dumps(result,allow_nan=False)+'\n')
   print('autopsy',i,'/',len(jobs),result['hash'][:10],len(result['trades']),flush=True)
 print('COMPLETE',len(jobs),flush=True)
if __name__=='__main__':main()
