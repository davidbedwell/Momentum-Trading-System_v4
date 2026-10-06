"""Production G2 fitness and registered MAP descriptors."""
from __future__ import annotations
import numpy as np,pandas as pd
from .g2fast import fast_simulate_g2

def _cagr_mdd(e):
    e=np.asarray(e,float);years=(len(e)-1)/252.0
    cagr=(e[-1]/e[0])**(1/max(years,1e-12))-1 if e[-1]>0 else -1.0
    peak=np.maximum.accumulate(e);mdd=np.min(e/peak-1.0)
    return float(cagr),float(mdd)

def _recovery_mask(tape):
    """J.2: SPY >=10% decline trough through recovery of the prior high."""
    dd=np.asarray(tape.market["spy_dd"],float);T=len(dd)-2;mask=np.zeros(T,bool)
    in_ep=False;trough=-1;trough_dd=0.0
    for i in range(len(dd)):
        x=dd[i]
        if not np.isfinite(x):continue
        if not in_ep and x<=-.10:in_ep=True;trough=i;trough_dd=x
        elif in_ep:
            if x<trough_dd:trough=i;trough_dd=x
            if x>=-1e-10:
                lo=max(0,trough-2);hi=min(T,i-1)
                if hi>=lo:mask[lo:hi+1]=True
                in_ep=False;trough=-1;trough_dd=0.0
    return mask

def make_g2_evaluator(tape):
    dates=pd.DatetimeIndex(tape.dates[2:])
    gfc=(dates>=pd.Timestamp("2007-10-09"))&(dates<=pd.Timestamp("2009-03-09"))
    rec=_recovery_mask(tape)
    spy=np.nan_to_num(np.asarray(tape.market["spy_ret1"],float)[2:2+len(dates)],nan=0.0)
    def evaluate(genome):
        equity,r,turn,safe,short,costs,gross,hhi=fast_simulate_g2(genome,tape)
        cagr,mdd=_cagr_mdd(equity)
        gfc_ret=float(np.prod(1+r[gfc])-1) if np.any(gfc) else 0.0
        if np.any(rec):
            mr=float(np.prod(1+r[rec])-1);sr=float(np.prod(1+spy[rec])-1)
            recovery=float(mr/sr) if abs(sr)>1e-12 else 0.0
        else:recovery=0.0
        return {"cagr":cagr,"mdd":mdd,"gross":float(np.mean(gross)),"safe_fraction":float(np.mean(safe)),
          "short_share":float(np.mean(short)),"turnover":float(np.mean(turn)),"holdings_hhi":float(np.mean(hhi)),
          "gfc_return":gfc_ret,"recovery_capture":recovery}
    return evaluate
