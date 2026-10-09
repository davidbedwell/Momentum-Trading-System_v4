"""DEV80-only fine-grained horizon audit for 168 provisional parents; no selection or promotion."""
import json,time,pathlib,numpy as np,pandas as pd
from Core.layered_ga.ga4_causal_compiler import CausalSignalCompiler
from Core.layered_ga.stage2_evaluator_v3 import evaluate_curve
from Core.layered_ga.stage2_path_v3 import ExecutionPaths,ProspectiveCosts
root=pathlib.Path('Research/Runs/gen1-merit-screen-20261008')
out=root/'phaseC_parent_study_20261009';out.mkdir(exist_ok=True)
phase=root/'phaseB_dev80_126_20261009'
assert json.loads((phase/'manifest.json').read_text())['status']=='OUTCOME_EXTENSION_BUILT_NOT_CERTIFIED'
parents=[json.loads(x) for x in open(root/'horizon_grouped_pareto_20261009/provisional_168_priority.jsonl')]
assert len(parents)==168 and len({r['index'] for r in parents})==168
records={r['index']:r for r in (json.loads(x) for x in open(root/'all_candidates.jsonl'))}
f=pd.read_parquet('Research/Runs/layered/stage2-opportunity-v3-20261007/ga4_dev80_checkpoint/dev80_predictors.parquet')
a=np.load(phase/'dev80_execution_arrays_126.npz')
paths=ExecutionPaths(*(a[k] for k in ('endpoint_return','low_excursion','high_excursion','calendar_days')))
costs=ProspectiveCosts(*(a[k] for k in ('long_roundtrip','short_roundtrip','spread_bps','impact_bps','adv_dollars','regulatory_sell_fraction')))
compiler=CausalSignalCompiler(f)
horizons=tuple(range(1,127))
started=time.time()
with open(out/'results.jsonl','w') as file:
 for i,parent in enumerate(parents):
  r=records[parent['index']]
  mask=np.logical_and.reduce([compiler.compile(family,genome) for family,genome in r['chromosomes']])
  points=evaluate_curve(mask,paths,costs,r['side'],a['cluster_ids'],horizons=horizons).points
  file.write(json.dumps({'index':r['index'],'side':r['side'],'allocation_window':parent['allocation_window'],'points':points},allow_nan=True)+'\n');file.flush()
  (out/'progress.json').write_text(json.dumps({'completed':i+1,'total':168,'elapsed_seconds':round(time.time()-started,1),'status':'RUNNING_UNCERTIFIED'}))
(out/'manifest.json').write_text(json.dumps({'status':'PHASE_C_FULL_HORIZON_CURVE_COMPLETE_UNCERTIFIED','candidate_count':168,'horizons':horizons,'scope':'DEV80 only','no_parent_selection_changes':True},indent=2))
