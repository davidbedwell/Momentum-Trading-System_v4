"""Isolated checkpoint/restart structural GA diagnostic; never touches production."""
import argparse,base64,hashlib,json,pickle,random,os
from pathlib import Path
import pandas as pd
from ga5_redesign.niche_seeds import initial
from ga5_redesign.optimizer_v3 import NICHES
from ga5_redesign.guarded_evaluator_niche_single_exit import PreparedSessions
from ga6.structural_independent_v2_20261022.structural_population import random_tree,propose_structural
from ga6.structural_independent_v2_20261022.discovery_allocation import Observation,ACTIVITIES
from ga6.structural_independent_v2_20261022.structural_candidate import StructuralCandidate
from ga6.structural_independent_v2_20261022.structural_batch import StructuralBatch
from ga5_redesign.canonical_engine import digest_file

def run(argv=None):
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--generations',type=int,default=2);p.add_argument('--population',type=int,default=400);p.add_argument('--workers',type=int,default=8);p.add_argument('--start',default='2025-01-01');p.add_argument('--end',default='2025-04-01');a=p.parse_args(argv)
 if a.population<26 or a.generations<1 or not 1<=a.workers<=len(os.sched_getaffinity(0)):raise ValueError('Invalid diagnostic budget or workers')
 if a.population<260:print('WARNING: population below 260 can leave fewer than half the slots for exploration after 130 protected niche elites',flush=True)
 root=Path('/opt/mts');out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
 source=root/'ga5_redesign/exploratory79_ga4_enriched.parquet';policypath=root/'ga5_redesign/exploratory79_policy.json'
 frame=pd.read_parquet(source);frame=frame[(frame.date>=a.start)&(frame.date<a.end)]
 if frame.empty:raise ValueError('No data')
 prepared=PreparedSessions(frame);policy_json=json.loads(policypath.read_text())
 policy={'membership':{(d,t):v for d,t,v in policy_json['membership'] if d in prepared.dates},'risk_veto':{d:v for d,v in policy_json['risk_veto'].items() if d in prepared.dates},'blocked':{t:frozenset(v) for t,v in policy_json['blocked'].items()},'annual_cash_yield':policy_json['cash_proxy_annual_yield']}
 # GA6 A-v2 defense overlay: defensive declaration after close D affects next session open D+1.
 from ga6.crash_defense_A_v2_adapter import build_revised_daily_state
 from ga5_redesign.canonical_engine import digest_file as _hash
 updated=build_revised_daily_state()
 updated.to_csv(root/'ga6/data/crash_defense_A_v2/STATE_TAPE_HISTORICAL.csv',index=False)
 state=updated.set_index('date')
 state.index=state.index.strftime('%Y-%m-%d')
 trading_dates=sorted(prepared.dates)
 missing=set(trading_dates)-set(state.index)
 if missing:raise ValueError('Crash defense missing dates: '+str(sorted(missing)[:5]))
 defensive=state.defensive.to_dict()
 previous=None
 for day in trading_dates:
  # First session uses the preceding completed market session, not its own close.
  idx=state.index.get_loc(day)
  if idx==0:raise ValueError('No prior crash-defense state for '+day)
  prev=state.iloc[idx-1]
  # Combine with existing policy, never turn an existing veto into permission.
  policy['risk_veto'][day]=bool(policy['risk_veto'][day] is True and not prev.defensive)
 crash_hash=_hash(root/'ga6/data/crash_defense_A_v2/STATE_TAPE_HISTORICAL.csv')

 modules=('structural_runner_A_v2.py','structural_batch.py','structural_candidate.py','structural_population.py','structural_portfolio_evaluator.py','structural_decision.py','family_logic.py','discovery_allocation.py','development_feedback_ledger.py')
 code=hashlib.sha256(''.join(digest_file(Path(__file__).parent/n) for n in modules).encode()).hexdigest()
 fingerprint=hashlib.sha256(json.dumps([digest_file(source),digest_file(policypath),crash_hash,code,a.population,a.start,a.end]).encode()).hexdigest()
 checkpoint=out/'structural_checkpoint.json';rng=random.Random(6106);generation=0
 if checkpoint.exists():
  state=json.loads(checkpoint.read_text())
  if state['fingerprint']!=fingerprint:raise ValueError('Checkpoint fingerprint mismatch')
  generation=state['generation'];rng.setstate(pickle.loads(base64.b64decode(state['rng'])));members=[StructuralCandidate.restore(x) for x in state['members']];origins=state['origins']
 else:
  members=[StructuralCandidate(initial(n),random_tree(rng)) for n in NICHES for _ in range(2)];origins=['new_structures']*len(members)
 batch=StructuralBatch(out,digest_file(source)+a.start+a.end,digest_file(policypath)+crash_hash,code)
 try:
  while generation<a.generations:
   scored=batch.evaluate(members,prepared,policy,generation,origins,workers=a.workers)
   scored.sort(key=lambda x:(-x[0],x[1].identity()))
   summary={'generation':generation+1,'evaluations':len(scored),'distinct':len({c.identity() for _,c,_ in scored}),'best_exploratory_fitness':scored[0][0],'completed_trades':sum(r['ga6_completed_position_metrics']['completed_trades'] for _,_,r in scored),'buys':sum(r['signal_trace']['executed_buys'] for _,_,r in scored)}
   per_niche={}
   for niche in NICHES:
    group=[(score,result) for score,c,result in scored if c.genome.niche==niche]
    trades=sum(result['ga6_completed_position_metrics']['completed_trades'] for _,result in group)
    session_sum=sum((result['ga6_completed_position_metrics']['avg_sessions'] or 0)*result['ga6_completed_position_metrics']['completed_trades'] for _,result in group)
    per_niche[niche]={'evaluated':len(group),'best_fitness':max(score for score,_ in group),'completed_trades':trades,'avg_sessions_per_trade':round(session_sum/trades,2) if trades else None}
   summary['per_niche']=per_niche
   # Write only after proposal, so allocation metadata matches the checkpoint.
   activity_counts={a:0 for a in ACTIVITIES}
   activity_novel={a:0 for a in ACTIVITIES}
   for candidate,activity in zip(members,origins):
    if activity in activity_counts:activity_counts[activity]+=1
   for activity in ACTIVITIES:
    activity_novel[activity]=len({c.identity() for c,origin in zip(members,origins) if origin==activity})
   # No fabricated compute-cost estimates: retain baseline allocation until measured feedback exists.
   observations=None
   members,info=propose_structural(scored,rng,a.population,generation+1,observations=observations)
   summary['next_allocation']=info['counts']
   origins=info['origins'];generation+=1
   state={'fingerprint':fingerprint,'generation':generation,'rng':base64.b64encode(pickle.dumps(rng.getstate())).decode(),'members':[c.checkpoint() for c in members],'origins':origins}
   temp=checkpoint.with_suffix('.tmp');temp.write_text(json.dumps(state));temp.replace(checkpoint)
   report=out/f'generation_{generation:04d}.json';report_tmp=report.with_suffix('.tmp');report_tmp.write_text(json.dumps(summary,indent=2));report_tmp.replace(report)
   print(json.dumps(summary),flush=True)
 finally:batch.close()
if __name__=='__main__':run()
