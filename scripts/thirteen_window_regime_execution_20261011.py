"""Causal execution ledger for oracle crash boundary plus R-1 reentry.

Daily decision at close t executes at open t+1; boundary liquidation occurs
at the boundary open. Uses supplied open-to-open returns and daily cash rates.
No heldout data access, no lookahead to subsequent R-1 states.
"""
import numpy as np
import pandas as pd
from Core.layered_ga.ga4_oracle_crash_mask import frozen_episode_intervals

def regime_tape(calendar,episodes,r1_normal_close,offset=10):
    dates=pd.DatetimeIndex(pd.to_datetime(calendar)).normalize()
    if not dates.is_monotonic_increasing or dates.has_duplicates:raise ValueError('calendar must be sorted and unique')
    r1=np.asarray(r1_normal_close,dtype=bool)
    if len(r1)!=len(dates):raise ValueError('R-1 tape length mismatch')
    excluded=np.zeros(len(dates),dtype=bool)
    for a,b in frozen_episode_intervals(dates,episodes,offset):excluded|=(dates>=a)&(dates<=b)
    # Release only after R-1 confirmation following exclusion; an earlier
    # confirmation does not bypass the crash exclusion interval.
    eligible=np.zeros(len(dates),dtype=bool)
    defensive=False
    for t in range(len(dates)):
        if excluded[t]:defensive=True
        elif defensive and r1[t]:defensive=False
        eligible[t]=not defensive
    return excluded,eligible

def simulate(targets,open_returns,cash_returns,calendar,episodes,r1_normal_close,cost_bps=5,offset=10):
    """Single-position Normal portfolio with forced cash and next-open orders.

    targets[t] is the desired Normal exposure decided at close t, for open t+1.
    open_returns[t] is open t -> open t+1 realized return; cash_returns[t]
    covers the same interval. The last session has no executable next open.
    """
    dates=pd.DatetimeIndex(pd.to_datetime(calendar)).normalize()
    target=np.asarray(targets,float);ret=np.asarray(open_returns,float);cash=np.asarray(cash_returns,float)
    n=len(dates)
    if not (len(target)==len(ret)==len(cash)==n):raise ValueError('input length mismatch')
    if not (np.isfinite(target).all() and np.isfinite(ret[:-1]).all() and np.isfinite(cash[:-1]).all()):raise ValueError('nonfinite inputs')
    if np.any((target<0)|(target>1)) or cost_bps<0:raise ValueError('invalid allocation or costs')
    excluded,eligible=regime_tape(dates,episodes,r1_normal_close,offset)
    weights=np.zeros(n);turnover=np.zeros(n);pnl=np.zeros(n);forced=np.zeros(n,dtype=bool)
    # Exposure at each open: a decision from previous close may only execute
    # if the receiving session is outside the crash window and R-1 released.
    for t in range(n-1):
        if t==0:
            desired=0.0
        else:
            desired=float(target[t-1]) if eligible[t-1] and eligible[t] else 0.0
        weights[t]=desired
        previous=weights[t-1] if t else 0.0
        turnover[t]=abs(desired-previous)
        forced[t]=bool(previous>0 and excluded[t] and desired==0)
        pnl[t]=desired*ret[t]+(1-desired)*cash[t]-turnover[t]*cost_bps/10000
    return {'returns':pnl,'exposure':weights,'turnover':turnover,'forced_liquidation':forced,'excluded':excluded,'normal_eligible':eligible}
