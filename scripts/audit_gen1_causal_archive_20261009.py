import json, numpy as np, pandas as pd, time, pathlib
from Core.layered_ga.ga4_causal_compiler import CausalSignalCompiler
from Core.layered_ga.stage2_evaluator_v3 import evaluate_curve
from Core.layered_ga.stage2_path_v3 import ExecutionPaths,ProspectiveCosts
root=pathlib.Path('Research/Runs/gen1-merit-screen-20261008')
out=root/'causal_replay_audit_20261009';out.mkdir(exist_ok=True)
p=pathlib.Path('Research/Runs/layered/stage2-opportunity-v3-20261007/ga4_dev80_checkpoint')
frame=pd.read_parquet(p/'dev80_predictors.parquet');a=np.load(p/'dev80_execution_arrays.npz')
paths=ExecutionPaths(*(a[k] for k in ('endpoint_return','low_excursion','high_excursion','calendar_days')))
costs=ProspectiveCosts(*(a[k] for k in ('long_roundtrip','short_roundtrip','spread_bps','impact_bps','adv_dollars','regulatory_sell_fraction')))
records=[json.loads(s) for s in open(root/'all_candidates.jsonl')]
compiler=CausalSignalCompiler(frame)
horizons=(1,2,3,5,7,10,15,20,63)
# First full nine-horizon cross-family smoke; deterministic, both sides and complex structures.
chosen=[];seen=set()
for r in records:
 k=(tuple(r['families']),r['side'])
 if k not in seen:
  seen.add(k);chosen.append(r)
 if len(chosen)>=80:break
for target in (2733,2159,887,991,1013,1663,1801,2105,2625,3691,3767,4175):
 r=next(x for x in records if x['index']==target)
 if r not in chosen:chosen.append(r)
start=time.time();failed=0;checks=0
with open(out/'comparisons.jsonl','w') as file:
 for i,r in enumerate(chosen):
  mask=np.logical_and.reduce([compiler.compile(f,g) for f,g in r['chromosomes']])
  ev=evaluate_curve(mask,paths,costs,r['side'],a['cluster_ids'],horizons=horizons)
  diffs=[]
  for point,ref in zip(ev.points,r['horizons']):
   checks+=1
   bad=(point['horizon']!=ref['horizon'] or point['n']!=ref['n'] or point['effective_n']!=ref['effective_n'] or not ((point['ev_net'] is None and ref['ev_net'] is None) or (point['ev_net'] is not None and ref['ev_net'] is not None and np.isclose(point['ev_net'],ref['ev_net'],atol=1e-14,rtol=0,equal_nan=True))))
   if bad:diffs.append({'h':point['horizon'],'replay_n':point['n'],'archive_n':ref['n'],'replay_ev':point['ev_net'],'archive_ev':ref['ev_net']})
  failed+=bool(diffs)
  file.write(json.dumps({'index':r['index'],'side':r['side'],'families':r['families'],'passed':not bool(diffs),'diffs':diffs})+'\n');file.flush()
  (out/'progress.json').write_text(json.dumps({'completed':i+1,'total':len(chosen),'checks':checks,'failed_candidates':failed,'elapsed_seconds':round(time.time()-start,1)}))
(out/'result.json').write_text(json.dumps({'status':'PASS' if failed==0 else 'FAIL','tested_candidates':len(chosen),'tested_horizons':len(horizons),'checks':checks,'failed_candidates':failed,'scope':'DEV80 only'},indent=2))
