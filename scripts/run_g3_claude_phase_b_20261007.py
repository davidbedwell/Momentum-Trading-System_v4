from __future__ import annotations
import json, time, random, hashlib
from pathlib import Path
import numpy as np
from concurrent.futures import ProcessPoolExecutor
from Core.g3.realdata import ROOT
from Core.g3.earnings_evidence import build_earnings_index, aligned_evidence_with_earnings
from Core.g3.preregistered_nullgate import apply_frozen_null
from Core.g3.starter import assert_independent_path, Specialist, Rule, evaluate_one, quality
from Core.g3.search_v3 import structural_screen

TICKERS=["NVDA","AAPL","XOM"]; DATA={}
def init_worker(data): global DATA; DATA=data
def score(q): return (-1e9,-1e9,-1e9) if q["n"]<25 else (q["mean"],q["tail"],-q["duration"])
def mutate(g,rng,nf):
 d=g.__dict__.copy(); p=rng.choice(["gate","signal","side","take_profit","stop_loss","max_horizon","add_at","reduce_at"])
 if p in ("gate","signal"):
  r=d[p]; d[p]=Rule(r.feature if rng.random()<.7 else rng.randrange(nf),r.threshold+rng.gauss(0,.2),r.direction if rng.random()<.8 else -r.direction)
 elif p=="side": d[p]=-d[p]
 elif p=="max_horizon": d[p]=max(2,min(30,d[p]+rng.choice([-3,-1,1,3])))
 else: d[p]=max(.002,min(.25,d[p]*np.exp(rng.gauss(0,.2))))
 return Specialist(**d)
def task(a):
 t,g=a; X,Y=DATA[t]; return quality(evaluate_one(g,X,Y,10))
def run_one(t,X,Y,seed,workers=60):
 data={t:(X,Y)}; rng=random.Random(seed); nf=X.shape[1]; P=structural_screen(data,48)
 with ProcessPoolExecutor(max_workers=workers,initializer=init_worker,initargs=(data,)) as ex:
  for _ in range(6):
   qs=list(ex.map(task,[(t,g) for g in P],chunksize=4)); order=sorted(range(48),key=lambda i:score(qs[i]),reverse=True)
   elite=[P[i] for i in order[:12]]; P=elite+[mutate(rng.choice(elite),rng,nf) for _ in range(36)]
 valid=[q["mean"] for q in qs if q["n"]>=25]
 return float(np.median(valid)) if valid else -1e9
def seed(rep,t):
 return int.from_bytes(hashlib.sha256(f"G3-PHASEB-NA|{rep}|{t}".encode()).digest()[:8],"big")%(2**32)
if __name__=="__main__":
 assert_independent_path(ROOT); ev=build_earnings_index(TICKERS); dates,AX,AY,cols=aligned_evidence_with_earnings(TICKERS,ev); AX=AX[-2500:];AY=AY[-2500:]
 out={"format":"MTS_G3_CLAUDE_PHASE_B_NA_VARIANCE","selection_rule":"top 3 Phase-A medians, prospectively specified by Claude","tickers":TICKERS,"replicates":50,"results":{}}
 t0=time.perf_counter()
 for i,t in enumerate(TICKERS):
  vals=[]
  for rep in range(50):
   Xn,Yn=apply_frozen_null(AX[:,i,:],AY[:,i,:],"NA_MOVING_BLOCK_BOOTSTRAP_Y",seed(rep,t))
   vals.append(run_one(t,Xn,Yn,1776000+rep))
  out["results"][t]={"null_primary":vals,"mean":float(np.mean(vals)),"variance":float(np.var(vals,ddof=1)),"sd":float(np.std(vals,ddof=1))}
  print(t,"mean",out["results"][t]["mean"],"sd",out["results"][t]["sd"],flush=True)
 out["seconds"]=time.perf_counter()-t0
 Path("Research/G3/MTS_G3_CLAUDE_PHASE_B_NA_VARIANCE_20261007.json").write_text(json.dumps(out,indent=2)+"\n")
 print("PHASE_B_DONE",round(out["seconds"],2))
