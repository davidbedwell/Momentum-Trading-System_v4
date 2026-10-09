"""Genome-specific Gen1 matched-path pilot; DEV80 only; never certification."""
import argparse,json,pathlib,time
import numpy as np,pandas as pd
from Core.layered_ga.ga4_causal_compiler import CausalSignalCompiler
from Core.layered_ga.gen1_path_study_split import validate_assignment,split_mask
from Core.layered_ga.gen1_horizon_path_labels import labels
from Core.layered_ga.gen1_path_matching import matched_failure_scores,select_threshold
ROOT=pathlib.Path('Research/Runs/gen1-merit-screen-20261008')
A=ROOT/'original_4360_train_horizon_20261009'
F='Research/Runs/layered/stage2-opportunity-v3-20261007/ga4_dev80_checkpoint/dev80_predictors.parquet'
FEATURES=['return_5__v1','return_20__v1','close_to_sma_50__v1','close_to_sma_200__v1','breadth_above_sma_200__v1']
def run(limit,neighbors):
 start=time.time()
 assignments=[json.loads(x) for x in (A/'assignments.jsonl').open()]
 candidates={x['index']:x for x in map(json.loads,(ROOT/'all_candidates.jsonl').open())}
 f=pd.read_parquet(F);dates=pd.to_datetime(f.effective_date)
 calendar=pd.DatetimeIndex(sorted(dates.unique()))
 train=split_mask(dates,calendar,end='2016-01-01',purge=63)
 cal=split_mask(dates,calendar,begin='2016-07-15',end='2020-06-01',purge=63)
 test=split_mask(dates,calendar,begin='2021-01-01',purge=63)
 assert not (train&cal).any() and not (cal&test).any()
 arr=np.load(ROOT/'phaseB_dev80_126_20261009/dev80_execution_arrays_126.npz',mmap_mode='r')
 endpoint=arr['endpoint_return'][:,:63]
 key=pd.MultiIndex.from_arrays([f.security_id.to_numpy(),dates.to_numpy()])
 if not key.is_unique:raise ValueError('Duplicate security/date PIT rows')
 bykey=f.set_index(key)[FEATURES]
 pos=calendar.searchsorted(dates)
 compiler=CausalSignalCompiler(f)
 out=ROOT/'matched_horizon_v4_20261009';out.mkdir(exist_ok=True)
 rows=[];pred=[]
 for a in assignments[:limit]:
  cps=validate_assignment(a);h=a['horizon'];idx=a['genome_index']
  if h is None or not cps:
   rows.append({'genome_index':idx,'horizon':h,'status':'NO_SUPPORTED_CHECKPOINT'});continue
  genome=candidates[idx];side=genome['side']
  mask=np.logical_and.reduce([compiler.compile(family,gene) for family,gene in genome['chromosomes']])
  cost=arr['long_roundtrip'] if side=='LONG' else arr['short_roundtrip']
  if cost.ndim==1:cost=np.repeat(cost[:,None],63,axis=1)
  else:cost=cost[:,:63]
  for c in cps:
   outcome=labels(endpoint,cost,side,h,c)
   # At T+1+c open, T+c closing features are historical, never terminal outcomes.
   shifted=pos+c;safe=np.minimum(shifted,len(calendar)-1)
   aligned=pd.MultiIndex.from_arrays([f.security_id.to_numpy(),calendar.take(safe)])
   context=bykey.reindex(aligned).to_numpy(dtype=float).copy()
   context[shifted>=len(calendar)]=np.nan
   features=np.column_stack([outcome['checkpoint_net'],context[:,0]*(1 if side=='LONG' else -1),
     context[:,1]*(1 if side=='LONG' else -1),context[:,2:],np.full(len(f),c,dtype=float)])
   valid=mask&outcome['distressed']&np.isfinite(features).all(axis=1)
   tr=np.flatnonzero(valid&train);ca=np.flatnonzero(valid&cal);te=np.flatnonzero(valid&test)
   rec={'genome_index':idx,'side':side,'horizon':h,'checkpoint':c,'train_n':len(tr),'cal_n':len(ca),'test_n':len(te)}
   # A failure is terminal net <=0, learned exclusively from training terminal outcomes.
   y=(outcome['terminal_net']<=0).astype(int)
   if len(tr)<neighbors or len(ca)<30 or len(te)<20 or len(np.unique(y[tr]))<2:
    rec['status']='INSUFFICIENT_MATCH_SUPPORT';rows.append(rec);continue
   try:
    cr=matched_failure_scores(features[tr],y[tr],features[ca],neighbors)
    threshold=select_threshold(cr['failure_probability'],y[ca])
    result=matched_failure_scores(features[tr],y[tr],features[te],neighbors)
   except ValueError:
    rec['status']='MATCH_ABSTAIN';rows.append(rec);continue
   for event_id,prob,dist in zip(te,result['failure_probability'],result['mean_neighbor_distance']):
    pred.append({'genome_index':idx,'side':side,'horizon':h,'checkpoint':c,
     'event_id':int(event_id),'decision_date':str(dates.iloc[event_id].date()),
     'failure_probability':float(prob),'baseline_probability':result['baseline_probability'],
     'failure_outcome':int(y[event_id]),'mean_neighbor_distance':float(dist),
     'calibration_threshold':threshold,'terminal_net':float(outcome['terminal_net'][event_id]),
     'checkpoint_net':float(outcome['checkpoint_net'][event_id])})
   rec.update(status='HELDOUT_DIAGNOSTIC_UNCERTIFIED',threshold=threshold,baseline=result['baseline_probability'])
   rows.append(rec)
  if len(rows)%25==0:
   (out/'progress.json').write_text(json.dumps({'rows':len(rows),'genomes_seen':idx,'elapsed':round(time.time()-start,1)}))
 with (out/'results.jsonl').open('w') as w:
  for r in rows:w.write(json.dumps(r)+'\n')
 pd.DataFrame(pred).to_parquet(out/'heldout_event_predictions.parquet',index=False)
 report={'status':'GENOME_SPECIFIC_MATCHED_PATH_PILOT_UNCERTIFIED','assignments_available':len(assignments),
  'genomes_processed':min(limit,len(assignments)),'diagnostics':sum(r['status']=='HELDOUT_DIAGNOSTIC_UNCERTIFIED' for r in rows),
  'predictions':len(pred),'scope':'DEV80','protected_banks_touched':False,
  'limitations':['Feature release timestamp lineage not verified','Selection multiplicity and independent episode validation pending',
   'Trade policy and portfolio replay not certified','Open-to-open endpoint path only']}
 (out/'manifest.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--limit',type=int,default=12);p.add_argument('--neighbors',type=int,default=25)
 a=p.parse_args();run(a.limit,a.neighbors)
