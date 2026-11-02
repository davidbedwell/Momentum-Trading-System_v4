"""Causal adapter for synthetic fsynth OHLCV; intentionally hides simulator regime."""
from dataclasses import dataclass
from pathlib import Path
import pandas as pd
import numpy as np

VISIBLE=("Date","Ticker","Open","High","Low","Close","Volume")

def load_fsynth(path):
    df=pd.read_parquet(Path(path)/"stock_prices.parquet")
    missing=set(VISIBLE)-set(df.columns)
    if missing: raise ValueError(f"missing fields: {missing}")
    df=df.loc[:,VISIBLE].copy()
    df["Date"]=pd.to_datetime(df["Date"])
    if df.duplicated(["Date","Ticker"]).any():raise ValueError("duplicate bars")
    if df[list(VISIBLE[2:6])].isna().any().any():raise ValueError("missing OHLC")
    if not np.isfinite(df[list(VISIBLE[2:6])].to_numpy()).all():raise ValueError("nonfinite prices")
    if (df[list(VISIBLE[2:6])]<=0).any().any():raise ValueError("nonpositive prices")
    if ((df["High"]<df[["Open","Close","Low"]].max(axis=1)) | (df["Low"]>df[["Open","Close","High"]].min(axis=1))).any():
        raise ValueError("invalid OHLC")
    return df.sort_values(["Date","Ticker"]).reset_index(drop=True)

def close_features_at(df,as_of,lookback=20):
    """Only bars dated <= as_of; lagged momentum and realized volatility."""
    now=pd.Timestamp(as_of)
    if lookback<2:raise ValueError("lookback")
    prior=df.loc[df["Date"]<=now,["Date","Ticker","Close"]]
    rows=[]
    for ticker,g in prior.groupby("Ticker",sort=True):
        p=g.sort_values("Date")["Close"].to_numpy(dtype=float)
        if len(p)<lookback+1:continue
        r=np.diff(np.log(p[-(lookback+1):]))
        rows.append({"Ticker":ticker,"as_of":str(now.date()),"momentum":float(p[-1]/p[-lookback-1]-1),"realized_volatility":float(r.std(ddof=1))})
    return pd.DataFrame(rows,columns=["Ticker","as_of","momentum","realized_volatility"])
