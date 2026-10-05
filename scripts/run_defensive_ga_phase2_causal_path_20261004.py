#!/usr/bin/env python3
import gzip, pickle, json, math, random, hashlib
from pathlib import Path
from collections import defaultdict, Counter
from statistics import mean

ROOT=Path("/home/ubuntu/Momentum-Trading-System_v4")
CACHE=Path("/home/ubuntu/mts-v4-cache/discovery_research_population_v1.RECONSTRUCTED.pkl.gz")
PROTO=ROOT/"Research/Protocols/MTS_DEFENSIVE_GA_PHASE2_CAUSAL_PATH_FREEZE_20261004.json"
REPORT=ROOT/"Research/Reports/MTS_DEFENSIVE_GA_PHASE2_CAUSAL_PATH_20261004.json"
CHECK=ROOT/"Research/Reports/MTS_DEFENSIVE_GA_PHASE2_CAUSAL_PATH_CHECKPOINT_20261004.json"
LOG=ROOT/"Research/Logs/MTS_DEFENSIVE_GA_PHASE2_CAUSAL_PATH_20261004.log"

SEED=20261004
R=random.Random(SEED)
POP=220
MAX_GEN=18
ELITE=36
STALE_STOP=7
COST=0.001

DEV=set("AMGN CI MPC STLD EXC CFG AJG NUE KKR TDG PPG TRV RL CTSH T FIS NOW SBAC SMCI KDP COST OMC NKE RSG ROK SO XEL DECK TRGP WELL CDW ITW DHI IRM COIN TPL FANG HWM NFLX BEN BNY BLDR EVRG GILD MCO TECH CLX PCAR COO FITB".split())
WINDOWS={
"GFC":("2007-10-09","2009-03-09"),"2011":("2011-07-22","2011-10-03"),
"2015_16":("2015-08-20","2016-02-11"),"2018":("2018-10-03","2018-12-24"),
"COVID":("2020-02-19","2020-03-23"),"2022":("2022-01-03","2022-10-12")}
FAMILIES=["MOMENTUM","BREAKOUT","TREND","MEAN_REVERSION","VOLUME_LIQUIDITY","RELATIVE_CROSS_SECTIONAL","MARKET_REGIME_STRUCTURE"]
HORIZONS=[10,20,63]
DEPTHS=[0.02,0.03,0.04,0.05,0.07,0.10]
RECLAIMS=[0.25,0.50,0.75,1.0]
DEADLINES=[2,3,5,8,10]
CONFIRMS=[0,1,2]
HOLDS=[2,3,5,8,10,15,20]
STOPS=[None,0.02,0.03,0.04,0.05,0.07,0.10]
TARGETS=[None,0.03,0.05,0.08,0.12,0.20]

SCORING={
"mean":1.0,
"worst_window":0.55,
"log_profit_factor":0.02,
"win_excess":0.04,
"cvar05":0.20,
"window_dispersion":-0.15
}

def wlabel(date):
    for w,(a,b) in WINDOWS.items():
        if a <= date <= b: return w
    return None

with gzip.open(CACHE,"rb") as f:
    src=pickle.load(f)
rows=[]
for rr in src["rows"]:
    if rr.get("ticker") not in DEV: continue
    if rr.get("family")=="VOLATILITY": continue
    if rr.get("h") not in HORIZONS: continue
    w=wlabel(rr.get("signal_date",""))
    if not w: continue
    path=rr.get("path") or []
    if len(path)<2: continue
    rows.append({
      "ticker":rr["ticker"],"family":rr["family"],"h":int(rr["h"]),
      "window":w,"signal_date":rr["signal_date"],"ep":float(rr["ep"]),
      "path":path
    })

BY_FAM=defaultdict(list)
for i,r in enumerate(rows): BY_FAM[r["family"]].append(i)

def canon(g):
    return {
      "families":tuple(sorted(set(g["families"]))),
      "horizons":tuple(sorted(set(g["horizons"]))),
      "entry_mode":g["entry_mode"],
      "depth":g["depth"],"reclaim":g["reclaim"],"deadline":g["deadline"],
      "confirm":g["confirm"],"hold":g["hold"],"stop":g["stop"],"target":g["target"]
    }

