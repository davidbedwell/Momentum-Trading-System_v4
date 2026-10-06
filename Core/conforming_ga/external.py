"""Registered external market/SAFE sources, isolated from stock outcome arrays."""
from __future__ import annotations
from pathlib import Path
import hashlib,pandas as pd,numpy as np

SPY_PATH=Path("Research/Data/Comparators/SPY_YFINANCE_2005_2026.parquet")
SAFE_PATH=Path("Research/Data/SAFE/DTB3_FRED_2005_2026.csv")
SPY_SHA256="b182402afd15c074ee4cc596149bf0a821e6cbd00fa5329d84eef269636f6381"
SAFE_SHA256="f7d5d40d4b1f6e0545b4898c04faa08cad34d30de8708ca3278212a1a508f1db"

def sha256(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()

def load_spy(repo:Path)->pd.DataFrame:
    p=repo/SPY_PATH
    if sha256(p)!=SPY_SHA256: raise RuntimeError("SPY registry hash mismatch")
    d=pd.read_parquet(p).copy();d["date"]=pd.to_datetime(d["date"])
    return d.sort_values("date")

def load_safe(repo:Path)->pd.DataFrame:
    p=repo/SAFE_PATH
    if sha256(p)!=SAFE_SHA256: raise RuntimeError("SAFE registry hash mismatch")
    d=pd.read_csv(p);d["observation_date"]=pd.to_datetime(d["observation_date"])
    d["DTB3"]=pd.to_numeric(d["DTB3"],errors="coerce")
    return d.sort_values("observation_date")

def safe_daily_rate_asof(repo:Path,decision_date,publication_lag_sessions:int=1)->float:
    """Use only an observation published before decision date by >= one session.
    DTB3 is a bank-discount annualized yield; convert to investment-style daily accrual.
    """
    d=load_safe(repo).dropna()
    dt=pd.Timestamp(decision_date)
    prior=d[d.observation_date < dt] if publication_lag_sessions>=1 else d[d.observation_date<=dt]
    if prior.empty:return np.nan
    disc=float(prior.iloc[-1].DTB3)/100.0
    # Approximate 3m bill investment yield from bank discount yield with 91-day convention.
    inv=(365.0*disc)/(360.0-91.0*disc)
    return (1.0+inv)**(1.0/365.0)-1.0

def spy_market_features(repo:Path,decision_date)->dict[str,float]:
    d=load_spy(repo)
    dt=pd.Timestamp(decision_date); x=d[d.date<=dt].copy()
    if len(x)<253:return {}
    c=x.adj_close.astype(float)
    r=c.pct_change()
    peak=c.cummax()
    return {
      "spy_ret_5":float(c.iloc[-1]/c.iloc[-6]-1),
      "spy_ret_20":float(c.iloc[-1]/c.iloc[-21]-1),
      "spy_dd":float(c.iloc[-1]/peak.iloc[-1]-1),
      "spy_vol_20":float(r.tail(20).std(ddof=0)),
    }
