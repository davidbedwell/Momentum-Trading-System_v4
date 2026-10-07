from __future__ import annotations
import json,time,random,argparse
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from Core.g3.realdata import ROOT
from Core.g3.earnings_evidence import build_earnings_index,evidence_arrays_with_earnings,aligned_evidence_with_earnings
from Core.g3.controls import apply_single_ticker_null,apply_aligned_n2
from Core.g3.starter import *
TICKERS=["AAPL","MSFT","XOM","JPM","JNJ","CAT","WMT","NVDA"]
DATA={}
def init_worker(data): global DATA;DATA=data
def score(q): return (-1e9,-1e9,-1e9) if q["n"]<25 else (q["mean"],q["tail"],-q["duration"])
def mutate(g,rng,nf):
 d=g.__dict__.copy();p=rng.choice(["gate","signal","side","take_profit","stop_loss","max_horizon","add_at","reduce_at"])
 if p in ("gate","signal"):
  r=d[p];d[p]=Rule(r.feature if rng.random()<.7 else rng.randrange(nf),r.threshold+rng.gauss(0,.2),r.direction if rng.random()<.8 else -r.direction)
 elif p=="side":d[p]=-d[p]
 elif p=="max_horizon":d[p]=max(2,min(30,d[p]+rng.choice([-3,-1,1,3])))
 else:d[p]=max(.002,min(.25,d[p]*np.exp(rng.gauss(0,.2))))
 return Specialist(**d)
def task(a):
 t,g,fam,seed,rows=a;X,Y=DATA[t];X=X[-rows:];Y=Y[-rows:]
 if fam:Y=apply_single_ticker_null(Y,fam,seed)
 return quality(evaluate_one(g,X,Y,10))
def arm(name,fam,data,generations,pop,workers,rows,seed):
 rng=random.Random(seed);nf=next(iter(data.values()))[0].shape[1];P=[random_specialist(rng,nf) for _ in range(pop)];led=[];t0=time.perf_counter()
 with ProcessPoolExecutor(max_workers=workers,initializer=init_worker,initargs=(data,)) as ex:
  for gen in range(generations):
   tasks=[(t,g,fam,(seed+gen*100000+i*100+j),rows) for i,g in enumerate(P) for j,t in enumerate(TICKERS)]
   qs=list(ex.map(task,tasks,chunksize=4));agg=[aggregate_quality_summaries(qs[i*8:(i+1)*8]) for i in range(pop)]
   order=sorted(range(pop),key=lambda i:score(agg[i]),reverse=True);elite=[P[i] for i in order[:max(4,pop//4)]]
   led.append({"generation":gen+1,"best":agg[order[0]],"median_mean":float(np.median([x["mean"] for x in agg if x["mean"]>-1e8]))})
   P=elite+[mutate(rng.choice(elite),rng,nf) for _ in range(pop-len(elite))]
 return {"arm":name,"generations":generations,"population":pop,"ticker_evaluations":generations*pop*8,"seconds":time.perf_counter()-t0,"ledger":led}
def n2_data(events,seed):
 dates,X,Y,cols=aligned_evidence_with_earnings(TICKERS,events);Yn=apply_aligned_n2(Y,seed)
 return {t:(X[:,i,:],Yn[:,i,:]) for i,t in enumerate(TICKERS)}
if __name__=="__main__":
 ap=argparse.ArgumentParser();ap.add_argument("--workers",type=int,default=60);ap.add_argument("--generations",type=int,default=6);ap.add_argument("--population",type=int,default=48);ap.add_argument("--rows",type=int,default=2500);a=ap.parse_args()
 assert_independent_path(ROOT);start=time.perf_counter();events=build_earnings_index(TICKERS)
 dates,AX,AY,cols=aligned_evidence_with_earnings(TICKERS,events)
 realdata={t:(AX[:,i,:],AY[:,i,:]) for i,t in enumerate(TICKERS)}
 arms=[arm("real",None,realdata,a.generations,a.population,a.workers,a.rows,1776)]
 arms.append(arm("N1_TEMPORAL_BLOCK","N1_TEMPORAL_BLOCK",realdata,a.generations,a.population,a.workers,a.rows,1776))
 n2Y=apply_aligned_n2(AY,2776); n2data={t:(AX[:,i,:],n2Y[:,i,:]) for i,t in enumerate(TICKERS)}
 arms.append(arm("N2_DATEWISE_CROSS_SECTION",None,n2data,a.generations,a.population,a.workers,a.rows,1776))
 arms.append(arm("N3_GUARDED_SHIFT","N3_GUARDED_SHIFT",realdata,a.generations,a.population,a.workers,a.rows,1776))
 ev=[x["ticker_evaluations"] for x in arms]
 out={"format":"MTS_G3_MATCHED_N1_N2_N3_GATE_PILOT_V2_ALIGNED","status":"PILOT_ONLY_THRESHOLD_NOT_FROZEN","workers":a.workers,"tickers":TICKERS,"rows":a.rows,"arms":arms,"matched_budget":len(set(ev))==1,"total_seconds":time.perf_counter()-start,"production_authorized":False}
 Path("Research/G3/MTS_G3_MATCHED_N1_N2_N3_GATE_PILOT_V2_ALIGNED_20261007.json").write_text(json.dumps(out,indent=2)+"\n")
 print(json.dumps({"total_seconds":out["total_seconds"],"matched_budget":out["matched_budget"],"arms":[{"arm":x["arm"],"seconds":x["seconds"],"final":x["ledger"][-1]} for x in arms]},indent=2))