def key(g):
    x=canon(g)
    return json.dumps(x,sort_keys=True,default=list)

def randg():
    fam=[f for f in FAMILIES if R.random()<0.34]
    if not fam: fam=[R.choice(FAMILIES)]
    hs=[h for h in HORIZONS if R.random()<0.55]
    if not hs: hs=[R.choice(HORIZONS)]
    mode=R.choice(["IMMEDIATE","PULLBACK_RECLAIM"])
    return canon({"families":fam,"horizons":hs,"entry_mode":mode,
      "depth":R.choice(DEPTHS),"reclaim":R.choice(RECLAIMS),"deadline":R.choice(DEADLINES),
      "confirm":R.choice(CONFIRMS),"hold":R.choice(HOLDS),"stop":R.choice(STOPS),"target":R.choice(TARGETS)})

def mutate(g):
    g={k:(list(v) if isinstance(v,tuple) else v) for k,v in canon(g).items()}
    n=1+(R.random()<0.28)
    for _ in range(int(n)):
        z=R.randrange(9)
        if z==0:
            f=R.choice(FAMILIES)
            if f in g["families"] and len(g["families"])>1: g["families"].remove(f)
            elif f not in g["families"]: g["families"].append(f)
        elif z==1:
            h=R.choice(HORIZONS)
            if h in g["horizons"] and len(g["horizons"])>1: g["horizons"].remove(h)
            elif h not in g["horizons"]: g["horizons"].append(h)
        elif z==2: g["entry_mode"]=R.choice(["IMMEDIATE","PULLBACK_RECLAIM"])
        elif z==3: g["depth"]=R.choice(DEPTHS)
        elif z==4: g["reclaim"]=R.choice(RECLAIMS)
        elif z==5: g["deadline"]=R.choice(DEADLINES)
        elif z==6: g["confirm"]=R.choice(CONFIRMS)
        elif z==7:
            if R.random()<0.5: g["hold"]=R.choice(HOLDS)
            else: g["stop"]=R.choice(STOPS)
        else: g["target"]=R.choice(TARGETS)
    return canon(g)

def enter(r,g):
    p=r["path"]
    if g["entry_mode"]=="IMMEDIATE":
        return 0,float(p[0]["open"])
    ep=r["ep"]; low=ep; up=0
    lim=min(len(p)-1,g["deadline"])
    for j in range(lim):
        bar=p[j]; low=min(low,float(bar["low"]))
        if low > ep*(1-g["depth"]): 
            up = up+1 if j>0 and float(bar["close"])>float(p[j-1]["close"]) else 0
            continue
        reclaim_level=low + g["reclaim"]*(ep-low)
        up = up+1 if j>0 and float(bar["close"])>float(p[j-1]["close"]) else 0
        if float(bar["close"])>=reclaim_level and up>=g["confirm"]:
            if j+1 < len(p): return j+1,float(p[j+1]["open"])
            return None
    return None

def sim(r,g):
    en=enter(r,g)
    if not en: return None
    ei,px=en; p=r["path"]
    end=min(len(p)-1,ei+g["hold"]-1)
    stop_px=px*(1-g["stop"]) if g["stop"] is not None else None
    targ_px=px*(1+g["target"]) if g["target"] is not None else None
    out=None
    for j in range(ei,end+1):
        b=p[j]; lo=float(b["low"]); hi=float(b["high"])
        if stop_px is not None and lo<=stop_px:
            out=stop_px; break
        if targ_px is not None and hi>=targ_px:
            out=targ_px; break
    if out is None: out=float(p[end]["close"])
    return out/px-1-COST

