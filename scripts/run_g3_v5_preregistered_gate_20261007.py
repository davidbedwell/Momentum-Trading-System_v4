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
def run_local_ticker(train,valid,seed0,nf):
 rng=random.Random(seed0);P=exact_structural_screen_local(*train,48)
 for gen in range(6):
  qs=[quality(evaluate_v3(g,*train,10)) for g in P]
  order=sorted(range(48),key=lambda i:score(qs[i]),reverse=True);elite=[P[i] for i in order[:12]]
  if gen<5:P=elite+[mutate(rng.choice(elite),rng,nf) for _ in range(36)]
 qs=[quality(evaluate_v3(g,*valid,10)) for g in P]
 vals=[q['mean'] for q in qs if q['n']>=25]
 return (float(np.median(vals)) if vals else None),len(vals)

def _local_job(arg):
 t,train,valid,seed0,nf=arg;v,n=run_local_ticker(train,valid,seed0,nf);return t,v,n

def run_arm(data,seed,workers=60):
 nf=next(iter(data.values()))[0].shape[1];n=min(len(v[0]) for v in data.values());cut=int(n*.70);vstart=cut+10
 jobs=[]
 for ti,t in enumerate(TICKERS):
  X,Y=data[t];jobs.append((t,(X[:cut],Y[:cut]),(X[vstart:],Y[vstart:]),seed+ti*100003,nf))
 with ProcessPoolExecutor(max_workers=min(workers,len(jobs))) as ex: res=list(ex.map(_local_job,jobs))
 vals=[v for _,v,_ in res if v is not None]
 endpoint={'viable_stock_count':len(vals),'median_viable_return':float(np.median(vals)) if vals else None}
 return endpoint,{t:{'endpoint':v,'valid_candidates':n} for t,v,n in res}

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
def _cmp_endpoint(real,null):
 rc,nc=real['viable_stock_count'],null['viable_stock_count']
 if rc!=nc:return (1 if rc>nc else -1),'viability'
 if rc==0:return 0,'tie'
 rr,nr=real['median_viable_return'],null['median_viable_return']
 if rr==nr:return 0,'tie'
 return (1 if rr>nr else -1),'return'

def _exact_sign_p(wins,n):
 from math import comb
 if n<=0:return 1.0
 return sum(comb(n,k) for k in range(wins,n+1))/(2**n)

def gate(real,nulls):
 tests=[]
 for fam in FAMILIES:
  outcomes=[_cmp_endpoint(r,n) for r,n in zip(real,nulls[fam])]
  wins=sum(c>0 for c,_ in outcomes);losses=sum(c<0 for c,_ in outcomes);ties=sum(c==0 for c,_ in outcomes);nt=wins+losses;p=_exact_sign_p(wins,nt)
  tests.append({'family':fam,'real_wins':wins,'null_wins':losses,'ties':ties,'non_tied_pairs':nt,'pvalue':float(p),'significant':bool(p<PER_NULL_ALPHA),'decided_by_viability':sum(reason=='viability' for _,reason in outcomes),'decided_by_return':sum(reason=='return' for _,reason in outcomes)})
 k=sum(x['significant'] for x in tests);state='STRONG_PASS_3_OF_3' if k==3 else ('PASS_2_OF_3' if k==2 else 'FAIL_NO_LARGE_DISCOVERY')
 return {'state':state,'significant_nulls':k,'tests':tests}

if __name__=="__main__":
 assert_independent_path(ROOT); ap=argparse.ArgumentParser(); ap.add_argument("--replicates",type=int,default=25);ap.add_argument("--workers",type=int,default=60);a=ap.parse_args()
 ev=build_earnings_index(TICKERS);dates,AX,AY,cols=aligned_evidence_with_earnings(TICKERS,ev);AX=AX[-2500:];AY=AY[-2500:]; rec=[]; t0=time.perf_counter()
 for rep in range(a.replicates):
  for fam in ["REAL",*FAMILIES]:
   data={t:(AX[:,i,:].copy(),AY[:,i,:].copy()) for i,t in enumerate(TICKERS)} if fam=="REAL" else transformed(AX,AY,fam,rep)
   v,detail=run_arm(data,1776000+rep,a.workers);rec.append({"replicate":rep,"arm":fam,"primary":v,"ticker_detail":detail})
  print("completed",rep+1,"/",a.replicates,flush=True)
 real=[r["primary"] for r in rec if r["arm"]=="REAL"]; nulls={f:[r["primary"] for r in rec if r["arm"]==f] for f in FAMILIES}
 out={"format":"MTS_G3_V5_PREREGISTERED_GATE","complete":len(rec)==a.replicates*4,"replicates":a.replicates,"records":rec,"seconds":time.perf_counter()-t0}
 out["gate_decision"]=gate(real,nulls) if a.replicates==25 and out["complete"] else "WITHHELD"
 Path("Research/G3/MTS_G3_V5_PREREGISTERED_GATE_20261007.json").write_text(json.dumps(out,indent=2)+"\n");print(json.dumps({"seconds":out["seconds"],"gate":out["gate_decision"]},indent=2))
