"""PIT publication and execution/cost semantics."""
from __future__ import annotations
import numpy as np

def published_value(obs_dates,values,publication_dates,t):
    obs_dates=np.asarray(obs_dates); publication_dates=np.asarray(publication_dates); values=np.asarray(values)
    ok=publication_dates<=t
    if not np.any(ok): return np.nan
    idx=np.flatnonzero(ok)[-1]
    return values[idx]

def next_open_return(open_px:np.ndarray,t:int)->np.ndarray:
    """Close-T decision executes T+1 open; realized next interval is T+1 open→T+2 open."""
    o=np.asarray(open_px,float)
    if t+2>=len(o): raise IndexError(t)
    return o[t+2]/o[t+1]-1.0

def portfolio_metrics(equity:np.ndarray,turnover:np.ndarray,safe_weight:np.ndarray)->dict:
    e=np.asarray(equity,float); tr=np.asarray(turnover,float); sw=np.asarray(safe_weight,float)
    peak=np.maximum.accumulate(e); dd=e/peak-1
    return {"total_return":float(e[-1]/e[0]-1),"mdd":float(dd.min()),"turnover":float(tr.mean()),"safe_fraction":float(sw.mean())}
