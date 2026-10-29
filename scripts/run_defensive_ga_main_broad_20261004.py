#!/usr/bin/env python3
import gzip, pickle, json, math, random, hashlib
from pathlib import Path
from collections import Counter
import numpy as np
import pandas as pd
import pyarrow.parquet as pq

ROOT=Path("/home/ubuntu/Momentum-Trading-System_v4")
PROTO=ROOT/"Research/Protocols/MTS_DEFENSIVE_GA_MAIN_BROAD_DISCOVERY_FREEZE_20261004.json"
IMPL=ROOT/"Research/Protocols/MTS_DEFENSIVE_GA_MAIN_IMPLEMENTATION_FREEZE_20261004.json"
CACHE=Path("/home/ubuntu/mts-v4-cache/discovery_research_population_v1.RECONSTRUCTED.pkl.gz")
PRED=Path("/home/ubuntu/mts-v4-nexus-derived-market-current-sp500-calibration-20260915-RECONSTRUCTED-CLEAN/data/sp500-current-calibration-20260915__a0dd6a1a76bb/mts_market_predictors_v2__3e9bdc71246a/predictor-v2-initial-20260929-predictors-2005-09-14-2026-09-14.parquet")
VIX=ROOT/"Research/Data/CrashMultiMarketV1/VIX_History.csv"
VVIX=ROOT/"Research/Data/CrashMultiMarketV1/VVIX_History.csv"
OFR=ROOT/"Research/Data/CrashCausalPackV1/ofr_fsi_raw_20261004.csv"
REPORT=ROOT/"Research/Reports/MTS_DEFENSIVE_GA_MAIN_BROAD_20261004.json"
CHECK=ROOT/"Research/Reports/MTS_DEFENSIVE_GA_MAIN_BROAD_CHECKPOINT_20261004.json"
LOG=ROOT/"Research/Logs/MTS_DEFENSIVE_GA_MAIN_BROAD_20261004.log"

SEED=20261004
R=random.Random(SEED)
POP=320
ELITE=48
MAX_GEN=28
STALE_STOP=9
COST=0.001

WINDOWS=[
 ("GFC","2007-10-09","2009-03-09"),
 ("2011","2011-07-22","2011-10-03"),
 ("2015_16","2015-08-20","2016-02-11"),
 ("2018","2018-10-03","2018-12-24"),
 ("COVID","2020-02-19","2020-03-23"),
 ("2022","2022-01-03","2022-10-12")]
WNAMES=[x[0] for x in WINDOWS]
DEV=set("AMGN CI MPC STLD EXC CFG AJG NUE KKR TDG PPG TRV RL CTSH T FIS NOW SBAC SMCI KDP COST OMC NKE RSG ROK SO XEL DECK TRGP WELL CDW ITW DHI IRM COIN TPL FANG HWM NFLX BEN BNY BLDR EVRG GILD MCO TECH CLX PCAR COO FITB".split())
FAMILIES=["MOMENTUM","BREAKOUT","TREND","MEAN_REVERSION","VOLATILITY","VOLUME_LIQUIDITY","RELATIVE_CROSS_SECTIONAL","MARKET_REGIME_STRUCTURE"]
FIDX={x:i for i,x in enumerate(FAMILIES)}
HORIZONS=[3,5,10,20,63]
HIDX={x:i for i,x in enumerate(HORIZONS)}
QLEVELS=[0.20,0.35,0.50,0.65,0.80]
ENTRY_DELAYS=[0,1,2,3,5,8,10]
MIN_HOLDS=[1,2,3]
MAX_HOLDS=[2,3,5,8,10,15,20]

FEATURES=[
 "stock_ret5","stock_ret20","stock_close_sma20","stock_range20","stock_rsi14",
 "stock_relvol_pct","stock_drawdown252","stock_rv_pct",
 "market_ret5","market_ret20","market_drawdown252","breadth_above_sma200",
 "breadth_positive20","market_rv_pct","vix","vvix","ofr_funding_lag2","ofr_credit_lag2"
]

def wlabel(date):
    for i,(w,a,b) in enumerate(WINDOWS):
        if a<=date<=b: return i
    return None

# ---- Build unique ticker/date opportunity events from consumed cache ----
with gzip.open(CACHE,"rb") as f:
    src=pickle.load(f)
