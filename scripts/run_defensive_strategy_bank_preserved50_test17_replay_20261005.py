#!/usr/bin/env python3
import gzip, pickle, json, math, random, hashlib
from pathlib import Path
from collections import Counter
import numpy as np
import pandas as pd
import pyarrow.parquet as pq

ROOT=Path("/home/ubuntu/Momentum-Trading-System_v4")
PROTO=ROOT/"Research/Protocols/MTS_DEFENSIVE_STRATEGY_BANK_GA_DISCOVERY_FREEZE_20261004.json"
IMPL=ROOT/"Research/Protocols/MTS_DEFENSIVE_GA_MAIN_IMPLEMENTATION_FREEZE_20261004.json"
CACHE=Path("/home/ubuntu/mts-v4-cache/preserved50_test17_replay_population_20261005.pkl.gz")
PRED=Path("/home/ubuntu/mts-v4-nexus-derived-market-current-sp500-calibration-20260915-RECONSTRUCTED-CLEAN/data/sp500-current-calibration-20260915__a0dd6a1a76bb/mts_market_predictors_v2__3e9bdc71246a/predictor-v2-initial-20260929-predictors-2005-09-14-2026-09-14.parquet")
VIX=ROOT/"Research/Data/CrashMultiMarketV1/VIX_History.csv"
VVIX=ROOT/"Research/Data/CrashMultiMarketV1/VVIX_History.csv"
OFR=ROOT/"Research/Data/CrashCausalPackV1/ofr_fsi_raw_20261004.csv"
REPORT=ROOT/"Research/Reports/MTS_DEFENSIVE_STRATEGY_BANK_GA_DISCOVERY_20261004.json"
CHECK=ROOT/"Research/Reports/MTS_DEFENSIVE_STRATEGY_BANK_GA_DISCOVERY_CHECKPOINT_20261004.json"
LOG=ROOT/"Research/Logs/MTS_DEFENSIVE_STRATEGY_BANK_GA_DISCOVERY_20261004.log"

SEED=20261004
R=random.Random(SEED)
POP=320
ELITE=48
MAX_GEN=28
STALE_STOP=9
COST=0.001

WINDOWS=[
 ("GFC","2007-11-20","2009-03-30"),
 ("2011","2011-06-13","2011-10-24"),
 ("2015_16","2015-07-06","2016-03-04"),
 ("2018","2018-11-14","2019-01-16"),
 ("COVID","2020-04-01","2020-04-14"),
 ("2022","2022-02-15","2022-11-02")]
WNAMES=[x[0] for x in WINDOWS]
DEV=set(['ACN', 'AEE', 'AIG', 'ALLE', 'AME', 'AMP', 'APA', 'ARE', 'ATO', 'BAX', 'BG', 'BR', 'BSX', 'CBOE', 'CDNS', 'CMCSA', 'CME', 'COF', 'CRM', 'DELL', 'DIS', 'DLTR', 'ECL', 'ELV', 'ETN', 'FCX', 'GE', 'GEV', 'GLW', 'GPC', 'HD', 'HPE', 'HSY', 'INTC', 'IVZ', 'JNJ', 'KLAC', 'KMI', 'KVUE', 'LIN', 'LYB', 'LYV', 'MAA', 'MRSH', 'MTB', 'NI', 'NTAP', 'PEG', 'PFG', 'PNC', 'PSKY', 'ROL', 'SCHW', 'SNPS', 'SPG', 'SWK', 'SYF', 'SYK', 'ULTA', 'UPS', 'V', 'VRSK', 'VRSN', 'WAB', 'WSM', 'XOM', 'ZTS'])
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
freeze=json.load(open(ROOT/"Research/Protocols/MTS_DEFENSIVE_STRATEGY_BANK_CONDITION_THRESHOLDS_FREEZE_20261005.json"))
cond_meta=freeze["cond_meta"]
thresholds=freeze["thresholds"]
conds=[]
for m in cond_meta:
    fi=FEATURES.index(m["feature"]); arr=X[:,:,fi]; q=float(m["threshold"])
    if m["direction"]==">=": conds.append(np.isfinite(arr)&(arr>=q))
    else: conds.append(np.isfinite(arr)&(arr<=q))
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
SLOTS=5

