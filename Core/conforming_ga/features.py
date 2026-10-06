"""Partition-local causal feature construction from permitted per-ticker histories."""
from __future__ import annotations
import pandas as pd,numpy as np
from .engine import partition_rank,trailing_peer_context

def panel_from_long(long_df:pd.DataFrame,tickers:tuple[str,...],field:str)->pd.DataFrame:
    x=long_df[long_df.ticker.isin(tickers)].pivot(index="date",columns="ticker",values=field).sort_index()
    return x.reindex(columns=list(tickers))

def causal_stock_features(long_df:pd.DataFrame,tickers:tuple[str,...],decision_date)->dict[str,dict[str,float]]:
    """Only the supplied partition and rows <= T can influence output."""
    d=long_df[(long_df.ticker.isin(tickers)) & (pd.to_datetime(long_df.date)<=pd.Timestamp(decision_date))].copy()
    if set(d.ticker.unique())-set(tickers):raise RuntimeError("partition contamination")
    px=panel_from_long(d,tickers,"adj_close").astype(float)
    vol=panel_from_long(d,tickers,"volume").astype(float)
    if len(px)<64:return {t:{} for t in tickers}
    ret1=px.pct_change()
    mom20=px.iloc[-1]/px.iloc[-21]-1
    mom63=px.iloc[-1]/px.iloc[-64]-1
    rv20=ret1.tail(20).std(ddof=0)
    vrel=vol.iloc[-1]/vol.tail(20).mean()
    # Cross-sectional transforms are built *after* partition selection.
    raw=np.vstack([mom20.values,mom63.values,rv20.values,vrel.values])
    ranks=partition_rank(raw)
    peer=trailing_peer_context(ret1.tail(64).fillna(0).values,window=20,k=min(3,max(1,len(tickers)-1)))
    peer_last=peer[-1] if len(peer) else np.full(len(tickers),np.nan)
    out={}
    for i,t in enumerate(tickers):
        out[t]={
          "mom20":float(mom20.iloc[i]) if np.isfinite(mom20.iloc[i]) else 0.0,
          "mom63":float(mom63.iloc[i]) if np.isfinite(mom63.iloc[i]) else 0.0,
          "rv20":float(rv20.iloc[i]) if np.isfinite(rv20.iloc[i]) else 0.0,
          "volume_rel20":float(vrel.iloc[i]) if np.isfinite(vrel.iloc[i]) else 0.0,
          "mom20_rank":float(ranks[0,i]) if np.isfinite(ranks[0,i]) else 0.5,
          "mom63_rank":float(ranks[1,i]) if np.isfinite(ranks[1,i]) else 0.5,
          "rv20_rank":float(ranks[2,i]) if np.isfinite(ranks[2,i]) else 0.5,
          "volume_rel20_rank":float(ranks[3,i]) if np.isfinite(ranks[3,i]) else 0.5,
          "peer_ret1":float(peer_last[i]) if np.isfinite(peer_last[i]) else 0.0,
        }
    return out