events={}
for rr in src["rows"]:
    t=rr.get("ticker"); sd=rr.get("signal_date","")
    if t not in DEV: continue
    wi=wlabel(sd)
    if wi is None: continue
    fam=rr.get("family"); h=int(rr.get("h",0))
    if fam not in FIDX or h not in HIDX: continue
    k=(t,sd)
    if k not in events:
        bars=rr.get("_bars") or []
        si=int(rr.get("si",-1))
        future=bars[si+1:si+21] if 0<=si<len(bars) else []
        if len(future)<3: continue
        events[k]={"ticker":t,"date":sd,"window":wi,"fmask":0,"hmask":0,"future":future}
    events[k]["fmask"] |= (1<<FIDX[fam])
    events[k]["hmask"] |= (1<<HIDX[h])
E=list(events.values())
N=len(E)

# ---- Predictor panel ----
pcols=[
 "security_id","effective_date","eligible","return_5__v1","return_20__v1",
 "close_to_sma_20__v1","range_position_20__v1","rsi_14__v1",
 "relative_volume_20_percentile__v1","drawdown_252__v1",
 "realized_vol_20_percentile__v1","breadth_above_sma_200__v1","breadth_positive_20__v1"]
pdf=pq.read_table(PRED,columns=pcols).to_pandas()
pdf["date"]=pd.to_datetime(pdf["effective_date"]).dt.strftime("%Y-%m-%d")
pdf["ticker"]=pdf["security_id"].astype(str).str.rsplit("_",n=1).str[-1]
pdf=pdf[pdf["eligible"].fillna(False)]

# Market features use the entire eligible reconstructed panel.
mkt=pdf.groupby("date",sort=True).agg(
 market_ret5=("return_5__v1","median"),
 market_ret20=("return_20__v1","median"),
 market_drawdown252=("drawdown_252__v1","median"),
 breadth_above_sma200=("breadth_above_sma_200__v1","median"),
 breadth_positive20=("breadth_positive_20__v1","median"),
 market_rv_pct=("realized_vol_20_percentile__v1","median")).sort_index()
all_dates=pd.Index(mkt.index)

# Causal external stress series.
vix=pd.read_csv(VIX)
vix["date"]=pd.to_datetime(vix["DATE"],format="%m/%d/%Y").dt.strftime("%Y-%m-%d")
vixs=vix.set_index("date")["CLOSE"].astype(float).reindex(all_dates).ffill()

vv=pd.read_csv(VVIX)
vv["date"]=pd.to_datetime(vv["DATE"],format="%m/%d/%Y").dt.strftime("%Y-%m-%d")
vvixs=vv.set_index("date")["VVIX"].astype(float).reindex(all_dates).ffill()

ofr=pd.read_csv(OFR)
ofr["date"]=pd.to_datetime(ofr["Date"]).dt.strftime("%Y-%m-%d")
ofr=ofr.set_index("date")[["Funding","Credit"]].astype(float).sort_index().shift(2)
ofr=ofr.reindex(all_dates).ffill()
mkt["vix"]=vixs
mkt["vvix"]=vvixs
mkt["ofr_funding_lag2"]=ofr["Funding"]
mkt["ofr_credit_lag2"]=ofr["Credit"]

stock_cols=[
 "return_5__v1","return_20__v1","close_to_sma_20__v1","range_position_20__v1",
 "rsi_14__v1","relative_volume_20_percentile__v1","drawdown_252__v1",
 "realized_vol_20_percentile__v1"]
sdf=pdf[pdf["ticker"].isin(DEV)][["ticker","date"]+stock_cols].drop_duplicates(["ticker","date"],keep="last")
stock_map={(r.ticker,r.date):np.array([
 r[stock_cols[0]],r[stock_cols[1]],r[stock_cols[2]],r[stock_cols[3]],
 r[stock_cols[4]],r[stock_cols[5]],r[stock_cols[6]],r[stock_cols[7]]],dtype=float)
 for _,r in sdf.iterrows()}
mkt_map={idx:row.to_numpy(dtype=float) for idx,row in mkt.iterrows()}

