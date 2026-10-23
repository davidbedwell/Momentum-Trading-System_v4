import json,csv,os,sys,hashlib,traceback
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import numpy as np,pandas as pd
from ga5_redesign.guarded_evaluator_niche_single_exit import PreparedSessions
from ga6.crash_defense_A_v2_adapter import build_revised_daily_state
from ga6.structural_independent_v2_20261022.structural_candidate import StructuralCandidate
from ga6_h.hold_variant_evaluator import evaluate
ROOT=Path('/opt/mts');OUT=ROOT/'ga6_h/audits';START='2019-01-01';END='2025-01-01';PREP=None;POLICY=None
sources={'DEV79':('ga5_redesign/exploratory79_ga4_enriched.parquet','ga5_redesign/exploratory79_policy.json'),'DEV87':('thunder-migration/mts-certification-20261011/dev87/dev87_ga6_enriched.parquet','thunder-migration/mts-certification-20261011/dev87/dev87_ga6_policy.json'),'DEV50b':('ga6_h/dev50b/DEV50b_enriched.parquet','ga6_h/dev50b/DEV50b_policy.json')}
def setup(frame,policy):
 global PREP,POLICY
 PREP=PreparedSessions(frame);POLICY=policy
def worker(item):
 i,c=item
 try:
  r=evaluate(PREP,c.genome,entry_tree=c.entry_tree,max_swing_sessions=40,allocation_audit=True,**POLICY)
  m=r['ga6_completed_position_metrics'];a=r['allocation_audit'];trades=a['completed'];marks=a['marks'];t=pd.DataFrame(trades);mark=pd.DataFrame(marks)
  # Trade-level return field discovery is recorded rather than silently assumed.
  return {'index':i,'identity':c.identity(),'niche':c.genome.niche,'status':'OK','trades':m['completed_trades'],'win_rate':m.get('win_rate'),'net_ev':m.get('net_ev_entry_equity'),'ev_lcb':m.get('net_ev_lower_confidence_95'),'avg_sessions':m.get('avg_sessions'),'cagr':r['cagr_diagnostic'],'mdd':r['mdd_diagnostic'],'trade_columns':'|'.join(t.columns),'trade_ledger':json.dumps(trades,default=str,separators=(',',':')),'avg_invested_weight':float(mark.groupby('date').weight.sum().mean()) if len(mark) else 0.0,'error':''}
 except Exception as e:return {'index':i,'identity':c.identity(),'niche':c.genome.niche,'status':'ERROR','error':repr(e)}
def main():
 checkpoint=json.loads((ROOT/'ga6/runs/A_v2_full_evolution_20261022/structural_checkpoint.json').read_text());assert checkpoint['generation']==269 and len(checkpoint['members'])==400
 cs=[StructuralCandidate.restore(z) for z in checkpoint['members']];assert len(set(c.identity() for c in cs))==400
 state=build_revised_daily_state().set_index('date');state.index=state.index.strftime('%Y-%m-%d')
 frames={};policies={}
 for name,(f,p) in sources.items():
  frame=pd.read_parquet(ROOT/f);frame=frame[(frame.date>=START)&(frame.date<END)].copy();frames[name]=frame;policies[name]=json.loads((ROOT/p).read_text())
  print('SOURCE',name,len(frame),frame.ticker.nunique(),flush=True)
 assert not(set(frames['DEV79'].ticker)&set(frames['DEV87'].ticker))
 assert not(set(frames['DEV50b'].ticker)&(set(frames['DEV79'].ticker)|set(frames['DEV87'].ticker)))
 for name in ['DEV79','DEV87','DEV79_DEV87','DEV50b']:
  frame=pd.concat([frames['DEV79'],frames['DEV87']],ignore_index=True) if name=='DEV79_DEV87' else frames[name]
  rawlist=[policies['DEV79'],policies['DEV87']] if name=='DEV79_DEV87' else [policies[name]]
  dates=set(frame.date.dt.strftime('%Y-%m-%d'));tickers=set(frame.ticker)
  member={(d,t):v for raw in rawlist for d,t,v in raw['membership'] if d in dates and t in tickers}
  blocked={t:frozenset(v) for raw in rawlist for t,v in raw['blocked'].items()}
  veto={d:bool(all(raw['risk_veto'].get(d) is True for raw in rawlist) and not state.iloc[state.index.get_loc(d)-1].defensive) for d in dates}
  policy={'membership':member,'blocked':blocked,'risk_veto':veto,'annual_cash_yield':0.03}
  path=OUT/('GA6v3_400_'+name+'_trade_ledger_2019_2024.csv');done=set()
  if path.exists():
   with path.open() as f:done={int(r['index']) for r in csv.DictReader(f)}
  remaining=[(i,c) for i,c in enumerate(cs) if i not in done]
  print('START',name,'remaining',len(remaining),'tickers',len(tickers),flush=True)
  if not remaining:continue
  with ProcessPoolExecutor(max_workers=8,initializer=setup,initargs=(frame,policy)) as pool:
   futures=[pool.submit(worker,item) for item in remaining]
   for n,future in enumerate(as_completed(futures),1):
    row=future.result();fields=['index','identity','niche','status','trades','win_rate','net_ev','ev_lcb','avg_sessions','cagr','mdd','trade_columns','trade_ledger','avg_invested_weight','error']
    with path.open('a',newline='') as stream:
     writer=csv.DictWriter(stream,fieldnames=fields,extrasaction='ignore')
     if stream.tell()==0:writer.writeheader()
     writer.writerow(row);stream.flush()
    if n%20==0 or row['status']!='OK':print('PROGRESS',name,n,'/',len(remaining),row['status'],flush=True)
  print('FINISHED',name,flush=True)
if __name__=='__main__':main()
