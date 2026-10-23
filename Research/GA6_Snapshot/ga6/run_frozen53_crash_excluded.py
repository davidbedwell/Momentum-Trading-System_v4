"""Retrospective oracle crash exclusion: keep all dates and cash accrual, force flat during two known crash cycles. Not prospective."""
import json,pathlib,concurrent.futures
import pandas as pd
from ga5_chromosome_contract import Genome
from ga5_redesign.guarded_evaluator_niche_single_exit import PreparedSessions
from ga6.research_exit_replay_evaluator import evaluate
R=pathlib.Path('/opt/mts');S=R/'ga6/runs/post_v3_comparison_20261022';O=R/'ga6/runs/certification_gate_20261022';F=None;P=None;D=None
WINDOWS=[('2006_2010','2006-01-01','2011-01-01','2007-10-09','2009-03-09'),('2016_2020','2016-01-01','2021-01-01','2020-02-19','2020-03-23')]
def setup(frame,policy,defs):
 global F,P,D
 F=PreparedSessions(frame);P=policy;D=defs
def run(key):
 d=D[key];r=evaluate(F,Genome(**d['genome']),entry_tree=d['entry_tree'],**P);m=r['ga6_completed_position_metrics'];return {'hash':key,'cagr':r['cagr_diagnostic'],'mdd':r['mdd_diagnostic'],'trades':m['completed_trades'],'win_rate':m.get('win_rate'),'avg_sessions':m.get('avg_sessions'),'ev':m.get('net_ev_entry_equity'),'nav':r['final_nav']}
def main():
 rank=pd.read_csv(S/'dev87_53_survivors_ranked.csv');keys=set(rank.definition_hash);defs={}
 for line in (S/'unique_chromosome_definitions.jsonl').open():
  j=json.loads(line)
  if j.get('system')=='structural_v3' and j.get('definition_hash') in keys:defs[j['definition_hash']]=j['definition']
 assert len(defs)==53
 frame=pd.read_parquet(R/'ga5_redesign/exploratory79_ga4_enriched.parquet');raw=json.loads((R/'ga5_redesign/exploratory79_policy.json').read_text());tickers=set(frame.ticker)
 (O/'CRASH_EXCLUSION_METHOD.json').write_text(json.dumps({'mode':'RETROSPECTIVE_ORACLE_NOT_TRADABLE','windows':WINDOWS,'method':'Retain all calendar sessions; override risk_veto=False on historical peak-to-trough inclusive; next-open liquidation; cash earns baseline proxy; no lookahead claim','comparison':'Original FROZEN53 files with same periods and candidates','caveat':'Peak/trough dates only knowable retrospectively; gap losses on first excluded day can occur'},indent=2))
 for name,start,end,peak,trough in WINDOWS:
  out=O/('CRASH_EXCLUDED_'+name+'.csv');done=set(pd.read_csv(out)['hash']) if out.exists() else set();todo=sorted(keys-done);f=frame[(frame.date>=start)&(frame.date<end)];dates=set(str(x)[:10] for x in f.date.unique());veto={d:(False if peak<=d<=trough else v) for d,v in raw['risk_veto'].items() if d in dates};policy={'membership':{(d,t):v for d,t,v in raw['membership'] if d in dates and t in tickers},'risk_veto':veto,'blocked':{t:frozenset(v) for t,v in raw['blocked'].items()},'annual_cash_yield':raw['cash_proxy_annual_yield']}
  print('START',name,'PENDING',len(todo),'CRASH',peak,trough,'BLOCKED',sum(peak<=d<=trough for d in dates),flush=True)
  with concurrent.futures.ProcessPoolExecutor(max_workers=8,initializer=setup,initargs=(f,policy,defs)) as pool:
   for i,result in enumerate(pool.map(run,todo),1):
    pd.DataFrame([result]).to_csv(out,mode='a',header=not out.exists(),index=False)
    if i%10==0:print('PROGRESS',name,i,'/',len(todo),flush=True)
  a=pd.read_csv(out).set_index('hash');b=pd.read_csv(O/('FROZEN53_'+name+'.csv')).set_index('hash');z=a.join(b,lsuffix='_excluded',rsuffix='_original');print('RESULT',name,'MEDIAN_CAGR',a.cagr.median(),'MEDIAN_MDD',a.mdd.median(),'MEDIAN_CAGR_DELTA_PP',((z.cagr_excluded-z.cagr_original)*100).median(),'MEDIAN_MDD_DELTA_PP',((z.mdd_excluded-z.mdd_original)*100).median(),'IMPROVED_CAGR',int((z.cagr_excluded>z.cagr_original).sum()),'IMPROVED_MDD',int((z.mdd_excluded>z.mdd_original).sum()),flush=True)
 print('FINISHED',flush=True)
if __name__=='__main__':main()
