"""Frozen-era and finalist diagnostic metrics."""
from __future__ import annotations
import numpy as np
ERAS=(("E1","2006-09-15","2011-09-14"),("E2","2011-09-15","2016-09-14"),("E3","2016-09-15","2021-09-14"),("E4","2021-09-15","2026-09-14"))
CONTINUOUS=("2006-09-15","2026-09-14")

def drawdowns(e):
    e=np.asarray(e,float);p=np.maximum.accumulate(e);return e/p-1
def cvar5(r):
    r=np.asarray(r,float);q=np.quantile(r,.05);return float(r[r<=q].mean())
def worst_rolling(r,n):
    r=np.asarray(r,float)
    if len(r)<n:return np.nan
    wealth=np.r_[1.0,np.cumprod(1+r)]
    vals=wealth[n:]/wealth[:-n]-1
    return float(vals.min())
def time_underwater(e):
    e=np.asarray(e,float);peak=np.maximum.accumulate(e);under=e<peak
    best=cur=0
    for z in under:cur=cur+1 if z else 0;best=max(best,cur)
    return int(best)
def recovery_sessions(e):
    e=np.asarray(e,float);dd=drawdowns(e);i=int(np.argmin(dd));pre=float(np.max(e[:i+1]))
    after=np.flatnonzero(e[i:]>=pre)
    return int(after[0]) if len(after) else None
def holdings_hhi(weights):
    a=np.asarray([abs(x) for x in weights],float);s=a.sum()
    return float(np.sum((a/s)**2)) if s else 0.0
def finalist_metrics(equity,turnover,safe_weight,short_share,session_returns,weights_by_session):
    e=np.asarray(equity,float);r=np.asarray(session_returns,float);dd=drawdowns(e)
    return {"cvar5":cvar5(r),"worst_day":float(r.min()),
      "worst_5":worst_rolling(r,5),"worst_10":worst_rolling(r,10),"worst_20":worst_rolling(r,20),
      "mdd":float(dd.min()),"drawdown_velocity":float(np.diff(dd).min()) if len(dd)>1 else 0.0,
      "time_underwater":time_underwater(e),"time_to_recovery":recovery_sessions(e),
      "turnover":float(np.mean(turnover)),"safe_fraction":float(np.mean(safe_weight)),
      "short_share":float(np.mean(short_share)),
      "holdings_hhi":float(np.mean([holdings_hhi(w.values()) for w in weights_by_session])) if weights_by_session else 0.0}
def reset_era_index(dates):
    import pandas as pd
    ds=pd.to_datetime(dates)
    out={}
    for name,a,b in ERAS:out[name]=np.flatnonzero((ds>=pd.Timestamp(a))&(ds<=pd.Timestamp(b)))
    return out
