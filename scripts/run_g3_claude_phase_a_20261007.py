from __future__ import annotations
import json, time, random
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from Core.g3.realdata import ROOT
from Core.g3.earnings_evidence import build_earnings_index, aligned_evidence_with_earnings
from Core.g3.starter import assert_independent_path, Specialist, Rule, evaluate_one, quality
from Core.g3.search_v3 import structural_screen

TICKERS=["AAPL","MSFT","XOM","JPM","JNJ","CAT","WMT","NVDA"]
DATA={}
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
def run_stock(t,data,generations=6,pop=48,workers=60,seed=1776000):
    rng=random.Random(seed); nf=data[t][0].shape[1]; P=structural_screen({t:data[t]},pop); ledger=[]
    with ProcessPoolExecutor(max_workers=workers,initializer=init_worker,initargs=(data,)) as ex:
        for gen in range(generations):
            qs=list(ex.map(task,[(t,g) for g in P],chunksize=4))
            order=sorted(range(pop),key=lambda i:score(qs[i]),reverse=True)
            valid=[q for q in qs if q["n"]>=25]
            top=qs[order[0]]
            ledger.append({"generation":gen+1,"median_mean":float(np.median([q["mean"] for q in valid])) if valid else -1e9,
                           "iqr_mean":[float(np.quantile([q["mean"] for q in valid],.25)),float(np.quantile([q["mean"] for q in valid],.75))] if valid else [-1e9,-1e9],
                           "qualifying":len(valid),"top":top})
            elite=[P[i] for i in order[:max(4,pop//4)]]
            P=elite+[mutate(rng.choice(elite),rng,nf) for _ in range(pop-len(elite))]
    return ledger[-1]
if __name__=="__main__":
    assert_independent_path(ROOT)
    events=build_earnings_index(TICKERS); dates,AX,AY,cols=aligned_evidence_with_earnings(TICKERS,events)
    AX=AX[-2500:]; AY=AY[-2500:]; dates=dates[-2500:]
    data={t:(AX[:,i,:].copy(),AY[:,i,:].copy()) for i,t in enumerate(TICKERS)}
    out={"format":"MTS_G3_CLAUDE_PHASE_A_STOCK_LEVEL_V2_DIAGNOSTIC","protocol":"frozen V2 structural_screen + 6x48 lifecycle GA","decision_rule":{"strong_pooling_evidence":">=5/8 final median > 0.003","weak_feature_signal":"<=2/8 final median > 0.003","ambiguous":"3-4/8 final median > 0.003"},"tickers":TICKERS,"date_start":str(dates[0]),"date_end":str(dates[-1]),"results":[]}
    t0=time.perf_counter()
    for t in TICKERS:
        r=run_stock(t,data)
        out["results"].append({"ticker":t,**r}); print(t,r["median_mean"],r["qualifying"],r["top"]["mean"],flush=True)
    n=sum(r["median_mean"]>0.003 for r in out["results"])
    out["count_above_0_003"]=n
    out["decision"]="PROCEED_PHASE_BC" if n>=3 else "STOPPING_RULE_EVALUATION"
    out["seconds"]=time.perf_counter()-t0
    Path("Research/G3/MTS_G3_CLAUDE_PHASE_A_STOCK_LEVEL_V2_DIAGNOSTIC_20261007.json").write_text(json.dumps(out,indent=2)+"\n")
    print("DECISION",out["decision"],"COUNT",n,"SECONDS",round(out["seconds"],2))
