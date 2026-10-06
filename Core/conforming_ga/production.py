"""Production evaluator shared by H.7 calibration and the certified GA."""
from __future__ import annotations
import numpy as np
from .simulator import simulate

def _cagr_mdd(equity:np.ndarray, sessions_per_year:float=252.0):
    e=np.asarray(equity,float)
    if len(e)<2 or not np.all(np.isfinite(e)) or e[0]<=0 or e[-1]<=0:
        return -1.0,-1.0
    years=(len(e)-1)/sessions_per_year
    cagr=float((e[-1]/e[0])**(1.0/max(years,1e-12))-1.0)
    peak=np.maximum.accumulate(e)
    mdd=float(np.min(e/peak-1.0))
    return cagr,mdd

def production_metrics(genome,sessions):
    """Frozen GA objectives plus the seven frozen MAP/novelty descriptors."""
    r=simulate(genome,sessions)
    cagr,mdd=_cagr_mdd(r.equity)
    signed_short=np.array([sum(abs(v) for v in w.values() if v<0) for w in r.weights],float)
    gross=np.array([sum(abs(v) for v in w.values()) for w in r.weights],float)
    hhi=[]
    for w in r.weights:
        a=np.array([abs(v) for v in w.values()],float); s=float(a.sum())
        hhi.append(float(np.sum((a/s)**2)) if s>0 else 0.0)
    # Episode descriptors are diagnostics only. Until episode masks are supplied by
    # the registered experiment controller, use neutral values rather than inventing labels.
    return {
      "cagr":cagr,"mdd":mdd,
      "gross":float(np.mean(gross)) if len(gross) else 0.0,
      "safe_fraction":float(np.mean(r.safe_weight)) if len(r.safe_weight) else 1.0,
      "short_share":float(np.mean(signed_short)) if len(signed_short) else 0.0,
      "turnover":float(np.mean(r.turnover)) if len(r.turnover) else 0.0,
      "holdings_hhi":float(np.mean(hhi)) if hhi else 0.0,
      "gfc_return":0.0,"recovery_capture":0.0,
    }

def evaluator_for_sessions(sessions):
    return lambda genome: production_metrics(genome,sessions)
