"""Archived Horizons signed strength/uncertainty/downside parity to causal patch."""
import json,importlib.util
import numpy as np
from .legacy_archive_index import iter_strategies
from .horizons_native_score import FEATURES
from .horizons_full_math import targets
SRC='/opt/mts/horizons_causal_patch.py'

def run(limit=100):
 # Import only corrected() body to avoid executing module-level archive scan.
 from pathlib import Path
 source=Path(SRC).read_text();body=source[source.index('def corrected('):source.index('def test():')]
 scope={'np':np};exec(body,scope);corrected=scope['corrected']
 rng=np.random.default_rng(20261027);days=10;n=24
 X=rng.uniform(.01,.99,(days,n,len(FEATURES)));RX=rng.normal(0,.01,(days,n));rf=np.zeros(days)
 panels=[{str(j):dict(zip(FEATURES,X[t,j])) for j in range(n)} for t in range(days-1)]
 output=[]
 for row in iter_strategies('HORIZONS'):
  g=json.loads(row.definition)
  _,ref,_=corrected(g,X,RX,rf)
  prev={};worst=0.
  for t,p in enumerate(panels):
   result=targets(g,p,prev,cap=1.,prior_returns=RX[max(0,t-20):t])
   actual=np.array([result.get(str(j),0.) for j in range(n)])
   worst=max(worst,float(np.max(np.abs(actual-ref[t]))))
   prev=result
  output.append((row.chromosome_id,g['alloc'],bool(g['short']),worst))
  if len(output)>=limit:break
 return {'tested':len(output),'by_mode':{mode:sum(r[1]==mode for r in output) for mode in ('strength','uncertainty','downside')},'short_enabled':sum(r[2] for r in output),'max_delta':max((r[3] for r in output),default=None),'failures':[r for r in output if r[3]>1e-10][:8]}
if __name__=='__main__':print(run())
