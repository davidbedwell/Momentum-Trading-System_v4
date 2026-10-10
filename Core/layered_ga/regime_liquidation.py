"""Causal regime transitions and forced liquidation horizon mapping.

A decision at close T enters at T+1 open. A DEFENSIVE designation at
close D exits an existing Normal position at D+1 open, never at D close.
No calendar dates are embedded in this production-facing module.
"""
import numpy as np

def forced_exit_horizons(decision_dates, security_ids, defensive_close_dates, requested_horizon):
    """Return executable horizon per decision row, or 0 for blocked entries.

    decision_dates: aligned close-decision dates per security, ordered by date
    defensive_close_dates: global causal controller transition close dates
    For any entry at the next open, first transition at/after decision close
    blocks entry when coincident; later transition truncates at its next open.
    The output is a number of trading sessions from entry to exit; -1 means
    there is no forced exit inside the requested horizon.
    """
    dates=np.asarray(decision_dates,dtype="datetime64[D]")
    ids=np.asarray(security_ids)
    transitions=np.sort(np.unique(np.asarray(defensive_close_dates,dtype="datetime64[D]")))
    if requested_horizon<1:raise ValueError("horizon")
    if len(dates)!=len(ids):raise ValueError("alignment")
    if len(transitions)==0:return np.full(len(dates),-1,dtype=int)
    result=np.full(len(dates),-1,dtype=int)
    for security in np.unique(ids):
        rows=np.flatnonzero(ids==security)
        rows=rows[np.argsort(dates[rows],kind="stable")]
        local_dates=dates[rows]
        if len(local_dates)!=len(np.unique(local_dates)):raise ValueError("duplicate security-date")
        transition_index=np.searchsorted(transitions,local_dates,side="left")
        for i,row in enumerate(rows):
            k=transition_index[i]
            if k==len(transitions):continue
            transition=transitions[k]
            if transition==local_dates[i]:
                result[row]=0
                continue
            # The execution is at the next session's open after the transition
            # close. Index distance equals the forward-path horizon index.
            j=np.searchsorted(local_dates,transition,side="left")
            if j==len(local_dates) or local_dates[j]!=transition:
                raise ValueError("missing security trading date for controller transition")
            h=j-i
            if h<=requested_horizon:result[row]=h
    return result

def select_executable_returns(paths,costs,side,decision_dates,security_ids,defensive_close_dates,horizon):
    """Return gross and round-trip cost per row at the forced/normal exit.

    Returns NaN for blocked entries. This routine assumes transitions are
    causally known at close and prices are executable at next open.
    """
    exit_h=forced_exit_horizons(decision_dates,security_ids,defensive_close_dates,horizon)
    n=len(exit_h)
    gross=np.full(n,np.nan);cost=np.full(n,np.nan)
    cm=costs.long_roundtrip if side.upper()=="LONG" else costs.short_roundtrip
    sign=1 if side.upper()=="LONG" else -1
    if side.upper() not in ("LONG","SHORT"):raise ValueError("side")
    for h in np.unique(exit_h):
        if h==0:continue
        target=horizon if h==-1 else int(h)
        if target>paths.endpoint_return.shape[1]:raise ValueError("missing path horizon")
        ix=np.flatnonzero(exit_h==h)
        gross[ix]=sign*paths.endpoint_return[ix,target-1]
        cost[ix]=cm[ix,target-1]
    return gross,cost,exit_h