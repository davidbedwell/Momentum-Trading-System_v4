import json, pathlib, concurrent.futures, math
import pandas as pd
from ga5_chromosome_contract import Genome
from ga5_redesign.guarded_evaluator_niche_single_exit import PreparedSessions
from ga6.research_exit_replay_evaluator import evaluate
R=pathlib.Path('/opt/mts'); S=R/'ga6/runs/post_v3_comparison_20261022'; OUT=R/'ga6/runs/independent_review'; FRAME=None;POLICY=None
SCENARIOS=[('baseline',None,'baseline')]
def setup(frame,policy):
 global FRAME,POLICY
 FRAME=PreparedSessions(frame);POLICY=policy
def run(job):
 key,definition=job;g=Genome(**definition['genome']);results=[]
 for label,limit,exitpolicy in SCENARIOS:
  r=evaluate(FRAME,g,entry_tree=definition['entry_tree'],breadth_limit=limit,exit_policy=exitpolicy,**POLICY)
  results.append({'hash':key,'scenario':label,'cagr':r['cagr_diagnostic'],'mdd':r['mdd_diagnostic'],'trades':r['ga6_completed_position_metrics']['completed_trades'],'final_nav':r['final_nav']})
 return results
def main():
 sel=pd.read_csv(S/'dev87_53_survivors_ranked.csv');defs={}
 for line in (S/'unique_chromosome_definitions.jsonl').open():
  j=json.loads(line)
  if j['system']=='structural_v3':defs[j['definition_hash']]=j['definition']
 jobs=[(r.definition_hash,defs[r.definition_hash]) for r in sel.itertuples(index=False)]
 f=pd.read_parquet(R/'ga5_redesign/exploratory79_ga4_enriched.parquet');f=f[(f.date>='2025-01-01')&(f.date<'2026-09-15')&(~f.ticker.isin(['GEV','HWM','GLW','GE']))]
 raw=json.loads((R/'ga5_redesign/exploratory79_policy.json').read_text());dates=set(str(x)[:10] for x in f.date.unique());tickers=set(f.ticker)
 policy={'membership':{(d,t):v for d,t,v in raw['membership'] if d in dates and t in tickers},'risk_veto':{d:v for d,v in raw['risk_veto'].items() if d in dates},'blocked':{t:frozenset(v) for t,v in raw['blocked'].items()},'annual_cash_yield':raw['cash_proxy_annual_yield']}
 results=[]
 with concurrent.futures.ProcessPoolExecutor(max_workers=8,initializer=setup,initargs=(f,policy)) as pool:
  for i,rows in enumerate(pool.map(run,jobs),1):
   results.extend(rows)
   if i%10==0:print('DEV79',i,'/',len(jobs),flush=True)
 out=OUT/'DEV79_EXCLUDE_TOP4_CONTROLLED_REPLAYS.csv';pd.DataFrame(results).to_csv(out,index=False)
 print(pd.DataFrame(results).groupby('scenario').agg(count=('hash','size'),median_cagr=('cagr','median'),median_mdd=('mdd','median'),mean_cagr=('cagr','mean'),mean_mdd=('mdd','mean'),median_trades=('trades','median')).to_string());print('COMPLETED',len(results),out,flush=True)
if __name__=='__main__':main()
