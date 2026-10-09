import json, numpy as np,pandas as pd
from Core.layered_ga.ga4_causal_compiler import CausalSignalCompiler as VectorSignalCompiler
from Core.layered_ga.stage2_evaluator_v3 import evaluate_curve
from Core.layered_ga.stage2_path_v3 import ExecutionPaths,ProspectiveCosts
p='Research/Runs/layered/stage2-opportunity-v3-20261007/ga4_dev80_checkpoint/'
f=pd.read_parquet(p+'dev80_predictors.parquet')
a=np.load(p+'dev80_execution_arrays.npz')
paths=ExecutionPaths(*(a[k] for k in ['endpoint_return','low_excursion','high_excursion','calendar_days']))
costs=ProspectiveCosts(*(a[k] for k in ['long_roundtrip','short_roundtrip','spread_bps','impact_bps','adv_dollars','regulatory_sell_fraction']))
compiler=VectorSignalCompiler(f)
records=[json.loads(x) for x in open('Research/Runs/gen1-merit-screen-20261008/all_candidates.jsonl')]
for r in [records[0],records[1],records[2],next(x for x in records if x['index']==2733)]:
 masks=[compiler.compile(fam,g) for fam,g in r['chromosomes']]
 mask=np.logical_and.reduce(masks)
 ev=evaluate_curve(mask,paths,costs,r['side'],a['cluster_ids'],horizons=(1,3,7,20,63))
 comparisons=[]
 for x in ev.points:
  ref=next(z for z in r['horizons'] if z['horizon']==x['horizon'])
  comparisons.append({'horizon':x['horizon'],'n_replay':x['n'],'n_archived':ref['n'],'ev_replay':x['ev_net'],'ev_archived':ref['ev_net'],'ev_delta':x['ev_net']-ref['ev_net'],'cluster_replay':x['effective_n'],'cluster_archived':ref['effective_n']})
 print(json.dumps({'index':r['index'],'side':r['side'],'comparisons':comparisons}),flush=True)
