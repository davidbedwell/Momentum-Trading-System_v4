"""Causal partition-local feature tape for production replay."""
from __future__ import annotations
import numpy as np,pandas as pd
from .engine import partition_rank
from .peers import peer_indices

def build_tape(long_df:pd.DataFrame,tickers:tuple[str,...],start="2006-09-15",end="2026-09-14"):
    d=long_df[long_df.ticker.isin(tickers)].copy()
    if set(d.ticker.unique())-set(tickers):raise RuntimeError("partition contamination")
    fields={}
    for col in ("adj_close","open","high","low","close","volume","dividends"):
        fields[col]=d.pivot(index="date",columns="ticker",values=col).sort_index().reindex(columns=tickers)
    dates=fields["adj_close"].index
    px=fields["adj_close"].astype(float);ret=px.pct_change()
    mom20=px/px.shift(20)-1;mom63=px/px.shift(63)-1
    rv20=ret.rolling(20,min_periods=20).std(ddof=0)
    vrel=fields["volume"].astype(float)/fields["volume"].astype(float).rolling(20,min_periods=20).mean()
    rank_arrays={}
    for name,frame in (("mom20",mom20),("mom63",mom63),("rv20",rv20),("volume_rel20",vrel)):
        rank_arrays[name]=partition_rank(frame.to_numpy(float))
    stock={};group={}
    r=ret.fillna(0).to_numpy(float)
    for ti,dt in enumerate(dates):
        if ti<63:continue
        srow={};grow={}
        peers=peer_indices(r,ti,60,3)
        for j,t in enumerate(tickers):
            srow[t]={
              "mom20":float(np.nan_to_num(mom20.iloc[ti,j])),
              "mom63":float(np.nan_to_num(mom63.iloc[ti,j])),
              "rv20":float(np.nan_to_num(rv20.iloc[ti,j])),
              "volume_rel20":float(np.nan_to_num(vrel.iloc[ti,j])),
              "mom20_rank":float(rank_arrays["mom20"][ti,j]) if np.isfinite(rank_arrays["mom20"][ti,j]) else .5,
              "mom63_rank":float(rank_arrays["mom63"][ti,j]) if np.isfinite(rank_arrays["mom63"][ti,j]) else .5,
            }
            ps=peers[j]
            grow[t]={
              "peer_ret1":float(np.mean(r[ti,ps])) if len(ps) else 0.0,
              "peer_mom20":float(np.nanmean(mom20.iloc[ti,ps])) if len(ps) else 0.0,
            }
        stock[pd.Timestamp(dt)]=srow;group[pd.Timestamp(dt)]=grow
    mask=(dates>=pd.Timestamp(start))&(dates<=pd.Timestamp(end))
    eligible=[pd.Timestamp(x) for x in dates[mask] if pd.Timestamp(x) in stock]
    return {"dates":eligible,"stock":stock,"group":group,"fields":fields}
