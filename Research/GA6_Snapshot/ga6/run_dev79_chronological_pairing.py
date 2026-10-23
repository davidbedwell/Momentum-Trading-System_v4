import json,pathlib,concurrent.futures
import pandas as pd
from ga5_chromosome_contract import Genome
from ga5_redesign.guarded_evaluator_niche_single_exit import PreparedSessions
from ga6.research_exit_replay_evaluator import evaluate
R=pathlib.Path('/opt/mts');S=R/'ga6/runs/post_v3_comparison_20261022';O=R/'ga6/runs/independent_review';FRAME=None;POLICY=None;DEFS=None

def setup(f,p,defs):
 global FRAME,POLICY,DEFS
 FRAME=PreparedSessions(f);POLICY=p;DEFS=defs

def run(job):
 key,t=job;d=DEFS[key];p=dict(POLICY)
 if t!='__BASELINE__':p['membership']={k:(v and k[1]!=t) for k,v in POLICY['membership'].items()}
 r=evaluate(FRAME,Genome(**d['genome']),entry_tree=d['entry_tree'],**p)
 return {'hash':key,'excluded_ticker':t,'cagr':r['cagr_diagnostic'],'mdd':r['mdd_diagnostic'],'trades':r['ga6_completed_position_metrics']['completed_trades'],'nav':r['final_nav']}

def main():
 baseline=pd.read_csv(O/'DEV79_CLAUDE_CONTROLLED_REPLAYS.csv');keys=set(baseline.loc[baseline.scenario=='baseline','hash']);defs={}
 for line in (S/'unique_chromosome_definitions.jsonl').open():
  j=json.loads(line)
  if j.get('system')=='structural_v3' and j.get('definition_hash') in keys:defs[j['definition_hash']]=j['definition']
 allframe=pd.read_parquet(R/'ga5_redesign/exploratory79_ga4_enriched.parquet');raw=json.loads((R/'ga5_redesign/exploratory79_policy.json').read_text());tickers=sorted(allframe.ticker.unique());jobs=[(k,t) for k in sorted(defs) for t in ['__BASELINE__']+tickers]
 for name,start,end in [('train2025','2025-01-01','2026-01-01'),('test2026','2026-01-01','2026-09-15')]:
  out=O/('DEV79_PAIRING_'+name+'.csv');done=set()
  if out.exists():
   old=pd.read_csv(out);done=set(zip(old['hash'],old['excluded_ticker']))
  todo=[j for j in jobs if j not in done];f=allframe[(allframe.date>=start)&(allframe.date<end)];dates=set(str(x)[:10] for x in f.date.unique());p={'membership':{(d,t):v for d,t,v in raw['membership'] if d in dates and t in tickers},'risk_veto':{d:v for d,v in raw['risk_veto'].items() if d in dates},'blocked':{t:frozenset(v) for t,v in raw['blocked'].items()},'annual_cash_yield':raw['cash_proxy_annual_yield']}
  print('START',name,'JOBS',len(todo),'SESSIONS',len(dates),flush=True)
  with concurrent.futures.ProcessPoolExecutor(max_workers=8,initializer=setup,initargs=(f,p,defs)) as pool:
   chunk=[]
   for i,result in enumerate(pool.map(run,todo,chunksize=1),1):
    chunk.append(result)
    if len(chunk)>=80 or i==len(todo):
     pd.DataFrame(chunk).to_csv(out,mode='a',index=False,header=not out.exists());chunk=[];print('PROGRESS',name,len(done)+i,'/',len(jobs),flush=True)
  print('COMPLETE',name,out,flush=True)
 a=pd.read_csv(O/'DEV79_PAIRING_train2025.csv');b=pd.read_csv(O/'DEV79_PAIRING_test2026.csv')
 def effects(df):
  z=df[df.excluded_ticker=='__BASELINE__'][['hash','cagr']].rename(columns={'cagr':'base_cagr'});v=df[df.excluded_ticker!='__BASELINE__'].merge(z,on='hash');v['contribution']=v.base_cagr-v.cagr;return v[['hash','excluded_ticker','contribution']]
 x=effects(a).rename(columns={'contribution':'train_contribution'});y=effects(b).rename(columns={'contribution':'test_contribution'});v=x.merge(y,on=['hash','excluded_ticker']);v['train_positive']=v.train_contribution>0;v['test_positive']=v.test_contribution>0;v.to_csv(O/'DEV79_PAIRING_CHRONOLOGICAL_VALIDATION.csv',index=False)
 selected=v[v.train_contribution>0];negative=v[v.train_contribution<0];print('SUMMARY',json.dumps({'pairs':len(v),'train_positive':len(selected),'test_positive_rate_of_train_positive':float(selected.test_positive.mean()),'train_negative':len(negative),'test_positive_rate_of_train_negative':float(negative.test_positive.mean()),'all_test_positive_rate':float(v.test_positive.mean()),'train_test_contribution_corr':float(v.train_contribution.corr(v.test_contribution))}),flush=True)
 print('TOP_STOCKS',selected.groupby('excluded_ticker').agg(train_positive=('train_positive','sum'),test_positive_rate=('test_positive','mean'),test_median_contribution=('test_contribution','median')).sort_values('test_positive_rate',ascending=False).head(20).to_string(),flush=True)
if __name__=='__main__':main()
