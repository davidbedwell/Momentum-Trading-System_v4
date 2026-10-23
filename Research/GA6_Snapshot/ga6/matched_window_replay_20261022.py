"""Re-evaluate frozen unique GA6 candidates on identical 2025-01-01..2026-09-15 data. In-sample comparison only."""
import csv,json,hashlib,collections,pathlib,os
from concurrent.futures import ProcessPoolExecutor
import pandas as pd
from ga5_chromosome_contract import Genome
from ga5_redesign.guarded_evaluator_niche_single_exit import PreparedSessions
from ga6.fast_portfolio_evaluator_20261021 import evaluate as diversity_eval
from ga6.structural_evolution_v3_20261022.structural_portfolio_evaluator import evaluate as structural_eval
from ga6.portfolio_pareto_20261021 import fitness
ROOT=pathlib.Path('/opt/mts');OUT=ROOT/'ga6/runs/post_v3_comparison_20261022';START='2025-01-01';END='2026-09-15'
PREP=None;POLICY=None
def setup(frame,policy):
 global PREP,POLICY
 PREP=PreparedSessions(frame);POLICY=policy
def evaluate(row):
 system,niche,key,definition,prior=row;g=Genome(**definition['genome'] if system=='structural_v3' else definition)
 fn=structural_eval if system=='structural_v3' else diversity_eval
 kw={'blocked':POLICY['blocked'],'membership':POLICY['membership'],'risk_veto':POLICY['risk_veto'],'annual_cash_yield':POLICY['annual_cash_yield']}
 if system=='structural_v3':kw['entry_tree']=definition['entry_tree']
 r=fn(PREP,g,**kw);m=r['ga6_completed_position_metrics']
 return dict(system=system,niche=niche,definition_hash=key,prior_ev_lcb=prior,fitness=fitness(r),completed_trades=m['completed_trades'],win_rate=m.get('win_rate'),avg_sessions=m.get('avg_sessions'),net_ev=m.get('net_ev_entry_equity'),ev_lcb=m.get('net_ev_lower_confidence_95'),cagr=r.get('cagr_diagnostic'),mdd=r.get('mdd_diagnostic'),calmar=r.get('calmar_diagnostic'),period_start=START,period_end_exclusive=END)
def main():
 rows=list(csv.DictReader((OUT/'unique_chromosome_profitability_drawdown.csv').open()));defs={}
 with (OUT/'unique_chromosome_definitions.jsonl').open() as f:
  for line in f:
   x=json.loads(line);defs[(x['system'],x['definition_hash'])]=x['definition']
 chosen=[]
 for system in ('structural_v3','diversity'):
  for niche in sorted({r['niche'] for r in rows if r['system']==system}):
   eligible=[r for r in rows if r['system']==system and r['niche']==niche and r['development_screen']=='PASS']
   eligible.sort(key=lambda r:(-float(r['ev_lcb']),r['definition_hash']))
   for r in eligible[:10]:chosen.append((system,niche,r['definition_hash'],defs[(system,r['definition_hash'])],float(r['ev_lcb'])))
 (OUT/'matched_replay_selection.json').write_text(json.dumps({'window':[START,END],'selection':'Top 10 per system/niche among development-screen passes, ranked by original EV lower confidence bound; no matched-window selection','selected':len(chosen),'counts':dict(collections.Counter(x[0] for x in chosen))},indent=2))
 frame=pd.read_parquet(ROOT/'ga5_redesign/exploratory79_ga4_enriched.parquet');frame=frame[(frame.date>=START)&(frame.date<END)]
 raw=json.loads((ROOT/'ga5_redesign/exploratory79_policy.json').read_text());dates=set(str(x)[:10] for x in frame.date.unique());tickers=set(frame.ticker)
 policy={'membership':{(d,t):v for d,t,v in raw['membership'] if d in dates and t in tickers},'risk_veto':{d:v for d,v in raw['risk_veto'].items() if d in dates},'blocked':{t:frozenset(v) for t,v in raw['blocked'].items()},'annual_cash_yield':raw['cash_proxy_annual_yield']}
 if not chosen:raise RuntimeError('No screened candidates')
 output=OUT/'matched_window_replay.csv';done=set()
 if output.exists():
  with output.open() as f:done={(r['system'],r['definition_hash']) for r in csv.DictReader(f)}
 chosen=[r for r in chosen if (r[0],r[2]) not in done]
 with ProcessPoolExecutor(max_workers=8,initializer=setup,initargs=(frame,policy)) as pool:
  for index,result in enumerate(pool.map(evaluate,chosen),1):
   with output.open('a',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(result));
    if f.tell()==0:w.writeheader()
    w.writerow(result)
   if index%10==0:print('matched replay',index,'/',len(chosen),flush=True)
 print('COMPLETE',len(chosen),flush=True)
if __name__=='__main__':main()
