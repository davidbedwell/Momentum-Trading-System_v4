"""Literal frozen F.2 claim construction, isolated for auditability."""
from __future__ import annotations
from .engine import AllocationMode, Opportunity

def frozen_claims(opportunities: dict[str,Opportunity], mode: AllocationMode, *,
                  tau: float, q: float, gamma: float, eta: float) -> dict[str,float]:
    if not 0.0 <= tau <= 1.0: raise ValueError("tau")
    if gamma <= 0 or eta < 0: raise ValueError("parameters")
    edge={k:max(0.0,v.value-q) for k,v in opportunities.items()}
    if mode is AllocationMode.EQUAL:
        g={k:(eta if opportunities[k].value>q else 0.0) for k in opportunities}
    elif mode is AllocationMode.STRENGTH:
        g={k:e**gamma for k,e in edge.items()}
    elif mode is AllocationMode.UNCERTAINTY:
        g={k:((e/max(1e-12,opportunities[k].uncertainty))**gamma if e>0 else 0.0) for k,e in edge.items()}
    elif mode is AllocationMode.DOWNSIDE:
        g={k:((e/max(1e-12,opportunities[k].downside))**gamma if e>0 else 0.0) for k,e in edge.items()}
    else: raise ValueError(mode)
    r={k:tau*v for k,v in g.items()}
    G=sum(abs(v) for v in r.values())
    return ({k:v/G for k,v in r.items()} if G>1.0 else r)
