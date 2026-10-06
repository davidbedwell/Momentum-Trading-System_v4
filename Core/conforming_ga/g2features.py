"""Causal partition-local and disjoint-external feature tape for MTS-GA-G2."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import hashlib,json
import numpy as np,pandas as pd
from .external import load_spy,load_safe
from .ofr import load_ofr
from .peers import peer_indices_tape
from .availability import earnings_registry

EXT_REL=Path("Research/Data/ExternalMarket/G2")
ETF_PANEL=EXT_REL/"legacy_sector_etf_panel_2005_2026.parquet"
DGS10=EXT_REL/"FRED_DGS10_20261006.csv"
EXT_MANIFEST=EXT_REL/"manifest_20261006.json"
LEGACY_SECTOR_ETFS=("XLB","XLE","XLF","XLI","XLK","XLP","XLU","XLV","XLY")

@dataclass(frozen=True)
class G2Tape:
    dates:pd.DatetimeIndex
    tickers:tuple[str,...]
    stock:dict[str,np.ndarray]
    sector:dict[str,np.ndarray]
    market:dict[str,np.ndarray]
    execution:dict[str,np.ndarray]

def _pct(px,n):return px/px.shift(n)-1.0
def _gap(px,n):return px/px.rolling(n,min_periods=n).mean()-1.0
def _slope(px,n,k=5):
    ma=px.rolling(n,min_periods=n).mean()
    return (ma/ma.shift(k)-1.0)/k
def _donchian(px,n):
    hi=px.rolling(n,min_periods=n).max();lo=px.rolling(n,min_periods=n).min()
    return (px-lo)/(hi-lo).replace(0,np.nan)
def _rsi(ret,n=14):
    up=ret.clip(lower=0).rolling(n,min_periods=n).mean()
    dn=(-ret.clip(upper=0)).rolling(n,min_periods=n).mean()
    rs=up/dn.replace(0,np.nan)
    return 100-100/(1+rs)
def _rolling_beta(stock_ret,market_ret,n=60):
    mr=market_ret.reindex(stock_ret.index)
    out=pd.DataFrame(index=stock_ret.index,columns=stock_ret.columns,dtype=float)
    v=mr.rolling(n,min_periods=n).var(ddof=0)
    for c in stock_ret:
        cov=stock_ret[c].rolling(n,min_periods=n).cov(mr,ddof=0)
        out[c]=cov/v
    return out
def _avg_pair_corr(frame,n=60):
    a=frame.fillna(0).to_numpy(float);T,N=a.shape;out=np.full(T,np.nan)
    for t in range(n-1,T):
        h=a[t-n+1:t+1]
        with np.errstate(invalid="ignore",divide="ignore"):c=np.corrcoef(h,rowvar=False)
        if N>1:
            vals=c[np.triu_indices(N,1)];vals=vals[np.isfinite(vals)]
            if len(vals):out[t]=vals.mean()
    return pd.Series(out,index=frame.index)

def build_stock_layer(long_df:pd.DataFrame,tickers:tuple[str,...],spy:pd.DataFrame):
    d=long_df[long_df.ticker.isin(tickers)].copy()
    if set(d.ticker.unique())-set(tickers):raise RuntimeError("partition contamination")
    def piv(col):return d.pivot(index="date",columns="ticker",values=col).sort_index().reindex(columns=tickers).astype(float)
    adj=piv("adj_close");opn=piv("open");high=piv("high");low=piv("low");close=piv("close");vol=piv("volume");div=piv("dividends")
    factor=adj/close.replace(0,np.nan)
    aopen=opn*factor;ahigh=high*factor;alow=low*factor
    ret=adj.pct_change();spy0=spy.set_index("date").sort_index().reindex(adj.index)
    sret=spy0.adj_close.astype(float).pct_change()
    beta60=_rolling_beta(ret,sret,60)
    resid=ret.sub(beta60.mul(sret,axis=0))
    dollar=close*vol
    prev=adj.shift(1)
    tr=pd.DataFrame(np.maximum.reduce([(ahigh-alow).to_numpy(),
                                      (ahigh-prev).abs().to_numpy(),
                                      (alow-prev).abs().to_numpy()]),index=adj.index,columns=adj.columns)
    atr5=tr.rolling(5,min_periods=5).mean()/adj
    atr20=tr.rolling(20,min_periods=20).mean()/adj
    r5=_pct(adj,5)
    below20=adj<adj.rolling(20,min_periods=20).max()
    failed=((r5<=0)&below20).astype(float).rolling(30,min_periods=30).sum()
    features={
      "ret1":ret,"ret5":_pct(adj,5),"ret20":_pct(adj,20),"ret60":_pct(adj,60),
      "ret120":_pct(adj,120),"ret252":_pct(adj,252),
      "ma_gap20":_gap(adj,20),"ma_gap50":_gap(adj,50),"ma_gap200":_gap(adj,200),
      "ma_slope20":_slope(adj,20),"ma_slope50":_slope(adj,50),"ma_slope200":_slope(adj,200),
      "dist_high20":adj/adj.rolling(20,min_periods=20).max()-1,
      "dist_high252":adj/adj.rolling(252,min_periods=252).max()-1,
      "dist_low20":adj/adj.rolling(20,min_periods=20).min()-1,
      "dist_low252":adj/adj.rolling(252,min_periods=252).min()-1,
      "donchian20":_donchian(adj,20),"donchian60":_donchian(adj,60),
      "rv5":ret.rolling(5,min_periods=5).std(ddof=0),
      "rv20":ret.rolling(20,min_periods=20).std(ddof=0),
      "rv60":ret.rolling(60,min_periods=60).std(ddof=0),
      "vol_compression5_60":ret.rolling(5,min_periods=5).std(ddof=0)/ret.rolling(60,min_periods=60).std(ddof=0),
      "atr5":atr5,"atr20":atr20,"atr_compression5_20":atr5/atr20,
      "beta60":beta60,"idio_vol60":resid.rolling(60,min_periods=60).std(ddof=0),
      "residual_mom60":_pct(adj,60)-beta60.mul(_pct(spy0[["adj_close"]].rename(columns={"adj_close":"SPY"}),60)["SPY"],axis=0),
      "positive_day_fraction20":(ret>0).astype(float).rolling(20,min_periods=20).mean(),
      "failed_rebound_count30":failed,
      "max_single_day_return20":ret.rolling(20,min_periods=20).max(),
      "skew60":ret.rolling(60,min_periods=60).skew(),
      "dollar_volume20":dollar.rolling(20,min_periods=20).mean(),
      "amihud20":(ret.abs()/dollar.replace(0,np.nan)).rolling(20,min_periods=20).mean(),
      "overnight1":aopen/adj.shift(1)-1,
      "intraday1":adj/aopen-1,
      "volume_rel20":vol/vol.rolling(20,min_periods=20).mean(),
      "rsi14":_rsi(ret,14),
      "pullback_high20":adj/adj.rolling(20,min_periods=20).max()-1,
      "range_expansion5_20":atr5/atr20,
      "rel_market20":_pct(adj,20).sub(_pct(spy0[["adj_close"]].rename(columns={"adj_close":"SPY"}),20)["SPY"],axis=0),
      "rel_market60":_pct(adj,60).sub(_pct(spy0[["adj_close"]].rename(columns={"adj_close":"SPY"}),60)["SPY"],axis=0),
    }
    execution={"adj_close":adj.to_numpy(float),"open":opn.to_numpy(float),"high":high.to_numpy(float),
               "low":low.to_numpy(float),"close":close.to_numpy(float),"volume":vol.to_numpy(float),
               "dividends":div.to_numpy(float)}
    return adj.index,{k:v.to_numpy(float) for k,v in features.items()},execution

def build_dynamic_peer_layer(stock:dict[str,np.ndarray],window:int=60,k:int=3):
    r=np.nan_to_num(stock["ret1"],nan=0.0)
    peers=peer_indices_tape(r,window,k);T,N=r.shape
    names=("ret1","ret20","ret60","rv20","positive_day_fraction20","rel_market20")
    out={f"peer_{name}":np.full((T,N),np.nan) for name in names}
    out["peer_breadth_positive20"]=np.full((T,N),np.nan)
    for t in range(T):
        psrow=peers[t]
        for i,ps in enumerate(psrow):
            if not len(ps):continue
            for name in names:
                vals=stock[name][t,ps];vals=vals[np.isfinite(vals)]
                if len(vals):out[f"peer_{name}"][t,i]=float(vals.mean())
            vals=stock["ret20"][t,ps];vals=vals[np.isfinite(vals)]
            if len(vals):out["peer_breadth_positive20"][t,i]=float(np.mean(vals>0))
    out["peer_rel_strength20"]=stock["ret20"]-out["peer_ret20"]
    out["peer_rel_strength60"]=stock["ret60"]-out["peer_ret60"]
    return out

def _asof_series(source:pd.Series,dates:pd.DatetimeIndex,strict_prior=True):
    s=source.dropna().sort_index();idx=s.index.to_numpy(dtype="datetime64[ns]");vals=s.to_numpy(float)
    out=np.full(len(dates),np.nan)
    for j,dt in enumerate(dates):
        side="left" if strict_prior else "right"
        i=int(np.searchsorted(idx,np.datetime64(pd.Timestamp(dt)),side))-1
        if i>=0:out[j]=vals[i]
    return out

def _leadership_churn(ret20:pd.DataFrame,k=3,lag=20):
    a=ret20.to_numpy(float);T,N=a.shape;out=np.full(T,np.nan)
    for t in range(lag,T):
        now=set(np.argsort(np.nan_to_num(a[t],nan=-np.inf))[-min(k,N):])
        old=set(np.argsort(np.nan_to_num(a[t-lag],nan=-np.inf))[-min(k,N):])
        out[t]=1-len(now&old)/max(len(now|old),1)
    return pd.Series(out,index=ret20.index)

def build_market_layer(repo:Path,dates:pd.DatetimeIndex):
    spy=load_spy(repo).set_index("date").sort_index().reindex(dates)
    sc=spy["adj_close"].astype(float);sr=sc.pct_change();peak=sc.cummax()
    etf=pd.read_parquet(repo/ETF_PANEL)
    ep=etf.pivot(index="date",columns="ticker",values="adj_close").sort_index().reindex(dates).reindex(columns=LEGACY_SECTOR_ETFS)
    er=ep.pct_change();er20=_pct(ep,20)
    b20=(er20>0).mean(axis=1)
    ma200=ep.rolling(200,min_periods=200).mean();b200=(ep>ma200).mean(axis=1)
    pos5=(_pct(ep,5)>0).mean(axis=1)
    disp=er.std(axis=1,ddof=0).rolling(20,min_periods=20).mean()
    apc=_avg_pair_corr(er,60)
    lead=_leadership_churn(er20,3,20)
    s5=_pct(spy[["adj_close"]].rename(columns={"adj_close":"SPY"}),5)["SPY"]
    failed=((s5<=0)&(sc<sc.rolling(20,min_periods=20).max())).astype(float).rolling(30,min_periods=30).sum()
    running_trough=sc.cummin()
    sessions_since_trough=np.zeros(len(sc),float);last=0
    vals=sc.to_numpy(float);tr=running_trough.to_numpy(float)
    for i in range(len(sc)):
        if np.isfinite(vals[i]) and np.isfinite(tr[i]) and vals[i]<=tr[i]+1e-12:last=i
        sessions_since_trough[i]=i-last
    # Same-close market observables.
    v=pd.read_csv(repo/"Research/Data/CrashMultiMarketV1/VIX_History.csv")
    v["date"]=pd.to_datetime(v.DATE);vix=v.set_index("date")["CLOSE"].reindex(dates).ffill()
    vv=pd.read_csv(repo/"Research/Data/CrashMultiMarketV1/VVIX_History.csv")
    vv["date"]=pd.to_datetime(vv.DATE);vvix=vv.set_index("date")["VVIX"].reindex(dates).ffill()
    # Published macro/financial series are strict-prior to decision close.
    ofr=load_ofr(repo).set_index("Date").sort_index()
    d3=pd.read_csv(repo/"Research/Data/RiskFree/FRED_DGS3MO_20261005.csv")
    d3["observation_date"]=pd.to_datetime(d3.observation_date);d3["DGS3MO"]=pd.to_numeric(d3.DGS3MO,errors="coerce")
    d10=pd.read_csv(repo/DGS10);d10["observation_date"]=pd.to_datetime(d10.observation_date);d10["DGS10"]=pd.to_numeric(d10.DGS10,errors="coerce")
    ofr_fsi=_asof_series(ofr["OFR FSI"],dates,True);fund=_asof_series(ofr["Funding"],dates,True);cred=_asof_series(ofr["Credit"],dates,True)
    y3=_asof_series(d3.set_index("observation_date")["DGS3MO"],dates,True)
    y10=_asof_series(d10.set_index("observation_date")["DGS10"],dates,True)
    gap20=_gap(spy[["adj_close"]].rename(columns={"adj_close":"SPY"}),20)["SPY"]
    gap50=_gap(spy[["adj_close"]].rename(columns={"adj_close":"SPY"}),50)["SPY"]
    slope20=_slope(spy[["adj_close"]].rename(columns={"adj_close":"SPY"}),20)["SPY"]
    slope50=_slope(spy[["adj_close"]].rename(columns={"adj_close":"SPY"}),50)["SPY"]
    market={
      "spy_ret1":sr.to_numpy(float),"spy_ret5":_pct(spy[["adj_close"]].rename(columns={"adj_close":"SPY"}),5)["SPY"].to_numpy(float),
      "spy_ret20":_pct(spy[["adj_close"]].rename(columns={"adj_close":"SPY"}),20)["SPY"].to_numpy(float),
      "spy_ret60":_pct(spy[["adj_close"]].rename(columns={"adj_close":"SPY"}),60)["SPY"].to_numpy(float),
      "spy_dd":(sc/peak-1).to_numpy(float),"spy_vol20":sr.rolling(20,min_periods=20).std(ddof=0).to_numpy(float),
      "market_positive20":(pd.Series(_pct(spy[["adj_close"]].rename(columns={"adj_close":"SPY"}),20)["SPY"],index=dates)>0).astype(float).to_numpy(),
      "breadth_positive20":b20.to_numpy(float),"breadth_above200":b200.to_numpy(float),
      "breadth_positive20_delta5":b20.diff(5).to_numpy(float),"breadth_positive20_delta10":b20.diff(10).to_numpy(float),
      "breadth_above200_delta5":b200.diff(5).to_numpy(float),"breadth_above200_delta10":b200.diff(10).to_numpy(float),
      "sector_participation5":pos5.to_numpy(float),"sector_participation20":b20.to_numpy(float),
      "leadership_change20":lead.to_numpy(float),"cross_sectional_dispersion20":disp.to_numpy(float),
      "avg_pair_corr60":apc.to_numpy(float),"failed_rebound_count30":failed.to_numpy(float),
      "gap20":gap20.to_numpy(float),"gap50":gap50.to_numpy(float),
      "slope20":slope20.to_numpy(float),"slope50":slope50.to_numpy(float),
      "bounce_from_running_trough":(sc/running_trough-1).to_numpy(float),
      "sessions_since_running_trough":sessions_since_trough,
      "vix":vix.to_numpy(float),"vvix":vvix.to_numpy(float),
      "ofr_fsi":ofr_fsi,"funding":fund,"credit":cred,
      "funding_delta5":pd.Series(fund,index=dates).diff(5).to_numpy(float),
      "funding_delta20":pd.Series(fund,index=dates).diff(20).to_numpy(float),
      "credit_delta5":pd.Series(cred,index=dates).diff(5).to_numpy(float),
      "credit_delta20":pd.Series(cred,index=dates).diff(20).to_numpy(float),
      "tbill3m":y3,"tbill3m_delta20":pd.Series(y3,index=dates).diff(20).to_numpy(float),
      "yield10y":y10,"yield_curve_10y_3m":y10-y3,
    }
    return market

def add_earnings_layer(repo:Path,dates:pd.DatetimeIndex,tickers:tuple[str,...],stock:dict[str,np.ndarray]):
    p=earnings_registry(repo)
    if p is None:raise RuntimeError("MANDATORY_PIT_EARNINGS_REGISTRY_MISSING")
    e=pd.read_parquet(p) if p.suffix==".parquet" else pd.read_csv(p)
    e=e[e.ticker.isin(tickers)].copy();e["effective_date"]=pd.to_datetime(e.effective_date)
    cols=[c for c in e.columns if c not in ("ticker","security_id","effective_date")]
    for c in cols:
        piv=e.pivot(index="effective_date",columns="ticker",values=c).reindex(index=dates,columns=tickers)
        stock[c]=piv.to_numpy(float)
    return stock

def build_g2_tape(repo:Path,long_df:pd.DataFrame,tickers:tuple[str,...],
                  start="2006-09-15",end="2026-09-14")->G2Tape:
    spy=load_spy(repo)
    dates,stock,execution=build_stock_layer(long_df,tickers,spy)
    stock=add_earnings_layer(repo,dates,tickers,stock)
    sector=build_dynamic_peer_layer(stock,60,3)
    market=build_market_layer(repo,dates)
    safe=load_safe(repo).dropna().set_index("observation_date").sort_index()
    disc=_asof_series(safe["DTB3"],dates,True)/100.0
    inv=(365.0*disc)/(360.0-91.0*disc)
    execution["safe_daily"]=(1.0+inv)**(1.0/365.0)-1.0
    execution["adv_dollars"]=stock["dollar_volume20"].copy()
    mask=(dates>=pd.Timestamp(start))&(dates<=pd.Timestamp(end))
    idx=np.flatnonzero(mask)
    if len(idx)<3:raise RuntimeError("empty G2 tape")
    # retain two future sessions in execution arrays so T -> T+1 -> T+2 can be evaluated.
    lo=int(idx[0]);hi=int(idx[-1])
    keep=np.arange(lo,min(hi+3,len(dates)))
    out_dates=dates[keep]
    stock2={k:v[keep] for k,v in stock.items()}
    sector2={k:v[keep] for k,v in sector.items()}
    market2={k:v[keep] for k,v in market.items()}
    execution2={k:v[keep] for k,v in execution.items()}
    return G2Tape(out_dates,tickers,stock2,sector2,market2,execution2)

def feature_registry(tape:G2Tape):
    return {"stock":tuple(sorted(tape.stock)),"sector":tuple(sorted(tape.sector)),
            "market":tuple(sorted(tape.market))}

def tape_audit(tape:G2Tape):
    out={"dates":len(tape.dates),"tickers":len(tape.tickers),"start":str(tape.dates[0].date()),
         "end":str(tape.dates[-1].date()),"features":feature_registry(tape),"coverage":{}}
    for scope,bank in (("stock",tape.stock),("sector",tape.sector),("market",tape.market)):
        for k,a in bank.items():
            z=np.asarray(a,float);out["coverage"][f"{scope}:{k}"]=float(np.mean(np.isfinite(z)))
    return out
