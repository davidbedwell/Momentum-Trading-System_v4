from __future__ import annotations
import argparse,json,random,time,hashlib
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from Core.g3.realdata import ROOT
from Core.g3.earnings_evidence import build_earnings_index,aligned_evidence_with_earnings
from Core.g3.preregistered_nullgate import NULL_B,NULL_C,guarded_shift_rows,PER_NULL_ALPHA
from Core.g3.v3_protocol import V3Specialist,stationary_bootstrap_y,evaluate_v3
from Core.g3.starter import assert_independent_path,Rule,quality,aggregate_quality_summaries
from scipy.stats import wilcoxon

TICKERS=["AAPL","MSFT","XOM","JPM","JNJ","CAT","WMT","NVDA"]; FAMILIES=["NA_STATIONARY_BOOTSTRAP_Y",NULL_B,NULL_C]; DATA={}
def init_worker(data): global DATA; DATA=data
def score(q): return (-1e9,-1e9,-1e9) if q["n"]<25 else (q["mean"],q["tail"],-q["duration"])
def task(a):
 t,g=a; return quality(evaluate_v3(g,*DATA[t],10))
from Core.g3.v3_search import exact_structural_screen_local

def screen_local(data,pop=48):
 out=[]
 for t,(X,Y) in data.items(): out.extend(exact_structural_screen_local(X,Y,max(1,pop//len(TICKERS))))
 return (out*((pop+len(out)-1)//len(out)))[:pop]
def mutate(g,rng,nf):
 d=g.__dict__.copy(); p=rng.choice(["applicability","gate","signal","side","take_profit","stop_loss","max_horizon","add_at","reduce_at"])
 if p in ("applicability","gate","signal"):
  r=d[p]; d[p]=Rule(r.feature if rng.random()<.7 else rng.randrange(nf),r.threshold+rng.gauss(0,.2),r.direction if rng.random()<.8 else -r.direction)
 elif p=="side": d[p]=-d[p]
 elif p=="max_horizon": d[p]=max(2,min(30,d[p]+rng.choice([-3,-1,1,3])))
 else: d[p]=max(.002,min(.25,d[p]*np.exp(rng.gauss(0,.2))))
 return V3Specialist(**d)
def run_arm(data,seed,workers=60):
 rng=random.Random(seed); nf=next(iter(data.values()))[0].shape[1]; P=screen_local(data,48); led=[]
 with ProcessPoolExecutor(max_workers=workers,initializer=init_worker,initargs=(data,)) as ex:
  for gen in range(6):
   qs=list(ex.map(task,[(t,g) for g in P for t in TICKERS],chunksize=4))
   agg=[aggregate_quality_summaries(qs[i*8:(i+1)*8]) for i in range(48)]
   order=sorted(range(48),key=lambda i:score(agg[i]),reverse=True); valid=[a["mean"] for a in agg if a["n"]>=25]
   led.append(float(np.median(valid))); elite=[P[i] for i in order[:12]]
   P=elite+[mutate(rng.choice(elite),rng,nf) for _ in range(36)]
 return led[-1]
def seed(rep,fam,t):
 return int.from_bytes(hashlib.sha256(f"G3V3|{rep}|{fam}|{t}".encode()).digest()[:8],"big")%(2**32)
def transformed(AX,AY,fam,rep):
 out={}
 for i,t in enumerate(TICKERS):
  x=AX[:,i,:].copy(); y=AY[:,i,:].copy()
  if fam=="NA_STATIONARY_BOOTSTRAP_Y": y=stationary_bootstrap_y(y,seed(rep,fam,t),50)
  elif fam==NULL_B: y=guarded_shift_rows(y,seed(rep,fam,t))
  elif fam==NULL_C: x=guarded_shift_rows(x,seed(rep,fam,t))
  out[t]=(x,y)
 return out
def gate(real,nulls):
 tests=[]
 for fam in FAMILIES:
  d=np.array(real)-np.array(nulls[fam]); stat,p=wilcoxon(d,alternative="greater",zero_method="wilcox",method="auto") if not np.all(d==0) else (0.,1.)
  tests.append({"family":fam,"statistic":float(stat),"pvalue":float(p),"median_paired_difference":float(np.median(d)),"significant":bool(p<PER_NULL_ALPHA)})
 k=sum(x["significant"] for x in tests); state="STRONG_PASS_3_OF_3" if k==3 else ("PASS_2_OF_3" if k==2 else "FAIL_NO_LARGE_DISCOVERY")
 return {"state":state,"significant_nulls":k,"tests":tests}
if __name__=="__main__":
 assert_independent_path(ROOT); ap=argparse.ArgumentParser(); ap.add_argument("--replicates",type=int,default=25);ap.add_argument("--workers",type=int,default=60);a=ap.parse_args()
 ev=build_earnings_index(TICKERS);dates,AX,AY,cols=aligned_evidence_with_earnings(TICKERS,ev);AX=AX[-2500:];AY=AY[-2500:]; rec=[]; t0=time.perf_counter()
 for rep in range(a.replicates):
  for fam in ["REAL",*FAMILIES]:
   data={t:(AX[:,i,:].copy(),AY[:,i,:].copy()) for i,t in enumerate(TICKERS)} if fam=="REAL" else transformed(AX,AY,fam,rep)
   v=run_arm(data,1776000+rep,a.workers);rec.append({"replicate":rep,"arm":fam,"primary":v})
  print("completed",rep+1,"/",a.replicates,flush=True)
 real=[r["primary"] for r in rec if r["arm"]=="REAL"]; nulls={f:[r["primary"] for r in rec if r["arm"]==f] for f in FAMILIES}
 out={"format":"MTS_G3_V3_PREREGISTERED_GATE","complete":len(rec)==a.replicates*4,"replicates":a.replicates,"records":rec,"seconds":time.perf_counter()-t0}
 out["gate_decision"]=gate(real,nulls) if a.replicates==25 and out["complete"] else "WITHHELD"
 Path("Research/G3/MTS_G3_V3_PREREGISTERED_GATE_20261007.json").write_text(json.dumps(out,indent=2)+"\n");print(json.dumps({"seconds":out["seconds"],"gate":out["gate_decision"]},indent=2))