# ---- Event timelines, features and prices ----
F=len(FEATURES)
X=np.full((N,21,F),np.nan,dtype=np.float32)
OPEN=np.full((N,21),np.nan,dtype=np.float32)
HIGH=np.full((N,21),np.nan,dtype=np.float32)
LOW=np.full((N,21),np.nan,dtype=np.float32)
CLOSE=np.full((N,21),np.nan,dtype=np.float32)
FM=np.zeros(N,dtype=np.uint16); HM=np.zeros(N,dtype=np.uint8); WIN=np.zeros(N,dtype=np.int8)
for i,e in enumerate(E):
    FM[i]=e["fmask"]; HM[i]=e["hmask"]; WIN[i]=e["window"]
    dates=[e["date"]]+[b["date"] for b in e["future"][:20]]
    for j,date in enumerate(dates[:21]):
        sv=stock_map.get((e["ticker"],date))
        mv=mkt_map.get(date)
        if sv is not None: X[i,j,:8]=sv
        if mv is not None: X[i,j,8:]=mv
    for j,b in enumerate(e["future"][:20],start=1):
        OPEN[i,j]=float(b["open"]); HIGH[i,j]=float(b["high"])
        LOW[i,j]=float(b["low"]); CLOSE[i,j]=float(b["close"])

# Remove events without usable next-session price or signal feature context.
good=np.isfinite(OPEN[:,1]) & np.isfinite(X[:,0,:]).sum(axis=1).astype(bool)
X=X[good]; OPEN=OPEN[good]; HIGH=HIGH[good]; LOW=LOW[good]; CLOSE=CLOSE[good]
FM=FM[good]; HM=HM[good]; WIN=WIN[good]
E=[e for e,g in zip(E,good) if g]
N=len(E)

# ---- Generic condition library ----
thresholds={}
cond_meta=[]
conds=[]
for fi,name in enumerate(FEATURES):
    vals=X[:,:,fi].reshape(-1)
    vals=vals[np.isfinite(vals)]
    if len(vals)<100: continue
    qs=np.quantile(vals,QLEVELS)
    thresholds[name]=[float(x) for x in qs]
    for qi,q in enumerate(qs):
        arr=X[:,:,fi]
        conds.append(np.isfinite(arr)&(arr>=q))
        cond_meta.append({"feature":name,"direction":">=","quantile":QLEVELS[qi],"threshold":float(q)})
        conds.append(np.isfinite(arr)&(arr<=q))
        cond_meta.append({"feature":name,"direction":"<=","quantile":QLEVELS[qi],"threshold":float(q)})
COND=np.stack(conds,axis=2)
M=COND.shape[2]

def rand_mask(n,p=.35):
    m=0
    for i in range(n):
        if R.random()<p: m|=(1<<i)
    return m or (1<<R.randrange(n))

def rand_rules():
    n=R.randint(1,4)
    return tuple(sorted(R.sample(range(M),n)))

def canon(g):
    er=tuple(sorted(set(g["entry_rules"])))
    xr=tuple(sorted(set(g["exit_rules"])))
    mn=int(g["min_hold"]); mx=int(g["max_hold"])
    if mx<mn: mx=mn
    return {"fmask":int(g["fmask"]),"hmask":int(g["hmask"]),
      "entry_rules":er,"entry_k":max(1,min(int(g["entry_k"]),len(er))),
      "entry_delay":int(g["entry_delay"]),
      "exit_rules":xr,"exit_k":max(1,min(int(g["exit_k"]),len(xr))),
      "min_hold":mn,"max_hold":mx}

def randg():
    er=rand_rules(); xr=rand_rules()
    mn=R.choice(MIN_HOLDS); mx=R.choice([x for x in MAX_HOLDS if x>=mn])
    return canon({"fmask":rand_mask(len(FAMILIES)),"hmask":rand_mask(len(HORIZONS),.5),
      "entry_rules":er,"entry_k":R.randint(1,len(er)),"entry_delay":R.choice(ENTRY_DELAYS),
      "exit_rules":xr,"exit_k":R.randint(1,len(xr)),"min_hold":mn,"max_hold":mx})

