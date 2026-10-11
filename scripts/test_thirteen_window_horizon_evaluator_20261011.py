#!/usr/bin/env python3
"""Non-evolutionary DEV80 2..65 evaluator horizon coverage and causal input smoke."""
import json,pathlib,sys,numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from Core.layered_ga.stage2_path_v3 import ExecutionPaths,ProspectiveCosts
from Core.layered_ga.stage2_evaluator_v3 import evaluate_curve
P=ROOT/'Research/Runs/gen1-merit-screen-20261008/phaseB_dev80_126_20261009/dev80_execution_arrays_126.npz'
D=np.load(P)
paths=ExecutionPaths(*(D[k] for k in ('endpoint_return','low_excursion','high_excursion','calendar_days')))
costs=ProspectiveCosts(*(D[k] for k in ('long_roundtrip','short_roundtrip','spread_bps','impact_bps','adv_dollars','regulatory_sell_fraction')))
assert paths.endpoint_return.shape[1]>=65
assert costs.long_roundtrip.shape==paths.endpoint_return.shape
assert costs.short_roundtrip.shape==paths.endpoint_return.shape
assert len(D['cluster_ids'])==len(paths.endpoint_return)
for h in range(2,66):
 assert np.count_nonzero(np.isfinite(paths.endpoint_return[:,h-1]) & np.isfinite(costs.long_roundtrip[:,h-1]))>1000,(h,'no viable forward data')
# Tiny deterministic arrays isolate evaluator's horizon indexing; no full DEV80 replay.
n=220;H=65
p=ExecutionPaths(np.tile(np.arange(1,H+1,dtype=float)/100,(n,1)),np.full((n,H),-.02),np.full((n,H),.04),np.ones((n,H),dtype=np.int16))
c=ProspectiveCosts(np.full((n,H),.001),np.full((n,H),.001),np.zeros(n),np.zeros(n),np.ones(n),np.zeros(n))
ids=np.arange(n,dtype=np.int32)
r=evaluate_curve(np.ones(n,dtype=bool),p,c,'LONG',ids,min_raw_n=200,min_effective_n=20,horizons=tuple(range(2,66)))
assert [x['horizon'] for x in r.points]==list(range(2,66))
for x in r.points:
 assert x['n']==n and abs(x['ev_net']-(x['horizon']/100-.001))<1e-10,x
print(json.dumps({'status':'PASS_HORIZON_COVERAGE_ONLY','horizons':[2,65],'n_horizons':64,'dev80_rows':len(paths.endpoint_return),'synthetic_evaluator_points':len(r.points)}))
