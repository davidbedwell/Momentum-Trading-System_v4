"""Real fold experiment assembly. Fails closed if mandatory PIT inputs are absent."""
from __future__ import annotations
from pathlib import Path
import pandas as pd,numpy as np
from .realdata import load_fold
from .external import load_spy,safe_daily_rate_asof
from .ofr import ofr_asof
from .availability import earnings_registry
from .tape import build_tape
from .simulator import SessionInput

def _load_long_from_fold_mirror(path:Path,tickers):
    frames=[]
    for t in tickers:
        p=path/f"{t}.parquet"
        if not p.is_file():raise FileNotFoundError(p)
        x=pd.read_parquet(p);x["ticker"]=t;frames.append(x)
    out=pd.concat(frames,ignore_index=True)
    if set(out.ticker)!=set(tickers):raise RuntimeError("fold mirror ticker mismatch")
    return out

def _market_tape(repo:Path,dates):
    spy=load_spy(repo).set_index("date").sort_index()
    c=spy.adj_close.astype(float);ret=c.pct_change();peak=c.cummax()
    out={}
    for dt in dates:
        if dt not in spy.index:continue
        i=spy.index.get_loc(dt)
        if not isinstance(i,(int,np.integer)) or i<20:continue
        out[dt]={
          "spy_ret_5":float(c.iloc[i]/c.iloc[i-5]-1),
          "spy_ret_20":float(c.iloc[i]/c.iloc[i-20]-1),
          "spy_dd":float(c.iloc[i]/peak.iloc[i]-1),
          "spy_vol_20":float(ret.iloc[i-19:i+1].std(ddof=0)),
          "ofr_fsi":float(ofr_asof(repo,dt)),
        }
    return out

def _earnings_tape(repo:Path,tickers,dates):
    p=earnings_registry(repo)
    if p is None:raise RuntimeError("MANDATORY_PIT_EARNINGS_REGISTRY_MISSING")
    d=pd.read_parquet(p) if p.suffix==".parquet" else pd.read_csv(p)
    required={"ticker","effective_date"}
    if not required.issubset(d.columns):raise RuntimeError("earnings registry schema")
    d=d[d.ticker.isin(tickers)].copy();d["effective_date"]=pd.to_datetime(d["effective_date"])
    feature_cols=[x for x in d.columns if x not in ("ticker","effective_date")]
    out={}
    for dt in dates:
        row={}
        x=d[d.effective_date<=dt].sort_values("effective_date")
        for t in tickers:
            z=x[x.ticker==t]
            row[t]={k:float(z.iloc[-1][k]) if len(z) and pd.notna(z.iloc[-1][k]) else 0.0 for k in feature_cols}
        out[dt]=row
    return out

def build_fold_sessions(repo:Path,fold_root:Path,fold:int,mode:str):
    tr,bl=load_fold(repo,fold);tickers=tr if mode=="train" else bl
    path=fold_root/f"fold{fold}"/mode
    long=_load_long_from_fold_mirror(path,tickers)
    tape=build_tape(long,tickers)
    earnings=_earnings_tape(repo,tickers,tape["dates"])
    market=_market_tape(repo,tape["dates"])
    fields=tape["fields"];dates=tape["dates"];sessions=[]
    date_index=list(fields["open"].index)
    for dt in dates:
        if dt not in market:continue
        idx=date_index.index(dt)
        if idx+2>=len(date_index):continue
        d1=date_index[idx+1];d2=date_index[idx+2]
        stock={t:{**tape["stock"][dt][t],**earnings[dt][t]} for t in tickers}
        def row(field,date):return {t:float(fields[field].loc[date,t]) for t in tickers}
        div=row("dividends",d2)
        sessions.append(SessionInput(
          when=dt.date().isoformat(),market=market[dt],sector=tape["group"][dt],stock=stock,
          open_t1=row("open",d1),open_t2=row("open",d2),high_t=row("high",dt),low_t=row("low",dt),
          close_t=row("close",dt),volume_t=row("volume",dt),dividends_t1_t2=div,
          daily_safe=float(safe_daily_rate_asof(repo,dt,1)),daily_borrow={t:.003/365.0 for t in tickers}))
    return sessions