def mutate(g):
    g=dict(canon(g)); z=R.randrange(9)
    if z==0:
        bit=1<<R.randrange(len(FAMILIES)); g["fmask"]^=bit
        if g["fmask"]==0:g["fmask"]=bit
    elif z==1:
        bit=1<<R.randrange(len(HORIZONS)); g["hmask"]^=bit
        if g["hmask"]==0:g["hmask"]=bit
    elif z==2:
        r=list(g["entry_rules"])
        if R.random()<.35 and len(r)<4:r.append(R.randrange(M))
        elif R.random()<.35 and len(r)>1:r.pop(R.randrange(len(r)))
        else:r[R.randrange(len(r))]=R.randrange(M)
        g["entry_rules"]=tuple(r); g["entry_k"]=min(g["entry_k"],len(r))
    elif z==3:g["entry_k"]=R.randint(1,len(g["entry_rules"]))
    elif z==4:g["entry_delay"]=R.choice(ENTRY_DELAYS)
    elif z==5:
        r=list(g["exit_rules"])
        if R.random()<.35 and len(r)<4:r.append(R.randrange(M))
        elif R.random()<.35 and len(r)>1:r.pop(R.randrange(len(r)))
        else:r[R.randrange(len(r))]=R.randrange(M)
        g["exit_rules"]=tuple(r); g["exit_k"]=min(g["exit_k"],len(r))
    elif z==6:g["exit_k"]=R.randint(1,len(g["exit_rules"]))
    elif z==7:g["min_hold"]=R.choice(MIN_HOLDS)
    else:g["max_hold"]=R.choice(MAX_HOLDS)
    return canon(g)

CACHE_EVAL={}
DAY=np.arange(21)[None,:]
def evaluate(g):
    g=canon(g)
    kk=json.dumps(g,sort_keys=True,default=list)
    if kk in CACHE_EVAL:return CACHE_EVAL[kk]
    elig=((FM & g["fmask"])!=0)&((HM & g["hmask"])!=0)
    if not np.any(elig):
        out={"score":-999.0,"n":0,"g":g}; CACHE_EVAL[kk]=out; return out
    ec=np.take(COND[:,:g["entry_delay"]+1,:],g["entry_rules"],axis=2).sum(axis=2)>=g["entry_k"]
    ec &= elig[:,None]
    has=ec.any(axis=1)
    first=np.argmax(ec,axis=1)
    entry_day=first+1
    has &= entry_day<=20
    has &= np.isfinite(OPEN[np.arange(N),np.minimum(entry_day,20)])
    ids=np.flatnonzero(has)
    if len(ids)<100:
        out={"score":-999.0,"n":int(len(ids)),"g":g}; CACHE_EVAL[kk]=out; return out
    ed=entry_day[ids]
    ep=OPEN[ids,ed]
    end=np.minimum(20,ed+g["max_hold"]-1)
    xc=np.take(COND[ids,:,:],g["exit_rules"],axis=2).sum(axis=2)>=g["exit_k"]
    start_obs=ed+g["min_hold"]-1
    valid=(DAY>=start_obs[:,None])&(DAY<end[:,None])
    fire=xc&valid
    fa=fire.any(axis=1)
    fd=np.argmax(fire,axis=1)
    exit_open_day=np.minimum(20,fd+1)
    xp=np.where(fa,OPEN[ids,exit_open_day],CLOSE[ids,end])
    ok=np.isfinite(ep)&np.isfinite(xp)&(ep>0)
    ids=ids[ok]; ed=ed[ok]; ep=ep[ok]; end=end[ok]; fa=fa[ok]; fd=fd[ok]; exit_open_day=exit_open_day[ok]; xp=xp[ok]
    if len(ids)<100:
        out={"score":-999.0,"n":int(len(ids)),"g":g}; CACHE_EVAL[kk]=out; return out
    last=np.where(fa,fd,end)
    days=np.arange(1,21)[None,:]
    held=(days>=ed[:,None])&(days<=last[:,None])
    lr=LOW[ids,1:]/ep[:,None]
    hr=HIGH[ids,1:]/ep[:,None]
    minr=np.min(np.where(held,np.where(np.isfinite(lr),lr,np.inf),np.inf),axis=1)
    maxr=np.max(np.where(held,np.where(np.isfinite(hr),hr,-np.inf),-np.inf),axis=1)
    mae=np.minimum(0,minr-1)
    mfe=np.maximum(0,maxr-1)
    gross=xp/ep-1
    net=gross-COST
    duration=np.where(fa,exit_open_day-ed,end-ed+1).astype(float)
    giveback=np.maximum(0,mfe-gross)
    wins=WIN[ids]
    counts=np.bincount(wins,minlength=6)
    if np.any(counts<5):
        out={"score":-999.0,"n":int(len(ids)),"window_counts":counts.tolist(),"g":g}; CACHE_EVAL[kk]=out; return out
    by={}
    wm=[]
    for wi,w in enumerate(WNAMES):
        v=net[wins==wi]
        mm=float(v.mean()); wm.append(mm)
        by[w]={"n":int(len(v)),"mean":mm,"win":float((v>0).mean())}
    m=float(net.mean()); wr=float((net>0).mean())
    gains=float(net[net>0].sum()); losses=float(-net[net<0].sum())
    pf=gains/losses if losses>1e-12 else 99.0
    worst=min(wm); disp=float(np.std(wm))
    eff=float(np.mean(net/np.maximum(duration,1)*5.0))
    mmae=float(np.mean(-mae)); mgb=float(np.mean(giveback)); mdur=float(np.mean(duration))
    score=(m + .50*worst + .25*eff + .010*math.log(max(1e-9,min(pf,10))) +
           .010*(wr-.5) - .35*mmae - .30*mgb - .10*disp - .0005*mdur)
    if worst<0: score-=.10+2*abs(worst)
    out={"score":float(score),"n":int(len(net)),"mean":m,"win":wr,"pf":float(pf),
      "worst_window":float(worst),"window_dispersion":disp,"five_session_efficiency":eff,
      "mean_mae":float(np.mean(mae)),"mean_giveback":mgb,"mean_duration":mdur,
      "by_window":by,"g":g}
    CACHE_EVAL[kk]=out
    return out

