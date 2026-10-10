#!/usr/bin/env python3
"""Sequential four-window LONG-only stop-policy screening; six parallel CPU workers per window.
Research pilot, NOT four genetically evolving entry GAs or stop-fill certification.
"""
import argparse,concurrent.futures,json,os,pathlib,time
import numpy as np,pandas as pd
from Core.layered_ga.ga4_causal_compiler import CausalSignalCompiler
R=pathlib.Path('Research/Runs/gen1-merit-screen-20261008')
F=pathlib.Path('Research/Runs/layered/stage2-opportunity-v3-20261007/ga4_dev80_checkpoint/dev80_predictors.parquet')
OUT=R/'four_window_frontier_stop_pilot_20261009'
WINDOWS=[(2,5),(6,10),(11,15),(16,20)]
POLICIES=[('hold',0.,0.),('fixed_close',-.02,0.),('fixed_close',-.04,0.),('fixed_close',-.06,0.),('trailing_close',0.,.025),('trailing_close',0.,.05),('trailing_close',0.,.08),('time_fail',0.,0.)]

def worker(job):
 lo,hi,indices=job
 os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
 f=pd.read_parquet(F);dates=pd.to_datetime(f.effective_date).to_numpy()
 a=np.load(R/'phaseB_dev80_126_20261009/dev80_execution_arrays_126.npz')
 e=a['endpoint_return'][:,:hi];cost=a['long_roundtrip'][:,:hi]
 catalog={r['index']:r for r in map(json.loads,(R/'all_candidates.jsonl').open())}
 compiler=CausalSignalCompiler(f);results=[]
 for idx in indices:
  genome=catalog[idx]
  if genome['side']!='LONG':continue
  entry=np.logical_and.reduce([compiler.compile(family,gene) for family,gene in genome['chromosomes']])
  valid=np.cumprod((np.isfinite(e)&np.isfinite(cost)).astype(np.int8),axis=1).astype(bool)
  for horizon in range(lo,hi+1):
   ids=np.flatnonzero(entry&valid[:,horizon-1])
   tr=ids[dates[ids]<np.datetime64('2016-01-01')];te=ids[dates[ids]>=np.datetime64('2021-01-01')]
   if len(tr)<40 or len(te)<20:continue
   if len(tr)>500:tr=tr[np.linspace(0,len(tr)-1,500,dtype=int)]
   if len(te)>500:te=te[np.linspace(0,len(te)-1,500,dtype=int)]
   def realize(rows,policy):
    name,level,trail=policy;paths=e[rows,:horizon];cs=cost[rows,:horizon];peak=np.maximum.accumulate(paths,axis=1)
    if name=='hold':hit=np.zeros_like(paths,dtype=bool)
    elif name=='fixed_close':hit=paths<=level
    elif name=='trailing_close':hit=(peak-paths)>=trail
    else:hit=(paths<=0)&(np.arange(horizon)[None,:]>=max(1,horizon//2))
    # Endpoint is an executable next-open return proxy; act at following observation, never same observation.
    shifted=np.zeros_like(hit);shifted[:,1:]=hit[:,:-1]
    ix=np.where(shifted.any(axis=1),shifted.argmax(axis=1),horizon-1)
    return paths[np.arange(len(rows)),ix]-cs[np.arange(len(rows)),ix],ix
   scores=[]
   for policy in POLICIES:
    values,_=realize(tr,policy)
    scores.append(float(np.mean(values)+min(0.,np.quantile(values,.05))*.25))
   best=int(np.argmax(scores));trv,_=realize(tr,POLICIES[best]);tev,ex=realize(te,POLICIES[best]);base,_=realize(te,POLICIES[0])
   results.append({'genome':idx,'horizon':horizon,'train_events':len(tr),'test_events':len(te),'selected_policy':POLICIES[best],'train_objective':scores[best],'test_mean_net':float(np.mean(tev)),'test_hold_mean_net':float(np.mean(base)),'test_delta_vs_hold':float(np.mean(tev-base)),'test_early_exit_rate':float(np.mean(ex<horizon-1))})
 return results

def main():
 p=argparse.ArgumentParser();p.add_argument('--workers',type=int,default=6);p.add_argument('--genomes-per-window',type=int,default=24);args=p.parse_args()
 if args.workers!=6:raise ValueError('Frozen request: exactly six workers')
 OUT.mkdir(parents=True,exist_ok=True)
 frontier=[r for r in map(json.loads,(R/'horizon_grouped_pareto_20261009/ranked_memberships.jsonl').open()) if r['side']=='LONG' and r['phase']=='refined' and r['ev_net']>0]
 for lo,hi in WINDOWS:
  dest=OUT/f'window_{lo:02d}_{hi:02d}.json'
  eligible=[r for r in frontier if lo<=r['horizon']<=hi]
  eligible.sort(key=lambda r:(r['pareto_rank'], -r['lcb95'], -r['ev_net']))
  selected=[];seen=set()
  for r in eligible:
   if r['index'] not in seen:
    selected.append(r['index']);seen.add(r['index'])
   if len(selected)>=args.genomes_per_window:break
  if not selected:raise RuntimeError(f'No eligible positive-EV refined frontier genomes for {lo}-{hi}')
  # Frontier-ranked candidate selection, rather than uniform sampling of all genomes.
  chunks=[selected[i::6] for i in range(6)];start=time.time()
  print('START',lo,hi,'workers',6,'genomes',len(selected),flush=True)
  with concurrent.futures.ProcessPoolExecutor(max_workers=6) as pool:
   parts=list(pool.map(worker,[(lo,hi,chunk) for chunk in chunks]))
  results=[x for part in parts for x in part]
  report={'status':'UNCERTIFIED_STOP_POLICY_SCREEN','window':[lo,hi],'six_workers':True,'long_only':True,'selected_genomes':selected,'frontier_eligible_memberships':len(eligible),'selection_rule':'Refined LONG positive preliminary EV; horizon in window; ascending provisional Pareto rank then descending lower confidence bound; distinct genome index','evaluated_genome_horizon_pairs':len(results),'elapsed_seconds':round(time.time()-start,1),'results':results,'limitations':['Not a genetically evolving entry GA; exploratory frontier-selected stop screening','Daily endpoint proxy, not executable intraday stop-loss fills or overnight gap handling','Same candidate set and overlapping episodes; no independent inference','Chronological test not independent across market episodes','Unadjusted multiple policy and horizon search','No capital-constrained portfolio replay','No protected partitions accessed']}
  dest.write_text(json.dumps(report,indent=2)+'\n');print('COMPLETE',lo,hi,'pairs',len(results),'seconds',report['elapsed_seconds'],flush=True)
 print('ALL_FOUR_COMPLETE',flush=True)
if __name__=='__main__':main()
