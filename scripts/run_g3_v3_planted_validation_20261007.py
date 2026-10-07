from __future__ import annotations
import json,time
from pathlib import Path
import numpy as np
from Core.g3.v3_search import exact_structural_screen_local
from Core.g3.v3_protocol import evaluate_v3
from Core.g3.starter import quality
TICKERS=[f"S{i}" for i in range(8)];ACTIVE=set(TICKERS[:3])
def planted(seed=99173,T=2500,F=17):
 rng=np.random.default_rng(seed);out={}
 for t in TICKERS:
  X=rng.normal(size=(T,F));Y=rng.normal(0,.01,size=(T,10))
  if t in ACTIVE:
   m=(X[:,0]<-1)&(X[:,1]>1);Y[m,:]+=.003
  out[t]=(X,Y)
 return out
if __name__=="__main__":
 data=planted();t0=time.perf_counter();candidates=[]
 for origin in TICKERS:
  for g in exact_structural_screen_local(*data[origin],6): candidates.append((origin,g))
 rec=[]
 for origin,g in candidates:
  per={t:quality(evaluate_v3(g,*data[t],10)) for t in TICKERS}
  av=[per[t]["mean"] for t in ACTIVE if per[t]["n"]>=25];iv=[per[t]["mean"] for t in TICKERS if t not in ACTIVE and per[t]["n"]>=25]
  rec.append({"origin":origin,"genome":repr(g),"active_mean":float(np.mean(av)) if av else -1e9,"inactive_mean":float(np.mean(iv)) if iv else -1e9,"per_stock":per})
 best=max(rec,key=lambda x:x["active_mean"])
 out={"format":"MTS_G3_V3_HETEROGENEOUS_PLANTED_VALIDATION","screen":"EXACT_THREE_RULE_LOCAL_ENUMERATION","complete":True,"ticker_identity_used":False,"criterion_active_mean":.025,"best":best,"pass":bool(best["active_mean"]>=.025),"seconds":time.perf_counter()-t0}
 Path("Research/G3/MTS_G3_V3_HETEROGENEOUS_PLANTED_VALIDATION_20261007.json").write_text(json.dumps(out,indent=2)+"\n")
 print(json.dumps({"pass":out["pass"],"active_mean":best["active_mean"],"inactive_mean":best["inactive_mean"],"seconds":out["seconds"]},indent=2))
