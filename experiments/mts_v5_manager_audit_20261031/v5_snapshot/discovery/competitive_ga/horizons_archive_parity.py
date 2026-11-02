"""Read-only sampled archived Horizons strength-long parity against original simulator.
Synthetic features are for mechanical parity only, not market validation.
"""
import importlib.util,json
from pathlib import Path
import numpy as np
from .legacy_archive_index import iter_strategies
from .horizons_daily_adapter import decide
from .horizons_native_score import FEATURES
SRC=Path('/opt/mts/thunder-migration/mts-layered-run-20261007/scripts/run_horizon_free_ga_final_study_20261005.py')

def run(limit=40):
 spec=importlib.util.spec_from_file_location('horizons_archive_original',SRC)
 original=importlib.util.module_from_spec(spec);spec.loader.exec_module(original)
 rng=np.random.default_rng(20261027);days=12;n=35
 X=rng.uniform(.01,.99,(days,n,len(FEATURES)))
 RX=np.zeros((days,n));rf=np.zeros(days)
 panel=[{str(j):dict(zip(FEATURES,X[t,j])) for j in range(n)} for t in range(days-1)]
 results=[];eligible=0
 for row in iter_strategies('HORIZONS'):
  g=json.loads(row.definition)
  if g['short'] or g['alloc']!='strength':continue
  eligible+=1
  _,reference,_=original.simulate(g,X,RX,rf)
  previous={};delta=0.
  for t,p in enumerate(panel):
   actions=decide(g,p,previous,cap=1.)
   actual=np.asarray([actions.get(str(j),{}).get('target_weight',0.) for j in range(n)])
   delta=max(delta,float(np.max(np.abs(actual-reference[t]))))
   previous={str(j):float(actual[j]) for j in range(n) if actual[j]>0}
  results.append({'id':row.chromosome_id,'max_delta':delta})
  if len(results)>=limit:break
 return {'sampled':len(results),'eligible_encountered':eligible,'max_delta':max((r['max_delta'] for r in results),default=None),'failed':[r for r in results if r['max_delta']>1e-10]}
if __name__=='__main__':print(json.dumps(run(),indent=2))
