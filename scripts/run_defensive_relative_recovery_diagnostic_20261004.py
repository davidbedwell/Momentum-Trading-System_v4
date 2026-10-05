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


# Frozen core conditions by semantic lookup.
def cidx(feature,direction,q):
    for i,m in enumerate(cond_meta):
        if m["feature"]==feature and m["direction"]==direction and abs(m["quantile"]-q)<1e-9:return i
    raise KeyError((feature,direction,q))
entry_rules=[cidx("stock_rv_pct","<=",.20),cidx("market_ret20","<=",.80),cidx("market_drawdown252","<=",.50)]
exit2=[cidx("stock_rsi14",">=",.50),cidx("market_ret20",">=",.35)]
exit3=exit2+[cidx("ofr_funding_lag2","<=",.20)]
variants=[
 ("D3_EXIT2",3,exit2,2),
 ("D5_EXIT2",5,exit2,2),
 ("D3_EXIT3",3,exit3,2),
 ("D5_EXIT3",5,exit3,2)]
# Main frontier family eligibility union: exclude only pure BREAKOUT/VOLATILITY/MARKET_REGIME-only signals;
# horizon is frozen to 5.
allowed_fams=set(["MOMENTUM","TREND","MEAN_REVERSION","VOLUME_LIQUIDITY","RELATIVE_CROSS_SECTIONAL"])
allow_mask=sum(1<<FIDX[x] for x in allowed_fams)
h5=1<<HIDX[5]

def make_trades(delay,xrules,xk):
    elig=((FM&allow_mask)!=0)&((HM&h5)!=0)
    ec=np.take(COND[:,:delay+1,:],entry_rules,axis=2).sum(axis=2)>=2
    ec &= elig[:,None]
    first=np.argmax(ec,axis=1); has=ec.any(axis=1); ed=first+1
    xc=np.take(COND,xrules,axis=2).sum(axis=2)>=xk
    out=[]
    for i in np.flatnonzero(has & (ed<=20)):
        e=int(ed[i])
        if not np.isfinite(OPEN[i,e]):continue
        start=e
        end=min(20,e+20-1)
        fire=None
        for obs in range(e,end):
            if xc[i,obs] and obs>=e:
                fire=obs+1;break
        xd=fire if fire is not None else end
        xp=OPEN[i,xd] if fire is not None and np.isfinite(OPEN[i,xd]) else CLOSE[i,end]
        if not np.isfinite(xp):continue
        ep=float(OPEN[i,e]); ret=float(xp/ep-1-COST)
        # strongest entry margin = count + normalized distance beyond satisfied thresholds.
        margins=[]
        for ci in entry_rules:
            m=cond_meta[ci]; val=float(X[i,e-1,FEATURES.index(m["feature"])])
            thr=m["threshold"]
            if m["direction"]=="<=": margins.append((thr-val)/(abs(thr)+1e-9))
            else:margins.append((val-thr)/(abs(thr)+1e-9))
        strength=sum(max(0,x) for x in margins)
        out.append(dict(ticker=E[i]["ticker"],signal_date=E[i]["date"],window=WNAMES[int(WIN[i])],
          entry_day=e,exit_day=xd,entry_price=ep,exit_price=float(xp),net_return=ret,strength=strength))
    return out



trades=make_trades(3,exit2,2)
key={(e["ticker"],e["date"]):i for i,e in enumerate(E)}
# derive causal signal-time observations
rows=[]
for t in trades:
 i=key[(t["ticker"],t["signal_date"])];obs=max(0,t["entry_day"]-1)
 def v(n):return float(X[i,obs,FEATURES.index(n)])
 sr5,sr20=v("stock_ret5"),v("stock_ret20"); mr5,mr20=v("market_ret5"),v("market_ret20")
 rows.append({"t":t,"stock_dd":v("stock_drawdown252"),"rel5":sr5-mr5,"rel20":sr20-mr20,"mret20":mr20,"mdd":v("market_drawdown252")})
dims=["stock_dd","rel5","rel20","mret20","mdd"]
sorts={k:np.sort(np.array([r[k] for r in rows if np.isfinite(r[k])])) for k in dims}
def pct(k,v):
 a=sorts[k];return np.searchsorted(a,v,side="right")/len(a)
for r in rows:
 for k in dims:r[k+"_pct"]=pct(k,r[k]) if np.isfinite(r[k]) else np.nan
def stats(rr):
 x=np.array([r["t"]["net_return"] for r in rr])
 if not len(x):return {"n":0}
 w=x[x>0];l=x[x<=0];loss=-l.sum()
 return {"n":len(x),"win_rate":float((x>0).mean()),"mean":float(x.mean()),"median":float(np.median(x)),
 "mean_winner":float(w.mean()) if len(w) else None,"mean_loser":float(l.mean()) if len(l) else None,
 "profit_factor":float(w.sum()/loss) if loss>1e-12 else 99.}
bins=[0,.2,.4,.6,.8,1.]
report={"format":"MTS_DEFENSIVE_RELATIVE_RECOVERY_DIAGNOSTIC_V1","provenance":"NEW_RESEARCH_POST_RECOVERY","quintiles":{},"cells":{},"episodes":{},"protected_accessed":False,"test17_accessed":False,"preserved50_accessed":False}
for k in dims:
 report["quintiles"][k]=[{"bin":[lo,hi],**stats([r for r in rows if r[k+"_pct"]>lo and r[k+"_pct"]<=hi])} for lo,hi in zip(bins[:-1],bins[1:])]
# damaged stock means lower stock_drawdown252 percentile (more negative); relative strength higher percentile.
# 3x3 cells to preserve support.
tb=[0,1/3,2/3,1]
for rel in ["rel5","rel20"]:
 cells=[]
 for dlo,dhi in zip(tb[:-1],tb[1:]):
  for rlo,rhi in zip(tb[:-1],tb[1:]):
   rr=[r for r in rows if r["stock_dd_pct"]>dlo and r["stock_dd_pct"]<=dhi and r[rel+"_pct"]>rlo and r[rel+"_pct"]<=rhi]
   cells.append({"damage_pct_bin":[dlo,dhi],"relative_pct_bin":[rlo,rhi],**stats(rr)})
 report["cells"][rel]=cells
# Explicit hypothesis cell: most damaged third + strongest relative third + still-weak market lower half ret20.
for rel in ["rel5","rel20"]:
 rr=[r for r in rows if r["stock_dd_pct"]<=1/3 and r[rel+"_pct"]>2/3 and r["mret20_pct"]<=.5]
 report["cells"][rel+"_hypothesis"]=stats(rr)
# episode hypothesis support
for wn in WNAMES:
 report["episodes"][wn]={}
 for rel in ["rel5","rel20"]:
  rr=[r for r in rows if r["t"]["window"]==wn and r["stock_dd_pct"]<=1/3 and r[rel+"_pct"]>2/3 and r["mret20_pct"]<=.5]
  report["episodes"][wn][rel]=stats(rr)
Path("Research/Reports/MTS_DEFENSIVE_RELATIVE_RECOVERY_DIAGNOSTIC_20261004.json").write_text(json.dumps(report,indent=2))
print("HYP",json.dumps({k:v for k,v in report["cells"].items() if "hypothesis" in k},indent=2))
for rel in ["rel5","rel20"]:
 print("\n",rel,"3x3")
 for z in report["cells"][rel]:print(z)
print("\nEPISODES",json.dumps(report["episodes"],indent=2))
