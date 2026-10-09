"""Original Gen1 nine-horizon, pre-heldout training-only freeze; DEV80 only."""
import argparse,json,pathlib,time
import numpy as np,pandas as pd
from Core.layered_ga.ga4_causal_compiler import CausalSignalCompiler
from Core.layered_ga.stage2_evaluator_v3 import evaluate_curve
from Core.layered_ga.stage2_path_v3 import ExecutionPaths,ProspectiveCosts
R=pathlib.Path('Research/Runs/gen1-merit-screen-20261008')
H=(1,2,3,5,7,10,15,20,63)
def run(limit):
 out=R/'original_4360_train_horizon_20261009';out.mkdir(exist_ok=True)
 frame=pd.read_parquet('Research/Runs/layered/stage2-opportunity-v3-20261007/ga4_dev80_checkpoint/dev80_predictors.parquet')
 dates=pd.to_datetime(frame.effective_date)
 train=(dates<'2016-01-01').to_numpy().copy()
 # Require complete 63-session horizon to end before training cutoff.
 cal=pd.Index(sorted(dates.unique()));end=pd.Timestamp('2016-01-01')
 cutoff_pos=int(cal.searchsorted(end));datepos=cal.searchsorted(dates)
 train &= (datepos+63<cutoff_pos)
 assert train.any()
 a=np.load(R/'phaseB_dev80_126_20261009/dev80_execution_arrays_126.npz')
 paths=ExecutionPaths(*(a[k][:,:63] for k in ('endpoint_return','low_excursion','high_excursion','calendar_days')))
 costs=ProspectiveCosts(*(a[k][:,:63] if a[k].ndim==2 else a[k] for k in ('long_roundtrip','short_roundtrip','spread_bps','impact_bps','adv_dollars','regulatory_sell_fraction')))
 compiler=CausalSignalCompiler(frame)
 candidates=[json.loads(s) for s in (R/'all_candidates.jsonl').open()]
 assert len(candidates)==4360
 results=[];start=time.time()
 for i,r in enumerate(candidates[:limit]):
  mask=np.logical_and.reduce([compiler.compile(family,gene) for family,gene in r['chromosomes']]) & train
  pts=evaluate_curve(mask,paths,costs,r['side'],a['cluster_ids'],horizons=H).points
  valid=[p for p in pts if np.isfinite(p.get('lcb95',np.nan))]
  best=max(valid,key=lambda p:(p['lcb95'],-p['horizon'])) if valid else None
  h=int(best['horizon']) if best else None
  results.append({'genome_index':r['index'],'side':r['side'],'horizon':h,
    'status':'TRAIN_ONLY_HORIZON_PROVISIONAL_UNCERTIFIED' if best else 'INSUFFICIENT_TRAIN_SUPPORT',
    'train_lcb95':float(best['lcb95']) if best else None,'train_n':int(best['n']) if best else 0,
    'checkpoints':[c for c in (1,2,3,5,7,10,15,20) if h is not None and c<h]})
  if (i+1)%25==0 or i+1==limit:
   (out/'progress.json').write_text(json.dumps({'done':i+1,'total':limit,'seconds':round(time.time()-start,1)}))
   with (out/'assignments.jsonl').open('w') as w:
    for row in results:w.write(json.dumps(row)+'\n')
 report={'status':'TRAIN_ONLY_HORIZON_ASSIGNMENTS_UNCERTIFIED','genomes_processed':len(results),
 'original_genomes':4360,'original_horizons':H,'training_before':'2016-01-01',
 'purge':'At least 63 market sessions before training cutoff','selection':'max train LCB95 with shorter-horizon tie-break',
 'insufficient_support':sum(r['horizon'] is None for r in results),
 'heldout_used_for_horizon_selection':False,'phase_b_c_intermediate_horizons_used':False,
 'limitations':['Horizon selection still optimized across nine hypotheses; multiplicity adjustment pending',
 'Security-year cluster SE insufficient for common market shock independence',
 'Feature release timing and portfolio replay not certified'],'protected_banks_touched':False}
 (out/'manifest.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--limit',type=int,default=12);run(p.parse_args().limit)