def _trade_candidates(g):
    elig=((FM & g["fmask"])!=0)&((HM & g["hmask"])!=0)
    ec=np.take(COND[:,:g["entry_delay"]+1,:],g["entry_rules"],axis=2).sum(axis=2)>=g["entry_k"]
    ec &= elig[:,None]
    has=ec.any(axis=1); first=np.argmax(ec,axis=1); entry_day=first+1
    has &= entry_day<=20
    ids=np.flatnonzero(has)
    if not len(ids): return []
    ed=entry_day[ids]; ep=OPEN[ids,ed]
    end=np.minimum(20,ed+g["max_hold"]-1)
    xc=np.take(COND[ids,:,:],g["exit_rules"],axis=2).sum(axis=2)>=g["exit_k"]
    start_obs=ed+g["min_hold"]-1
    valid=(DAY>=start_obs[:,None])&(DAY<end[:,None]); fire=xc&valid
    fa=fire.any(axis=1); fd=np.argmax(fire,axis=1); xd=np.where(fa,np.minimum(20,fd+1),end)
    xp=np.where(fa,OPEN[ids,xd],CLOSE[ids,end])
    out=[]
    for j,i in enumerate(ids):
        if not(np.isfinite(ep[j]) and ep[j]>0 and np.isfinite(xp[j])): continue
        e=int(ed[j]); x=int(xd[j]); ev=E[i]
        if e<1 or x<e or x>len(ev["future"]): continue
        entry_date=ev["future"][e-1]["date"]; exit_date=ev["future"][x-1]["date"]
        # causal selection strength, used only to resolve same-day capacity
        strength=0.0
        for ci in g["entry_rules"]:
            m=cond_meta[ci]; val=float(X[i,e-1,FEATURES.index(m["feature"])]); thr=m["threshold"]
            if not np.isfinite(val): continue
            margin=(thr-val)/(abs(thr)+1e-9) if m["direction"]=="<=" else (val-thr)/(abs(thr)+1e-9)
            strength+=max(0.0,margin)
        closes={}
        for d in range(e,x+1):
            if d<=len(ev["future"]):
                b=ev["future"][d-1]; c=float(b["close"])
                if np.isfinite(c): closes[b["date"]]=c
        out.append({"i":int(i),"ticker":ev["ticker"],"window":WNAMES[int(WIN[i])],
                    "entry_date":entry_date,"exit_date":exit_date,"entry_price":float(ep[j]),
                    "exit_price":float(xp[j]),"closes":closes,"strength":float(strength)})
    return out

def _simulate_exact(trades):
    episodes={}; all_daily=[]; compounded=1.0; total_sessions=0
    for wi,w in enumerate(WNAMES):
        a,b=WINDOWS[wi][1],WINDOWS[wi][2]
        cal=[d for d in all_dates if a<=d<=b]
        ts=[t for t in trades if t["window"]==w and t["entry_date"] in set(cal)]
        byentry={}
        for t in ts: byentry.setdefault(t["entry_date"],[]).append(t)
        cash=100000.0; pos={}; curve=[]; executed=0; missed=0
        for dt in cal:
            # exit at open before new entries
            for k,q in list(pos.items()):
                if q["exit_date"]==dt:
                    cash += q["shares"]*q["exit_price"]*(1-COST/2); del pos[k]
            held={q["ticker"] for q in pos.values()}
            cands=[t for t in byentry.get(dt,[]) if t["ticker"] not in held]
            cands=sorted(cands,key=lambda z:(-z["strength"],z["ticker"],z["entry_date"]))
            avail=max(0,SLOTS-len(pos)); chosen=cands[:avail]; missed+=max(0,len(cands)-len(chosen))
            if chosen:
                alloc=min(cash/len(chosen),100000.0/SLOTS)
                for t in chosen:
                    spend=min(alloc,cash)
                    if spend<=0: continue
                    shares=spend*(1-COST/2)/t["entry_price"]; cash-=spend
                    pos[(t["ticker"],t["entry_date"])]=dict(t,shares=shares,last=t["entry_price"]); executed+=1
            eq=cash
            for q in pos.values():
                if dt in q["closes"]: q["last"]=q["closes"][dt]
                eq += q["shares"]*q["last"]
            curve.append(float(eq))
        # liquidate any positions at final available mark
        terminal=curve[-1] if curve else 100000.0
        arr=np.array(curve or [100000.0]); peak=np.maximum.accumulate(arr); mdd=float(np.min(arr/peak-1))
        ret=float(terminal/100000.0-1); compounded*=1+ret; total_sessions+=len(cal)
        episodes[w]={"sessions":len(cal),"return":ret,"max_daily_mtm_drawdown":mdd,"trades":executed,"missed_capacity":missed}
        if len(arr): all_daily.extend((arr/100000.0).tolist())
    years=max(total_sessions/252.0,1/252.0)
    cagr=float(compounded**(1/years)-1) if compounded>0 else -1.0
    worst_dd=min((z["max_daily_mtm_drawdown"] for z in episodes.values()),default=0.0)
    worst_ret=min((z["return"] for z in episodes.values()),default=0.0)
    return {"cagr":cagr,"max_daily_mtm_drawdown":float(worst_dd),"compounded_reset_return":float(compounded-1),
            "worst_episode_return":float(worst_ret),"total_trades":sum(z["trades"] for z in episodes.values()),"episodes":episodes}

