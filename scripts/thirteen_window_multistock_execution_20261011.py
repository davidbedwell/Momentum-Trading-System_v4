"""Multi-stock close-decision / next-open portfolio ledger; fail closed on R-1 tape.
Oracle peak+10 to trough+10 forces liquidation; R-1 permits next-open reentry.
This is a portfolio execution layer, not GA fitness certification.
"""
import numpy as np
import pandas as pd
from scripts.thirteen_window_regime_execution_20261011 import regime_tape

def simulate(target_weights,open_returns,cash_returns,calendar,episodes,r1_normal_close,*,cost_bps=5,offset=10):
    target=np.asarray(target_weights,float);returns=np.asarray(open_returns,float)
    cash=np.asarray(cash_returns,float)
    if target.ndim!=2 or returns.shape!=target.shape:raise ValueError('stock panel shape mismatch')
    n,m=target.shape
    if len(calendar)!=n or cash.shape!=(n,):raise ValueError('calendar/cash mismatch')
    if not np.isfinite(target).all() or not np.isfinite(returns[:-1]).all() or not np.isfinite(cash[:-1]).all():raise ValueError('nonfinite inputs')
    if np.any(target<0) or np.any(target.sum(axis=1)>1+1e-10) or cost_bps<0:raise ValueError('invalid long-only target/cost')
    excluded,eligible=regime_tape(calendar,episodes,r1_normal_close,offset)
    holdings=np.zeros((n,m));turnover=np.zeros(n);pnl=np.zeros(n);forced=np.zeros(n,dtype=bool)
    for t in range(n-1):
        w=target[t-1] if t and eligible[t-1] and eligible[t] else np.zeros(m)
        holdings[t]=w
        old=holdings[t-1] if t else np.zeros(m)
        turnover[t]=np.abs(w-old).sum()
        forced[t]=bool(excluded[t] and old.sum()>0 and w.sum()==0)
        pnl[t]=np.dot(w,returns[t])+(1-w.sum())*cash[t]-turnover[t]*cost_bps/10000
    return {'returns':pnl,'weights':holdings,'turnover':turnover,'forced_liquidation':forced,'excluded':excluded,'normal_eligible':eligible}