def describe(g):
    z=dict(g)
    z["families"]=[FAMILIES[i] for i in range(len(FAMILIES)) if g["fmask"]&(1<<i)]
    z["horizons"]=[HORIZONS[i] for i in range(len(HORIZONS)) if g["hmask"]&(1<<i)]
    z["entry_conditions"]=[cond_meta[i] for i in g["entry_rules"]]
    z["exit_conditions"]=[cond_meta[i] for i in g["exit_rules"]]
    return z

pop=[randg() for _ in range(POP)]
best=None; stale=0
LOG.parent.mkdir(parents=True,exist_ok=True); LOG.write_text("")
for gen in range(MAX_GEN):
    ev=[evaluate(g) for g in pop]
    ev.sort(key=lambda z:z["score"],reverse=True)
    cur=ev[0]
    if best is None or cur["score"]>best["score"]+1e-12:
        best=cur; stale=0
    else: stale+=1
    line=f"GEN={gen} UNIQUE={len(CACHE_EVAL)} SCORE={best['score']:.6f} N={best.get('n')} MEAN={best.get('mean',0):.5f} PF={best.get('pf',0):.3f} WORST={best.get('worst_window',0):.5f} MAE={best.get('mean_mae',0):.5f} GIVEBACK={best.get('mean_giveback',0):.5f} DUR={best.get('mean_duration',0):.2f} STALE={stale}"
    print(line,flush=True)
    with LOG.open("a") as f:f.write(line+"\n")
    cp={"format":"MTS_DEFENSIVE_GA_MAIN_BROAD_CHECKPOINT_V1","generation":gen,"unique_genomes":len(CACHE_EVAL),
        "best":{**best,"g_described":describe(best["g"])},"source_events":N,
        "test17_accessed":False,"protected_accessed":False}
    CHECK.write_text(json.dumps(cp,indent=2,default=list))
    if stale>=STALE_STOP:break
    elites=[z["g"] for z in ev[:ELITE]]
    nxt=list(elites)
    while len(nxt)<POP:
        parent=R.choice(elites[:max(12,ELITE//2)])
        child=mutate(parent)
        if R.random()<.22: child=mutate(child)
        nxt.append(child)
    pop=nxt

final=sorted(CACHE_EVAL.values(),key=lambda z:z["score"],reverse=True)
top=[]
for z in final[:100]:
    zz=dict(z); zz["g_described"]=describe(z["g"]); top.append(zz)
report={
 "format":"MTS_DEFENSIVE_GA_MAIN_BROAD_V1",
 "provenance":"NEW_RESEARCH_POST_RECOVERY",
 "protocol_sha256":hashlib.sha256(PROTO.read_bytes()).hexdigest(),
 "implementation_sha256":hashlib.sha256(IMPL.read_bytes()).hexdigest(),
 "source_cache":str(CACHE),"source_events":N,
 "event_window_counts":{WNAMES[i]:int((WIN==i).sum()) for i in range(6)},
 "condition_library_size":M,"condition_thresholds":thresholds,
 "generations":gen+1,"unique_genomes":len(CACHE_EVAL),
 "test17_accessed":False,"preserved50_accessed":False,"protected_accessed":False,
 "top":top}
REPORT.write_text(json.dumps(report,indent=2,default=list))
print("COMPLETE",REPORT,flush=True)
