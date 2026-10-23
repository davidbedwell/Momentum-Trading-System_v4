"""Frozen final GA6-v3 checkpoint 400 DEV87 transport. No optimization or selection on DEV87."""
import json,csv,os,hashlib,traceback
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import pandas as pd
from ga5_redesign.guarded_evaluator_niche_single_exit import PreparedSessions
from ga6.crash_defense_A_v2_adapter import build_revised_daily_state
from ga6.structural_independent_v2_20261022.structural_candidate import StructuralCandidate
from ga6_h.hold_variant_evaluator import evaluate
ROOT=Path('/opt/mts');RUN=ROOT/'ga6/runs/A_v2_full_evolution_20261022'
OUT=ROOT/'ga6_h/audits/ga6v3_400_DEV87_same_period_2019_2024.csv'
START='2019-01-01';END='2025-01-01'
PREP=None;POLICY=None
def setup(frame,policy):
 global PREP,POLICY
 PREP=PreparedSessions(frame);POLICY=policy
def worker(item):
 idx,c=item
 try:
  r=evaluate(PREP,c.genome,entry_tree=c.entry_tree,max_swing_sessions=40,**POLICY)
  m=r['ga6_completed_position_metrics']
  return {'index':idx,'identity':c.identity(),'niche':c.genome.niche,'status':'OK','cagr':r['cagr_diagnostic'],'mdd':r['mdd_diagnostic'],'calmar':r['calmar_diagnostic'],'trades':m['completed_trades'],'win_rate':m.get('win_rate'),'avg_sessions':m.get('avg_sessions'),'net_ev':m.get('net_ev_entry_equity'),'ev_lcb':m.get('net_ev_lower_confidence_95'),'error':''}
 except Exception as e:return {'index':idx,'identity':c.identity(),'niche':c.genome.niche,'status':'ERROR','cagr':'','mdd':'','calmar':'','trades':'','win_rate':'','avg_sessions':'','net_ev':'','ev_lcb':'','error':repr(e)}
def main():
 checkpoint=json.loads((RUN/'structural_checkpoint.json').read_text())
 assert checkpoint['generation']==269 and len(checkpoint['members'])==400
 candidates=[StructuralCandidate.restore(x) for x in checkpoint['members']]
 assert len(set(c.identity() for c in candidates))==400
 dev=ROOT/'thunder-migration/mts-certification-20261011/dev87'
 frame=pd.read_parquet(dev/'dev87_ga6_enriched.parquet')
 frame=frame[(frame.date>=START)&(frame.date<END)]
 raw=json.loads((dev/'dev87_ga6_policy.json').read_text())
 dates=set(str(x)[:10] for x in frame.date.unique());tickers=set(frame.ticker)
 assert len(tickers)==86,(len(tickers),sorted(tickers))
 state=build_revised_daily_state().set_index('date')
 state.index=state.index.strftime('%Y-%m-%d')
 veto={}
 for d in dates:
  i=state.index.get_loc(d)
  assert i>0
  veto[d]=bool(raw['risk_veto'].get(d) is True and not state.iloc[i-1].defensive)
 policy={'membership':{(d,t):v for d,t,v in raw['membership'] if d in dates and t in tickers},'risk_veto':veto,'blocked':{t:frozenset(v) for t,v in raw['blocked'].items()},'annual_cash_yield':raw['cash_proxy_annual_yield']}
 meta={'source':'original GA6-v3 generation 269 final checkpoint','candidate_count':400,'unique_identities':400,'DEV87_tickers':len(tickers),'missing_original_DEV87_ticker':'Q','DEV87_rows':len(frame),'start_inclusive':START,'end_exclusive':END,'defense':'prior session A-v2/B/B1/C/R1 state','fees_bps':10,'holding_cap_sessions':40,'cash_yield':raw['cash_proxy_annual_yield'],'holdout_caveat':'DEV87 exploratory holdout; PIT membership and earnings publication timing not certified','workers':8}
 (OUT.with_suffix('.manifest.json')).write_text(json.dumps(meta,indent=2))
 done=set()
 if OUT.exists():
  with OUT.open() as f:done={int(r['index']) for r in csv.DictReader(f)}
 remaining=[(i,c) for i,c in enumerate(candidates) if i not in done]
 print('PREFLIGHT',json.dumps(meta),'remaining',len(remaining),flush=True)
 if not remaining:return
 with ProcessPoolExecutor(max_workers=8,initializer=setup,initargs=(frame,policy)) as pool:
  futures=[pool.submit(worker,x) for x in remaining]
  for n,f in enumerate(as_completed(futures),1):
   result=f.result()
   with OUT.open('a',newline='') as stream:
    w=csv.DictWriter(stream,fieldnames=list(result))
    if stream.tell()==0:w.writeheader()
    w.writerow(result)
    stream.flush();os.fsync(stream.fileno())
   if n%10==0 or result['status']!='OK':print('PROGRESS',n,'/',len(remaining),result['status'],result['identity'][:10],flush=True)
 print('COMPLETE',OUT,flush=True)
if __name__=='__main__':main()
