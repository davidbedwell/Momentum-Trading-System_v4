from __future__ import annotations
import json, random, time
from pathlib import Path
import numpy as np
from Core.g3.search_v3 import structural_screen
from Core.g3.starter import evaluate_one, quality

TICKERS=["S0","S1","S2","S3","S4","S5","S6","S7"]
ACTIVE=set(TICKERS[:3])
def planted(seed=99173,T=2500,F=17):
 rng=np.random.default_rng(seed); out={}
 for t in TICKERS:
  X=rng.normal(size=(T,F)); Y=rng.normal(0,.01,size=(T,10))
  if t in ACTIVE:
   m=(X[:,0] < -1.0)&(X[:,1] > 1.0)
   Y[m,:]+=0.003
  out[t]=(X,Y)
 return out
if __name__=="__main__":
 data=planted(); t0=time.perf_counter()
 P=structural_screen(data,48)
 records=[]
 for rank,g in enumerate(P):
  per={}
  for t in TICKERS:
   q=quality(evaluate_one(g,*data[t],10)); per[t]=q
  active=[per[t]["mean"] for t in ACTIVE if per[t]["n"]>=25]
  inactive=[per[t]["mean"] for t in TICKERS if t not in ACTIVE and per[t]["n"]>=25]
  records.append({"rank":rank,"genome":str(g),"active_mean":float(np.mean(active)) if active else -1e9,"inactive_mean":float(np.mean(inactive)) if inactive else -1e9,"per_stock":per})
 best=max(records,key=lambda r:r["active_mean"])
 out={"format":"MTS_G3_CLAUDE_PHASE_C_PLANTED_HETEROGENEITY","active":sorted(ACTIVE),"inactive":[t for t in TICKERS if t not in ACTIVE],"oracle":"feature0<-1 AND feature1>1, long","criterion":"best screened candidate median/mean active-stock event return >= 0.025 requested by Claude","best":best,"pass":best["active_mean"]>=0.025,"seconds":time.perf_counter()-t0}
 Path("Research/G3/MTS_G3_CLAUDE_PHASE_C_PLANTED_HETEROGENEITY_20261007.json").write_text(json.dumps(out,indent=2)+"\n")
 print("ACTIVE_MEAN",best["active_mean"],"INACTIVE_MEAN",best["inactive_mean"],"PASS",out["pass"],"SECONDS",round(out["seconds"],2))