def evaluate(g):
    g=canon(g); kk=json.dumps(g,sort_keys=True,default=list)
    if kk in CACHE_EVAL:return CACHE_EVAL[kk]
    tr=_trade_candidates(g)
    if len(tr)<30:
        out={"score":-999.0,"n":len(tr),"g":g}; CACHE_EVAL[kk]=out; return out
    sim=_simulate_exact(tr)
    # scalar is only an evolutionary search ordering; final selection is Pareto CAGR vs exact daily MTM DD.
    # Penalize negative episode performance and excessive DD; do not impose a fixed final CAGR/DD preference.
    pos_eps=sum(z["return"]>0 for z in sim["episodes"].values())
    score=sim["cagr"] + 1.5*sim["max_daily_mtm_drawdown"] + .03*(pos_eps/6.0) + .25*min(0,sim["worst_episode_return"])
    out={"score":float(score),"n":len(tr),"g":g,**sim,"positive_episodes":pos_eps}
    CACHE_EVAL[kk]=out; return out

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

finalists=json.load(open(ROOT/"Research/Protocols/MTS_DEFENSIVE_STRATEGY_BANK_FINALISTS_FREEZE_20261004.json"))["finalists"]
results=[]
for f in finalists:
    z=evaluate(f["genome"])
    results.append({"id":f["id"],"source_frontier_index":f["source_frontier_index"],"development_metrics":f["development_metrics"],"replay":z,"g_described":describe(f["genome"])})
    print(f["id"],"CAGR",z.get("cagr"),"MDD",z.get("max_daily_mtm_drawdown"),"WORST",z.get("worst_episode_return"),"TRADES",z.get("total_trades"),"POS",z.get("positive_episodes"),flush=True)
out={"format":"MTS_DEFENSIVE_STRATEGY_BANK_PRESERVED50_TEST17_REPLAY_V1","date":"2026-10-05","status":"FROZEN_FINALISTS_REPLAYED_ONCE","population":{"tickers":len(DEV),"preserved50":50,"test17":17,"events":N},"condition_thresholds":"development-frozen numeric thresholds","accounting":"exact daily mark-to-market, 5 equal-capacity slots, episode-reset capital","provenance_note":"preserved50 candidate population reconstructed from surviving deterministic search specification; TEST17 from reconstructed consumed cache; neither is pristine validation evidence","results":results,"remaining_discovery_accessed":False,"verification_A_accessed":False,"verification_B_accessed":False,"mutation_after_reveal":False}
Path(ROOT/"Research/Reports/MTS_DEFENSIVE_STRATEGY_BANK_PRESERVED50_TEST17_REPLAY_20261005.json").write_text(json.dumps(out,indent=2))
