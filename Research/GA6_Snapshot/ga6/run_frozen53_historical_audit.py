"""Frozen GA6 bank historical regime audit; NOT independent OOS certification."""
import json,pathlib,concurrent.futures,hashlib
import pandas as pd
from ga5_chromosome_contract import Genome
from ga5_redesign.guarded_evaluator_niche_single_exit import PreparedSessions
from ga6.research_exit_replay_evaluator import evaluate
R=pathlib.Path('/opt/mts');S=R/'ga6/runs/post_v3_comparison_20261022';O=R/'ga6/runs/certification_gate_20261022';PREP=None;POLICY=None;DEFS=None
WINDOWS=[('2006_2010','2006-01-01','2011-01-01'),('2011_2015','2011-01-01','2016-01-01'),('2016_2020','2016-01-01','2021-01-01'),('2021_2024','2021-01-01','2025-01-01')]
def setup(f,p,defs):
 global PREP,POLICY,DEFS
 PREP=PreparedSessions(f);POLICY=p;DEFS=defs
def run(key):
 d=DEFS[key];r=evaluate(PREP,Genome(**d['genome']),entry_tree=d['entry_tree'],**POLICY);m=r['ga6_completed_position_metrics'];return {'hash':key,'cagr':r['cagr_diagnostic'],'mdd':r['mdd_diagnostic'],'trades':m['completed_trades'],'win_rate':m.get('win_rate'),'avg_sessions':m.get('avg_sessions'),'ev':m.get('net_ev_entry_equity'),'nav':r['final_nav'],'reconciliation_error':r['reconciliation']['cash_flow_nav_error']}
def main():
 O.mkdir(parents=True,exist_ok=True);rank=pd.read_csv(S/'dev87_53_survivors_ranked.csv');keys=set(rank.definition_hash);defs={}
 for line in (S/'unique_chromosome_definitions.jsonl').open():
  j=json.loads(line)
  if j.get('system')=='structural_v3' and j.get('definition_hash') in keys:defs[j['definition_hash']]=j['definition']
 assert len(defs)==53,(len(defs),len(keys))
 f=pd.read_parquet(R/'ga5_redesign/exploratory79_ga4_enriched.parquet');raw=json.loads((R/'ga5_redesign/exploratory79_policy.json').read_text());tickers=set(f.ticker)
 (O/'FREEZE_MANIFEST.json').write_text(json.dumps({'candidate_count':len(defs),'candidate_hashes':sorted(defs),'definition_sha256':hashlib.sha256((S/'unique_chromosome_definitions.jsonl').read_bytes()).hexdigest(),'feature_source':'ga5_redesign/exploratory79_ga4_enriched.parquet','historical_windows':WINDOWS,'status':'RETROSPECTIVE_RESEARCH_NOT_BLIND','selector':'NONE; individual chromosome diagnostics only','engine':'ga6.research_exit_replay_evaluator.evaluate','position_cap_sessions':40},indent=2))
 for name,start,end in WINDOWS:
  out=O/('FROZEN53_'+name+'.csv');done=set(pd.read_csv(out)['hash']) if out.exists() else set();todo=sorted(keys-done);frame=f[(f.date>=start)&(f.date<end)];dates=set(str(x)[:10] for x in frame.date.unique());policy={'membership':{(d,t):v for d,t,v in raw['membership'] if d in dates and t in tickers},'risk_veto':{d:v for d,v in raw['risk_veto'].items() if d in dates},'blocked':{t:frozenset(v) for t,v in raw['blocked'].items()},'annual_cash_yield':raw['cash_proxy_annual_yield']}
  print('WINDOW',name,'PENDING',len(todo),'SESSIONS',len(dates),flush=True)
  if todo:
   with concurrent.futures.ProcessPoolExecutor(max_workers=8,initializer=setup,initargs=(frame,policy,defs)) as pool:
    for i,result in enumerate(pool.map(run,todo),1):
     pd.DataFrame([result]).to_csv(out,mode='a',header=not out.exists(),index=False)
     if i%10==0:print('PROGRESS',name,i,'/',len(todo),flush=True)
  a=pd.read_csv(out);print('RESULT',name,'COUNT',len(a),'MEDIAN_CAGR',a.cagr.median(),'MEDIAN_MDD',a.mdd.median(),'POSITIVE',int((a.cagr>0).sum()),'MEDIAN_TRADES',a.trades.median(),flush=True)
 print('FINISHED',O,flush=True)
if __name__=='__main__':main()
