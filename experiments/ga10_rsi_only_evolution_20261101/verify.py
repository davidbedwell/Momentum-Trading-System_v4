"""Independent terminal artifact and accounting audit, no optimization."""
from pathlib import Path
import json,hashlib
import numpy as np
import pandas as pd
from study import ROOT,load,arrays,simulate
import prototype
checks={}
d=load();a=arrays(d,'2009-01-01','2013-12-31')
# Baseline shares and next-open fee accounting cross-check with original Python engine.
m,path,_,_=simulate(np.zeros(53),*a,1)
ref,frame,_=prototype.run(d,'2009-01-01','2013-12-31',baseline='rsi')
np.testing.assert_allclose(path[:,0],frame.nav.to_numpy(),rtol=1e-10,atol=1e-11)
checks['baseline_independent_python_nav_parity']=True
# Missing optional predictors may not veto an eligible entry.
prior=np.ones((2,1));x=np.full((2,1,6),np.nan);screen=np.ones((2,1),bool);monthly=np.array([True,False]);g=np.zeros(53);g[0]=1;g[27]=-1;g[18]=-1;g[9]=-1
_,_,count,_=simulate(g,prior,prior,prior,x,screen,monthly)
assert count[0]>0;checks['no_optional_feature_eligibility_gate']=True
if (ROOT/'terminal.json').exists():
 s=json.loads((ROOT/'terminal.json').read_text());cp=json.loads((ROOT/'checkpoint.json').read_text());gen=pd.read_csv(ROOT/'generations.csv');cand=pd.read_csv(ROOT/'candidates.csv')
 assert len(gen)==s['completed']<=1000;assert len(cand)==len(gen)*64
 assert gen.generation.tolist()==list(range(1,len(gen)+1));stale=0
 for row in gen.itertuples():
  stale=0 if row.meaningful_improvement else stale+1
  assert row.stagnant==stale
 assert len(gen)==1000 or stale>=100
 assert len(cp['pop'])==64
 checks['generation_count_and_stagnation']=True
 front=json.loads((ROOT/'frontier.json').read_text());champ=json.loads((ROOT/'champions.json').read_text())
 for z in front:np.testing.assert_allclose(simulate(np.array(z['g']),*a)[0],z['m'],rtol=1e-12)
 checks['frontier_replay']=True
 f=pd.read_csv(ROOT/'frontier.csv')
 for i,z in f.iterrows():
  dominated=(f.cagr>=z.cagr)&(f.mdd<=z.mdd)&(f.calmar>=z.calmar)&((f.cagr>z.cagr)|(f.mdd<z.mdd)|(f.calmar>z.calmar))
  assert not dominated.any()
 checks['nondominated_frontier']=True
 feasible=cand[cand.mdd<.25]
 if len(feasible):assert abs(champ['feasible_cagr']['m'][0]-feasible.cagr.max())<1e-12
 checks['champion_maximum_feasible_cagr']=True
 for file in ROOT.glob('*_events.csv'):
  e=pd.read_csv(file)
  if len(e):assert e.loc[e.action=='entry','in_screen'].all(),file
 checks['all_new_entries_screened']=True
 for file in ROOT.glob('*_daily.csv'):
  z=pd.read_csv(file);nav=z.nav.to_numpy();marks=np.r_[1.,nav];dd=np.max(1-marks/np.maximum.accumulate(marks))
  assert (z.exposure>=-1e-9).all() and (z.exposure<=1+1e-9).all()
 checks['saved_daily_paths_exposure']=True
 prov=json.loads((ROOT/'provenance.json').read_text());assert prov['code_sha256']==hashlib.sha256((ROOT/'study.py').read_bytes()).hexdigest()
 checks['source_hash']=True
 (ROOT/'verification.json').write_text(json.dumps(checks,indent=2))
else:
 (ROOT/'preflight_verification.json').write_text(json.dumps(checks,indent=2))
print(json.dumps(checks,indent=2))
