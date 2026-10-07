from __future__ import annotations
import argparse,json,time,random,hashlib
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from Core.g3.realdata import evidence_arrays,ROOT
from Core.g3.starter import *
TICKERS=["AAPL","MSFT","XOM","JPM","JNJ","CAT","WMT","NVDA"]
def key(g): return repr(g)
def score(q):
    if q["n"]<25:return (-1e9,-1e9,-1e9)
    return (q["mean"],q["tail"],-q["duration"])
def mutate(g,rng,nf):
    d=g.__dict__.copy()
    pick=rng.choice(["gate","signal","side","take_profit","stop_loss","max_horizon","add_at","reduce_at"])
    if pick in ("gate","signal"):
        r=d[pick]; d[pick]=Rule(r.feature if rng.random()<.7 else rng.randrange(nf), r.threshold+rng.gauss(0,.2), r.direction if rng.random()<.8 else -r.direction)
    elif pick=="side": d[pick]=-d[pick]
    elif pick=="max_horizon": d[pick]=max(2,min(30,d[pick]+rng.choice([-3,-1,1,3])))
    else:d[pick]=max(.002,min(.25,d[pick]*np.exp(rng.gauss(0,.2))))
    return Specialist(**d)
def eval_task(a):
    ticker,g,null_seed,rows=a;X,Y,_=evidence_arrays(ticker);X=X[-rows:];Y=Y[-rows:]
    if null_seed is not None:Y=temporal_block_permute(Y,null_seed,20)
    return quality(evaluate_one(g,X,Y,10))
def run_arm(name,null,generations,pop,workers,rows,seed):
    rng=random.Random(seed); nf=evidence_arrays(TICKERS[0])[0].shape[1]; P=[random_specialist(rng,nf) for _ in range(pop)]
    ledger=[]; t0=time.perf_counter()
    with ProcessPoolExecutor(max_workers=workers) as ex:
      for gen in range(generations):
        tasks=[]
        for i,g in enumerate(P):
          for j,t in enumerate(TICKERS):
            ns=(seed+gen*100000+i*100+j) if null else None
            tasks.append((t,g,ns,rows))
        qs=list(ex.map(eval_task,tasks,chunksize=4)); agg=[]
        for i,g in enumerate(P):
          q=qs[i*len(TICKERS):(i+1)*len(TICKERS)]
          agg.append(aggregate_quality_summaries(q))
        order=sorted(range(pop),key=lambda i:score(agg[i]),reverse=True)
        elite=[P[i] for i in order[:max(4,pop//4)]]
        best=agg[order[0]]
        ledger.append({"generation":gen+1,"best":best,"median_mean":float(np.median([x["mean"] for x in agg if x["mean"]>-1e8]))})
        P=elite+[mutate(rng.choice(elite),rng,nf) for _ in range(pop-len(elite))]
    return {"arm":name,"generations":generations,"population":pop,"ticker_evaluations":generations*pop*len(TICKERS),"seconds":time.perf_counter()-t0,"ledger":ledger}
if __name__=="__main__":
 ap=argparse.ArgumentParser();ap.add_argument("--workers",type=int,default=60);ap.add_argument("--generations",type=int,default=6);ap.add_argument("--population",type=int,default=48);ap.add_argument("--rows",type=int,default=2500);a=ap.parse_args()
 assert_independent_path(ROOT)
 t=time.perf_counter(); real=run_arm("real",False,a.generations,a.population,a.workers,a.rows,1776); null=run_arm("matched_temporal_block_null",True,a.generations,a.population,a.workers,a.rows,1776)
 out={"format":"MTS_G3_MATCHED_REAL_NULL_PILOT_V1","status":"PILOT_ONLY_NOT_PRODUCTION","workers":a.workers,"tickers":TICKERS,"rows":a.rows,"arms":[real,null],"total_seconds":time.perf_counter()-t,"matched_budget":real["ticker_evaluations"]==null["ticker_evaluations"],"production_authorized":False}
 p=Path("Research/G3/MTS_G3_MATCHED_REAL_NULL_PILOT_20261006.json");p.write_text(json.dumps(out,indent=2)+"\n");print(json.dumps({k:v for k,v in out.items() if k!="arms"}|{"real_seconds":real["seconds"],"null_seconds":null["seconds"],"real_final":real["ledger"][-1],"null_final":null["ledger"][-1]},indent=2))
