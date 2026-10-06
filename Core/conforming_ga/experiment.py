"""Real fold experiment assembly. Fails closed if mandatory PIT inputs are absent."""
from __future__ import annotations
from pathlib import Path
import pandas as pd,numpy as np
from .realdata import load_fold
from .external import load_spy,load_safe
from .ofr import load_ofr
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
    ofr=load_ofr(repo).set_index("Date").sort_index()
    c=spy.adj_close.astype(float);ret=c.pct_change();peak=c.cummax()
    odates=ofr.index.to_numpy(dtype="datetime64[ns]")
    out={}
    for dt in dates:
        if dt not in spy.index:continue
        i=spy.index.get_loc(dt)
        if not isinstance(i,(int,np.integer)) or i<20:continue
        oi=int(np.searchsorted(odates,np.datetime64(pd.Timestamp(dt)),"left"))-1
        if oi<0:continue
        out[dt]={
          "spy_ret_5":float(c.iloc[i]/c.iloc[i-5]-1),
          "spy_ret_20":float(c.iloc[i]/c.iloc[i-20]-1),
          "spy_dd":float(c.iloc[i]/peak.iloc[i]-1),
          "spy_vol_20":float(ret.iloc[i-19:i+1].std(ddof=0)),
          "ofr_fsi":float(ofr.iloc[oi]["OFR FSI"]),
        }
    return out

def _safe_tape(repo:Path,dates):
    d=load_safe(repo).dropna().set_index("observation_date").sort_index()
    idx=d.index.to_numpy(dtype="datetime64[ns]"); vals=d["DTB3"].to_numpy(float)
    out={}
    for dt in dates:
        i=int(np.searchsorted(idx,np.datetime64(pd.Timestamp(dt)),"left"))-1
        if i<0:continue
        disc=float(vals[i])/100.0
        inv=(365.0*disc)/(360.0-91.0*disc)
        out[pd.Timestamp(dt)]=(1.0+inv)**(1.0/365.0)-1.0
    return out

def _earnings_tape(repo:Path,tickers,dates):
    p=earnings_registry(repo)
    if p is None:raise RuntimeError("MANDATORY_PIT_EARNINGS_REGISTRY_MISSING")
    d=pd.read_parquet(p) if p.suffix==".parquet" else pd.read_csv(p)
    required={"ticker","effective_date"}
    if not required.issubset(d.columns):raise RuntimeError("earnings registry schema")
    d=d[d.ticker.isin(tickers)].copy();d["effective_date"]=pd.to_datetime(d["effective_date"])
    feature_cols=[x for x in d.columns if x not in ("ticker","security_id","effective_date")]
    if d.duplicated(["effective_date","ticker"]).any(): raise RuntimeError("duplicate earnings clock identity")
    wanted={pd.Timestamp(x) for x in dates}
    d=d[d.effective_date.isin(wanted)]
    zero={k:0.0 for k in feature_cols};out={}
    grouped={pd.Timestamp(dt):g for dt,g in d.groupby("effective_date",sort=False)}
    for dt in dates:
        ts=pd.Timestamp(dt); g=grouped.get(ts)
        row={t:dict(zero) for t in tickers}
        if g is not None:
            for rec in g.itertuples(index=False):
                vals={k:(float(getattr(rec,k)) if pd.notna(getattr(rec,k)) else 0.0) for k in feature_cols}
                row[rec.ticker]=vals
        out[ts]=row
    return out

def build_fold_sessions(repo:Path,fold_root:Path,fold:int,mode:str):
    tr,bl=load_fold(repo,fold);tickers=tr if mode=="train" else bl
    path=fold_root/f"fold{fold}"/mode
    long=_load_long_from_fold_mirror(path,tickers)
    tape=build_tape(long,tickers)
    earnings=_earnings_tape(repo,tickers,tape["dates"])
    market=_market_tape(repo,tape["dates"])
    safe=_safe_tape(repo,tape["dates"])
    fields=tape["fields"];dates=tape["dates"];sessions=[]
    date_index=list(fields["open"].index);pos={pd.Timestamp(x):i for i,x in enumerate(date_index)}
    arrays={name:frame.to_numpy(float) for name,frame in fields.items()}
    adv20=(fields["close"].astype(float)*fields["volume"].astype(float)).rolling(20,min_periods=20).mean().to_numpy(float)
    def row_at(field,i): return dict(zip(tickers,arrays[field][i].astype(float)))
    def adv_at(i): return dict(zip(tickers,np.nan_to_num(adv20[i],nan=0.0).astype(float)))
    borrow={t:.003/365.0 for t in tickers}
    for dt in dates:
        if dt not in market:continue
        idx=pos[pd.Timestamp(dt)]
        if idx+2>=len(date_index):continue
        stock={t:{**tape["stock"][dt][t],**earnings[dt][t]} for t in tickers}
        sessions.append(SessionInput(
          when=dt.date().isoformat(),market=market[dt],sector=tape["group"][dt],stock=stock,
          open_t1=row_at("open",idx+1),open_t2=row_at("open",idx+2),high_t=row_at("high",idx),low_t=row_at("low",idx),
          close_t=row_at("close",idx),volume_t=row_at("volume",idx),dividends_t1_t2=row_at("dividends",idx+2),
          daily_safe=float(safe[dt]),daily_borrow=dict(borrow),adv_dollars_t=adv_at(idx),
          execute_when=pd.Timestamp(date_index[idx+1]).date().isoformat(),
          calendar_days=int((pd.Timestamp(date_index[idx+2])-pd.Timestamp(date_index[idx+1])).days)))
    return sessions
