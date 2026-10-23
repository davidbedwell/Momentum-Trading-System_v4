import json,pathlib,concurrent.futures,time
import pandas as pd
from ga5_chromosome_contract import Genome
from ga5_redesign.guarded_evaluator_niche_single_exit import PreparedSessions
from ga6.research_exit_replay_evaluator import evaluate
R=pathlib.Path('/opt/mts');S=R/'ga6/runs/post_v3_comparison_20261022';O=R/'ga6/runs/independent_review';FRAME=None;POLICY=None;DEFS=None

def setup(f,p,defs):
 global FRAME,POLICY,DEFS
 FRAME=PreparedSessions(f);POLICY=p;DEFS=defs

def run(job):
 key,t=job;d=DEFS[key];p=dict(POLICY);p['membership']={k:(v and k[1]!=t) for k,v in POLICY['membership'].items()} if t else POLICY['membership'];r=evaluate(FRAME,Genome(**d['genome']),entry_tree=d['entry_tree'],**p)
 return {'hash':key,'excluded_ticker':t or '__BASELINE__','cagr':r['cagr_diagnostic'],'mdd':r['mdd_diagnostic'],'trades':r['ga6_completed_position_metrics']['completed_trades'],'final_nav':r['final_nav']}

def main():
 base=pd.read_csv(O/'DEV79_CLAUDE_CONTROLLED_REPLAYS.csv');keys=set(base.loc[base.scenario=='baseline','hash']);defs={}
 for line in (S/'unique_chromosome_definitions.jsonl').open():
  j=json.loads(line)
  if j.get('system')=='structural_v3' and j.get('definition_hash') in keys:defs[j['definition_hash']]=j['definition']
 f=pd.read_parquet(R/'ga5_redesign/exploratory79_ga4_enriched.parquet');f=f[(f.date>='2025-01-01')&(f.date<'2026-09-15')];raw=json.loads((R/'ga5_redesign/exploratory79_policy.json').read_text());dates=set(str(x)[:10] for x in f.date.unique());tickers=sorted(set(f.ticker));policy={'membership':{(d,t):v for d,t,v in raw['membership'] if d in dates and t in tickers},'risk_veto':{d:v for d,v in raw['risk_veto'].items() if d in dates},'blocked':{t:frozenset(v) for t,v in raw['blocked'].items()},'annual_cash_yield':raw['cash_proxy_annual_yield']}
 jobs=[(k,t) for k in sorted(defs) for t in tickers];out=O/'DEV79_ALL53_TICKER_MARGINAL_REPLAYS.csv';done=set()
 if out.exists():
  old=pd.read_csv(out);done=set(zip(old['hash'],old['excluded_ticker']));print('RESUME',len(done),flush=True)
 jobs=[j for j in jobs if j not in done];print('JOBS',len(jobs),'GENOMES',len(defs),'TICKERS',len(tickers),flush=True)
 with concurrent.futures.ProcessPoolExecutor(max_workers=8,initializer=setup,initargs=(f,policy,defs)) as pool:
  chunk=[]
  for i,result in enumerate(pool.map(run,jobs,chunksize=1),1):
   chunk.append(result)
   if len(chunk)>=80 or i==len(jobs):
    pd.DataFrame(chunk).to_csv(out,mode='a',index=False,header=not out.exists());chunk=[];print('COMPLETED',len(done)+i,'/',len(done)+len(jobs),flush=True)
 df=pd.read_csv(out);b=base[base.scenario=='baseline'][['hash','cagr','mdd']].rename(columns={'cagr':'baseline_cagr','mdd':'baseline_mdd'});df=df.merge(b,on='hash');df['delta_cagr']=df.cagr-df.baseline_cagr;df['delta_mdd']=df.mdd-df.baseline_mdd
 summary=df.groupby('excluded_ticker').agg(genomes=('hash','nunique'),median_delta_cagr=('delta_cagr','median'),mean_delta_cagr=('delta_cagr','mean'),pct_genomes_improve_if_excluded=('delta_cagr',lambda s:100*(s>0).mean()),median_delta_mdd=('delta_mdd','median')).sort_values('median_delta_cagr',ascending=False);summary.to_csv(O/'DEV79_ALL53_TICKER_ATTRIBUTION_SUMMARY.csv');print('DRAGS',summary.head(15).to_string());print('CONTRIBUTORS',summary.tail(15).to_string());print('DONE',flush=True)
if __name__=='__main__':main()
