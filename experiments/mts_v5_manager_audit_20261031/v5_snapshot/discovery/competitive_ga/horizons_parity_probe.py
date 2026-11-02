"""Parity audit against original Horizons strength-mode simulator.
This deliberately removes the manager's 10% cap for like-for-like comparison.
"""
import importlib.util
from pathlib import Path
import numpy as np
from .horizons_daily_adapter import decide
from .horizons_native_score import FEATURES
SRC=Path('/opt/mts/thunder-migration/mts-layered-run-20261007/scripts/run_horizon_free_ga_final_study_20261005.py')

def run():
 spec=importlib.util.spec_from_file_location('horizons_original_parity',SRC)
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 rng=np.random.default_rng(20261027)
 n=20;days=8
 X=rng.uniform(.01,.99,(days,n,len(FEATURES))).astype(np.float64)
 RX=np.zeros((days,n));rf=np.zeros(days)
 genome={'ids':[0,3,8,12],'w':[1.,-.6,.4,.7],'qual':.70,'short':False,'short_qual':.9,'replace_margin':.06,'alloc':'strength','safe_margin':.001}
 _,original,_=mod.simulate(genome,X,RX,rf)
 previous={};largest=0.;mismatches=[]
 for t in range(days-1):
  panel={str(j):dict(zip(FEATURES,X[t,j])) for j in range(n)}
  actions=decide(genome,panel,previous,cap=1.)
  actual=np.array([actions.get(str(j),{}).get('target_weight',0.) for j in range(n)])
  delta=float(np.max(np.abs(actual-original[t])))
  largest=max(largest,delta)
  if delta>1e-10:mismatches.append({'session':t,'max_abs_delta':delta})
  previous={str(j):float(actual[j]) for j in range(n) if actual[j]>0}
 return {'sessions':days-1,'stocks':n,'max_abs_delta':largest,'mismatches':mismatches,'parity':not mismatches}
if __name__=='__main__':print(run())
