import json,pathlib,concurrent.futures
import pandas as pd
from ga5_chromosome_contract import Genome
from ga5_redesign.guarded_evaluator_niche_single_exit import PreparedSessions
from ga6.research_exit_replay_evaluator import evaluate
R=pathlib.Path('/opt/mts');S=R/'ga6/runs/post_v3_comparison_20261022';O=R/'ga6/runs/independent_review'; FRAME=None;POLICY=None;G=None;TREE=None
def setup(f,p,g,tree):
 global FRAME,POLICY,G,TREE
 FRAME=PreparedSessions(f);POLICY=p;G=Genome(**g);TREE=tree
def run(t):
 # Excluding one ticker from membership preserves the same 79-stock market panel and all other signals.
 policy=dict(POLICY);policy['membership']={k:(v and k[1]!=t) for k,v in POLICY['membership'].items()}
 r=evaluate(FRAME,G,entry_tree=TREE,**policy)
 return {'excluded_ticker':t,'cagr':r['cagr_diagnostic'],'mdd':r['mdd_diagnostic'],'trades':r['ga6_completed_position_metrics']['completed_trades'],'nav':r['final_nav']}
def main():
 baseline=pd.read_csv(O/'DEV79_CLAUDE_CONTROLLED_REPLAYS.csv');baseline=baseline[baseline.scenario=='baseline'].sort_values('cagr');key=baseline.iloc[len(baseline)//2]['hash'];defs={}
 for line in (S/'unique_chromosome_definitions.jsonl').open():
  j=json.loads(line)
  if j['system']=='structural_v3' and j['definition_hash']==key:defs=j['definition'];break
 f=pd.read_parquet(R/'ga5_redesign/exploratory79_ga4_enriched.parquet');f=f[(f.date>='2025-01-01')&(f.date<'2026-09-15')];raw=json.loads((R/'ga5_redesign/exploratory79_policy.json').read_text());dates=set(str(x)[:10] for x in f.date.unique());tickers=sorted(set(f.ticker));policy={'membership':{(d,t):v for d,t,v in raw['membership'] if d in dates and t in tickers},'risk_veto':{d:v for d,v in raw['risk_veto'].items() if d in dates},'blocked':{t:frozenset(v) for t,v in raw['blocked'].items()},'annual_cash_yield':raw['cash_proxy_annual_yield']}
 results=[]
 with concurrent.futures.ProcessPoolExecutor(max_workers=8,initializer=setup,initargs=(f,policy,defs['genome'],defs['entry_tree'])) as pool:
  for i,r in enumerate(pool.map(run,tickers),1):
   results.append(r)
   if i%20==0:print('EXCLUSION',i,'/',len(tickers),flush=True)
 df=pd.DataFrame(results);base=baseline[baseline.hash==key].iloc[0];df['cagr_improvement_vs_baseline']=df.cagr-base.cagr;df['mdd_change_vs_baseline']=df.mdd-base.mdd;df=df.sort_values('cagr_improvement_vs_baseline',ascending=False);path=O/'DEV79_MEDIAN_CHROMOSOME_TICKER_EXCLUSIONS.csv';df.to_csv(path,index=False)
 print('BASELINE',key,'CAGR',base.cagr,'MDD',base.mdd,'TRADES',base.trades);print('WORST DRAGS',df.head(15).to_string(index=False));print('BEST CONTRIBUTORS',df.tail(10).to_string(index=False));print('OUTPUT',path,flush=True)
if __name__=='__main__':main()