CACHE_EVAL={}
def evaluate(g):
    kk=key(g)
    if kk in CACHE_EVAL: return CACHE_EVAL[kk]
    fam=set(g["families"]); hs=set(g["horizons"])
    rets=[]; byw=defaultdict(list)
    for r in rows:
        if r["family"] not in fam or r["h"] not in hs: continue
        z=sim(r,g)
        if z is None: continue
        rets.append(z); byw[r["window"]].append(z)
    n=len(rets)
    if n<30 or len(byw)<3:
        out={"score":-999.0,"n":n,"g":canon(g)}
        CACHE_EVAL[kk]=out; return out
    vals=sorted(rets)
    m=sum(vals)/n; win=sum(v>0 for v in vals)/n
    gains=sum(v for v in vals if v>0); losses=-sum(v for v in vals if v<0)
    pf=gains/losses if losses>1e-12 else 99.0
    k=max(1,int(math.ceil(.05*n))); cvar=sum(vals[:k])/k
    bm={w:{"n":len(v),"mean":sum(v)/len(v),"win":sum(x>0 for x in v)/len(v)} for w,v in byw.items()}
    wm=[v["mean"] for v in bm.values()]
    worst=min(wm); avg=sum(wm)/len(wm); disp=(sum((x-avg)**2 for x in wm)/len(wm))**0.5
    score=(SCORING["mean"]*m + SCORING["worst_window"]*worst +
           SCORING["log_profit_factor"]*math.log(max(1e-9,min(pf,20))) +
           SCORING["win_excess"]*(win-.5) + SCORING["cvar05"]*cvar +
           SCORING["window_dispersion"]*disp)
    if worst<0: score-=0.25+2*abs(worst)
    if len(byw)<5: score-=0.04*(5-len(byw))
    out={"score":score,"n":n,"mean":m,"win":win,"pf":pf,"worst_window":worst,
         "cvar05":cvar,"window_dispersion":disp,"by_window":bm,"g":canon(g)}
    CACHE_EVAL[kk]=out; return out

pop=[randg() for _ in range(POP)]
best=None; stale=0
LOG.parent.mkdir(parents=True,exist_ok=True)
LOG.write_text("")
for gen in range(MAX_GEN):
    ev=[evaluate(g) for g in pop]
    ev.sort(key=lambda z:z["score"],reverse=True)
    cur=ev[0]
    if best is None or cur["score"]>best["score"]+1e-12:
        best=cur; stale=0
    else: stale+=1
    line=f"GEN={gen} UNIQUE={len(CACHE_EVAL)} SCORE={best['score']:.6f} N={best.get('n')} MEAN={best.get('mean',0):.5f} PF={best.get('pf',0):.3f} WORST={best.get('worst_window',0):.5f} STALE={stale}"
    print(line,flush=True)
    with LOG.open("a") as f:f.write(line+"\n")
    checkpoint={"format":"MTS_DEFENSIVE_GA_PHASE2_CAUSAL_PATH_CHECKPOINT_V1","provenance":"NEW_RESEARCH_POST_RECOVERY",
      "generation":gen,"unique_genomes":len(CACHE_EVAL),"best":best,"scoring":SCORING,
      "source_rows":len(rows),"test17_accessed":False,"protected_accessed":False}
    CHECK.write_text(json.dumps(checkpoint,indent=2,default=list))
    if stale>=STALE_STOP: break
    elites=[z["g"] for z in ev[:ELITE]]
    nxt=list(elites)
    while len(nxt)<POP:
        parent=R.choice(elites[:max(10,ELITE//2)])
        nxt.append(mutate(parent))
    pop=nxt

final=sorted(CACHE_EVAL.values(),key=lambda z:z["score"],reverse=True)
report={
 "format":"MTS_DEFENSIVE_GA_PHASE2_CAUSAL_PATH_V1",
 "provenance":"NEW_RESEARCH_POST_RECOVERY",
 "runner_provenance":"RECONSTRUCTED_FROM_SURVIVING_SPEC",
 "protocol_sha256":hashlib.sha256(PROTO.read_bytes()).hexdigest(),
 "source_cache":str(CACHE),
 "source_rows":len(rows),"source_tickers":len(set(r["ticker"] for r in rows)),
 "row_family_counts":dict(Counter(r["family"] for r in rows)),
 "row_window_counts":dict(Counter(r["window"] for r in rows)),
 "generations":gen+1,"unique_valid_genomes":len(CACHE_EVAL),
 "scoring":SCORING,"test17_accessed":False,"protected_accessed":False,
 "top":final[:100]
}
REPORT.write_text(json.dumps(report,indent=2,default=list))
print("COMPLETE",REPORT,flush=True)
