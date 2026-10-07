from __future__ import annotations
import argparse,json,random,time,hashlib
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from Core.g3.realdata import ROOT
from Core.g3.earnings_evidence import build_earnings_index,aligned_evidence_with_earnings
from Core.g3.preregistered_nullgate import *
from Core.g3.starter import assert_independent_path,random_specialist,Specialist,Rule,evaluate_one,quality,aggregate_quality_summaries

TICKERS=["AAPL","MSFT","XOM","JPM","JNJ","CAT","WMT","NVDA"]
DATA={}
def init_worker(data): global DATA; DATA=data
def score(q): return (-1e9,-1e9,-1e9) if q["n"]<25 else (q["mean"],q["tail"],-q["duration"])
def mutate(g,rng,nf):
    d=g.__dict__.copy();p=rng.choice(["gate","signal","side","take_profit","stop_loss","max_horizon","add_at","reduce_at"])
    if p in ("gate","signal"):
        r=d[p];d[p]=Rule(r.feature if rng.random()<.7 else rng.randrange(nf),r.threshold+rng.gauss(0,.2),r.direction if rng.random()<.8 else -r.direction)
    elif p=="side": d[p]=-d[p]
    elif p=="max_horizon": d[p]=max(2,min(30,d[p]+rng.choice([-3,-1,1,3])))
    else: d[p]=max(.002,min(.25,d[p]*np.exp(rng.gauss(0,.2))))
    return Specialist(**d)
def task(a):
    t,g=a;X,Y=DATA[t]
    return quality(evaluate_one(g,X,Y,10))
def run_arm(data,generations,pop,workers,search_seed):
    rng=random.Random(search_seed);nf=next(iter(data.values()))[0].shape[1];P=[random_specialist(rng,nf) for _ in range(pop)];led=[]
    t0=time.perf_counter()
    with ProcessPoolExecutor(max_workers=workers,initializer=init_worker,initargs=(data,)) as ex:
        for gen in range(generations):
            qs=list(ex.map(task,[(t,g) for g in P for t in TICKERS],chunksize=4))
            agg=[aggregate_quality_summaries(qs[i*8:(i+1)*8]) for i in range(pop)]
            order=sorted(range(pop),key=lambda i:score(agg[i]),reverse=True);elite=[P[i] for i in order[:max(4,pop//4)]]
            led.append({"generation":gen+1,"best":agg[order[0]],"median_mean":float(np.median([x["mean"] for x in agg if x["mean"]>-1e8]))})
            P=elite+[mutate(rng.choice(elite),rng,nf) for _ in range(pop-len(elite))]
    return {"seconds":time.perf_counter()-t0,"ticker_evaluations":generations*pop*len(TICKERS),"ledger":led,"primary":led[-1]["median_mean"]}
def derive_seed(rep,family):
    h=hashlib.sha256(f"G3-FROZEN-NULL|{rep}|{family}".encode()).digest()
    return int.from_bytes(h[:8],"big")%(2**32)
def make_data(AX,AY,family,rep):
    out={}
    for i,t in enumerate(TICKERS):
        if family is None: x,y=AX[:,i,:].copy(),AY[:,i,:].copy()
        else: x,y=apply_frozen_null(AX[:,i,:],AY[:,i,:],family,derive_seed(rep,f"{family}|{t}"))
        out[t]=(x,y)
    return out
if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--workers",type=int,default=60);ap.add_argument("--generations",type=int,default=6);ap.add_argument("--population",type=int,default=48)
    ap.add_argument("--rows",type=int,default=2500);ap.add_argument("--replicates",type=int,default=25);ap.add_argument("--output",default="Research/G3/MTS_G3_PREREGISTERED_REPLICATED_GATE_20261007.json")
    a=ap.parse_args();assert_independent_path(ROOT)
    events=build_earnings_index(TICKERS);dates,AX,AY,cols=aligned_evidence_with_earnings(TICKERS,events);AX=AX[-a.rows:];AY=AY[-a.rows:];dates=dates[-a.rows:]
    records=[];start=time.perf_counter();families=[None,*FROZEN_NULL_FAMILIES]
    for rep in range(a.replicates):
        search_seed=1776000+rep
        for family in families:
            name="REAL" if family is None else family
            rr=run_arm(make_data(AX,AY,family,rep),a.generations,a.population,a.workers,search_seed)
            records.append({"replicate":rep,"arm":name,"search_seed":search_seed,"null_seed_scheme":None if family is None else "sha256(rep,family,ticker)","result":rr})
        print(f"completed paired replicate {rep+1}/{a.replicates}",flush=True)
    complete=(len(records)==a.replicates*4)
    out={"format":"MTS_G3_PREREGISTERED_REPLICATED_GATE_V1","preregistration":"Research/G3/MTS_G3_NULL_GATE_PREREGISTRATION_20261007.md","tickers":TICKERS,"date_start":str(dates[0]),"date_end":str(dates[-1]),"rows":a.rows,"generations":a.generations,"population":a.population,"workers":a.workers,"replicates_requested":a.replicates,"records":records,"complete":complete,"total_seconds":time.perf_counter()-start,"production_discovery_authorized":False}
    if a.replicates==REPLICATES and complete:
        real=[r["result"]["primary"] for r in records if r["arm"]=="REAL"]
        nulls={f:[r["result"]["primary"] for r in records if r["arm"]==f] for f in FROZEN_NULL_FAMILIES}
        d=evaluate_replicated_gate(real,nulls)
        out["gate_decision"]={"state":d.state,"significant_nulls":d.significant_nulls,"tests":[t.__dict__ for t in d.tests]}
    else:
        out["gate_decision"]="WITHHELD_REQUIRES_EXACTLY_25_COMPLETE_REPLICATES"
    Path(a.output).write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps({"complete":complete,"replicates":a.replicates,"total_seconds":out["total_seconds"],"gate_decision":out["gate_decision"]},indent=2))
