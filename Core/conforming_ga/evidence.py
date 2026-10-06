"""G.6 effective-evidence and G.7 finalist diagnostics without unapproved guard thresholds."""
from __future__ import annotations
import numpy as np
from .metrics import finalist_metrics

def newey_west_effective_n(x,max_lag:int|None=None)->float:
    x=np.asarray(x,float);x=x[np.isfinite(x)];n=len(x)
    if n<2:return float(n)
    z=x-x.mean();var=float(np.dot(z,z)/n)
    if var<=0:return float(n)
    L=max_lag if max_lag is not None else max(1,int(round(4*(n/100)**(2/9))))
    vif=1.0
    for lag in range(1,min(L,n-1)+1):
        cov=float(np.dot(z[lag:],z[:-lag])/n)
        rho=cov/var;w=1-lag/(L+1);vif+=2*w*rho
    return float(n/max(vif,1e-12))

def effective_stocks(pnl_by_stock):
    a=np.abs(np.asarray(pnl_by_stock,float));s=a.sum()
    if s<=0:return 0.0
    sh=a/s;return float(1/np.sum(sh*sh))

def effective_bets(holding_returns):
    x=np.asarray(holding_returns,float)
    if x.ndim!=2 or x.shape[1]==0:return 0.0
    c=np.cov(np.nan_to_num(x),rowvar=False)
    if np.ndim(c)==0:return 1.0
    eig=np.linalg.eigvalsh(c);eig=np.maximum(eig,0);s=eig.sum()
    return float(s*s/np.sum(eig*eig)) if np.sum(eig*eig)>0 else 0.0

def cross_era_recurrence(contribs):
    x=np.asarray(contribs,float)
    return {"positive_eras":int(np.sum(x>0)),"negative_eras":int(np.sum(x<0)),
            "mean":float(np.mean(x)) if len(x) else np.nan,"std":float(np.std(x)) if len(x) else np.nan}

def cross_stock_transport(train_metric:float,blind_metric:float):
    return {"train":float(train_metric),"blind":float(blind_metric),"delta":float(blind_metric-train_metric)}

def trial_multiplicity(behaviors,tol:float=1e-9):
    """Report exact behavioral uniqueness; no threshold enters fitness."""
    arr=np.asarray(behaviors,float)
    if len(arr)==0:return 0
    rounded=np.round(arr/max(tol,1e-15))*max(tol,1e-15)
    return int(np.unique(rounded,axis=0).shape[0])

def full_evidence(*,session_returns,equity,turnover,safe_weight,short_share,weights_by_session,
                  stock_sessions:int,trades:int,pnl_by_stock,holding_returns,sector_pnl,
                  episode_records,era_contributions,train_metric,blind_metric,behavior_matrix):
    diag=finalist_metrics(equity,turnover,safe_weight,short_share,session_returns,weights_by_session)
    sectors=sum(1 for v in sector_pnl.values() if v!=0)
    return {
      "raw_n":{"sessions":int(len(session_returns)),"stock_sessions":int(stock_sessions),"trades":int(trades)},
      "effective_n_sessions_newey_west":newey_west_effective_n(session_returns),
      "effective_stocks":effective_stocks(pnl_by_stock),
      "effective_bets":effective_bets(holding_returns),
      "sectors_contributing_nonzero":int(sectors),
      "episodes":int(len(episode_records)),
      "cross_era_recurrence":cross_era_recurrence(era_contributions),
      "cross_stock_transport":cross_stock_transport(train_metric,blind_metric),
      "trial_multiplicity_exact_behavioral":trial_multiplicity(behavior_matrix),
      "diagnostics":diag,
    }
