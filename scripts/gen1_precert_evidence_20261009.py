"""Precert evidence: clustered predictive tests, matched-path labels, observability audit.
Fail closed; no claim of trading-policy certification or access to protected banks.
"""
import json,pathlib,hashlib
import numpy as np,pandas as pd
ROOT=pathlib.Path('Research/Runs/gen1-merit-screen-20261008')
OUT=ROOT/'matched_winner_loser_checkpoint_v3_20261009'
def main():
 p=pd.read_parquet(OUT/'heldout_event_predictions.parquet')
 f=pd.read_parquet('Research/Runs/layered/stage2-opportunity-v3-20261007/ga4_dev80_checkpoint/dev80_predictors.parquet',columns=['security_id','effective_date'])
 a=np.load(ROOT/'phaseB_dev80_126_20261009/dev80_execution_arrays_126.npz',mmap_mode='r')
 assert len(f)==a['endpoint_return'].shape[0]
 assert p.event_id.between(0,len(f)-1).all()
 assert not p.duplicated(['genome_index','checkpoint','event_id']).any()
 dates=pd.to_datetime(p.decision_date)
 p['year']=dates.dt.year
 p['quarter']=dates.dt.to_period('Q').astype(str)
 p['gain']=(p.baseline_probability-p.failure_outcome)**2-(p.failure_probability-p.failure_outcome)**2
 p['abs_calibration_error']=abs(p.failure_probability-p.failure_outcome)
 rng=np.random.default_rng(20261009)
 tests={}
 for label,grp in [('quarter',p.groupby('quarter').gain.mean()),('year',p.groupby('year').gain.mean())]:
  v=grp.to_numpy();boots=rng.choice(v,size=(5000,len(v)),replace=True).mean(axis=1)
  tests[label]={'blocks':len(v),'mean_block_gain':float(v.mean()),'ci95':list(map(float,np.quantile(boots,[.025,.975]))),'positive_blocks':int(np.sum(v>0))}
 # Count duplicate market events to avoid presenting trade rows as independent samples.
 per_event=p.groupby('event_id').gain.mean()
 # Evaluate counterfactual outcome paths with no future inputs: labels ONLY.
 sample=p[['event_id','checkpoint','genome_index','failure_outcome']].copy()
 unique=sample.drop_duplicates(['event_id','checkpoint'])
 ix=unique.event_id.to_numpy(dtype=int);cp=unique.checkpoint.to_numpy(dtype=int)
 terminal=a['endpoint_return'][ix,19]
 at_cp=a['endpoint_return'][ix,cp-1]
 at_20=np.isfinite(terminal)
 continued=terminal-at_cp
 path={'distinct_event_checkpoint_pairs':len(unique),'finite_terminal_paths':int(at_20.sum()),
       'continued_positive_gross_fraction':float(np.mean(continued[np.isfinite(continued)]>0)),
       'checkpoint_to_20_delta_quantiles':list(map(float,np.nanquantile(continued,[.1,.5,.9]))),
       'interpretation':'Entry-notional gross change, outcome-only; NOT direction-adjusted or net policy PnL'}
 # Features timestamp semantics: exact close-T observations used at open T+1+c.
 # Data source does not supply verified release/availability timestamps.
 provenance={'checkpoint_mapping':'decision T close, checkpoint exit open T+1+c; predictor date T+c close',
 'data_has_verified_release_timestamps':False,'observability_certified':False,
 'action':'Require feature-by-feature data dictionary and release/latency evidence; exclude unverified inputs before policy certification'}
 result={'status':'PRECERT_EVIDENCE_BUILT_CERTIFICATION_BLOCKED','genomes':int(p.genome_index.nunique()),
 'heldout_predictions':len(p),'unique_market_events':int(p.event_id.nunique()),
 'distinct_genome_event_pairs':int(p[['genome_index','event_id']].drop_duplicates().shape[0]),
 'brier_gain_per_prediction':float(p.gain.mean()),'cluster_tests':tests,
 'per_market_event_mean_gain':float(per_event.mean()),
 'genome_gain':{str(k):float(v) for k,v in p.groupby('genome_index').gain.mean().items()},
 'path_label_diagnostic':path,'timing_provenance':provenance,
 'unresolved':['verified release-time provenance','competing recovery/failure labels and competing-risk fitting',
 'market-episode segmentation beyond calendar blocks','economic policy replay with portfolio CAGR/MDD',
 'full 4360-genome multiplicity-adjusted out-of-training comparison'],
 'no_parent_selection_changes':True,'protected_banks_touched':False}
 (OUT/'precert_evidence.json').write_text(json.dumps(result,indent=2))
 print(json.dumps({k:v for k,v in result.items() if k not in ('genome_gain',)},indent=2))
if __name__=='__main__':main()
