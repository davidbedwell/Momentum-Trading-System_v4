import json,pathlib,concurrent.futures
import pandas as pd
from ga5_chromosome_contract import Genome
from ga5_redesign.guarded_evaluator_niche_single_exit import PreparedSessions
from ga6.research_band_replay_evaluator import evaluate
R=pathlib.Path('/opt/mts');S=R/'ga6/runs/post_v3_comparison_20261022';D=R/'thunder-migration/mts-certification-20261011/dev87';OUT=R/'ga6/runs/independent_review';FRAME=None;POLICY=None

def setup(frame,policy):
 global FRAME,POLICY
 FRAME=PreparedSessions(frame);POLICY=policy

def run(job):
 key,definition,expected=job;g=Genome(**definition['genome']);results=[]
 for label,floor,limit in [('baseline',None,None),('le45',None,.45),('45to50',.45,.50),('50to55',.50,.55),('55to60',.55,.60),('gt60',.60,None),('le55',None,.55)]:
  r=evaluate(FRAME,g,entry_tree=definition['entry_tree'],breadth_limit=limit,breadth_floor=floor,**POLICY)
  if label=='baseline':
   if abs(r['cagr_diagnostic']-expected['cagr'])>1e-9 or abs(r['mdd_diagnostic']-expected['mdd'])>1e-9 or r['ga6_completed_position_metrics']['completed_trades']!=expected['trades']:raise ValueError('BASELINE MISMATCH '+key)
  results.append({'hash':key,'scenario':label,'cagr':r['cagr_diagnostic'],'mdd':r['mdd_diagnostic'],'trades':r['ga6_completed_position_metrics']['completed_trades'],'final_nav':r['final_nav'],'buys':r['signal_trace']['executed_buys']})
 return results

def main():
 sel=pd.read_csv(S/'dev87_53_survivors_ranked.csv');defs={}
 for line in (S/'unique_chromosome_definitions.jsonl').open():
  j=json.loads(line)
  if j['system']=='structural_v3':defs[j['definition_hash']]=j['definition']
 jobs=[(r.definition_hash,defs[r.definition_hash],{'cagr':r.cagr_dev87,'mdd':r.mdd_dev87,'trades':r.completed_trades_dev87}) for r in sel.itertuples(index=False)]
 frame=pd.read_parquet(D/'dev87_ga6_enriched.parquet');frame=frame[(frame.date>='2025-01-01')&(frame.date<'2026-09-15')];raw=json.loads((D/'dev87_ga6_policy.json').read_text());dates=set(str(x)[:10] for x in frame.date.unique());tickers=set(frame.ticker)
 policy={'membership':{(d,t):v for d,t,v in raw['membership'] if d in dates and t in tickers},'risk_veto':{d:v for d,v in raw['risk_veto'].items() if d in dates},'blocked':{t:frozenset(v) for t,v in raw['blocked'].items()},'annual_cash_yield':raw['cash_proxy_annual_yield']}
 results=[]
 with concurrent.futures.ProcessPoolExecutor(max_workers=8,initializer=setup,initargs=(frame,policy)) as pool:
  for i,rows in enumerate(pool.map(run,jobs),1):
   results.extend(rows)
   if i%10==0:print('REPLAY',i,'/',len(jobs),flush=True)
 pd.DataFrame(results).to_csv(OUT/'BREADTH_INDEPENDENT_BAND_REPLAY.csv',index=False)
 summary=pd.DataFrame(results).groupby('scenario').agg(count=('hash','size'),median_cagr=('cagr','median'),median_mdd=('mdd','median'),mean_cagr=('cagr','mean'),mean_mdd=('mdd','mean'),median_trades=('trades','median'))
 print(summary.to_string());print('COMPLETED',len(results),flush=True)
if __name__=='__main__':main()
