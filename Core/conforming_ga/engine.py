"""Clean MTS conforming simulator primitives.

Independent implementation.  Deliberately does not import the invalid
2026-10-05/06 runner or its feature builder.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
import numpy as np

class AllocationMode(str, Enum):
    EQUAL="equal"; STRENGTH="strength"; UNCERTAINTY="uncertainty"; DOWNSIDE="downside"

@dataclass(frozen=True)
class Opportunity:
    value: float
    uncertainty: float = 0.0
    downside: float = 0.0

@dataclass(frozen=True)
class Move:
    source: str
    destination: str
    amount: float
    net_gain: float
    label: str

def partition_rank(x: np.ndarray) -> np.ndarray:
    """Row-wise percentile rank using only columns supplied by this partition."""
    x=np.asarray(x,float)
    out=np.full_like(x,np.nan)
    for t,row in enumerate(x):
        ok=np.isfinite(row); vals=row[ok]
        if vals.size:
            order=np.argsort(vals,kind="mergesort")
            ranks=np.empty(vals.size,float); ranks[order]=(np.arange(vals.size)+0.5)/vals.size
            out[t,ok]=ranks
    return out

def trailing_peer_context(returns: np.ndarray, window: int=20, k: int=3) -> np.ndarray:
    """Causal peer mean: peers are chosen solely among supplied partition columns."""
    r=np.asarray(returns,float); T,N=r.shape
    out=np.full((T,N),np.nan)
    for t in range(T):
        if t < window: continue
        hist=r[t-window:t+1]
        corr=np.corrcoef(np.nan_to_num(hist,nan=0.0),rowvar=False)
        for i in range(N):
            c=corr[i].copy(); c[i]=-np.inf
            peers=np.argsort(c)[-min(k,max(0,N-1)):]
            out[t,i]=np.nanmean(r[t,peers]) if peers.size else 0.0
    return out

def absolute_claims(opportunities: dict[str,Opportunity], safe_value: float,
                    mode: AllocationMode) -> dict[str,float]:
    """Absolute risky claims versus SAFE. Weak opportunity is not normalized upward."""
    edge={k:max(0.0,v.value-safe_value) for k,v in opportunities.items()}
    if mode is AllocationMode.EQUAL:
        raw={k:(1.0 if e>0 else 0.0) for k,e in edge.items()}
        n=sum(raw.values()); raw={k:(v/n if n else 0.0) for k,v in raw.items()}
        # absolute opportunity still gates gross exposure
        gross=min(1.0,max(edge.values(),default=0.0))
        return {k:v*gross for k,v in raw.items()}
    if mode is AllocationMode.STRENGTH:
        raw=edge
    elif mode is AllocationMode.UNCERTAINTY:
        raw={k:e/max(1e-12,1.0+opportunities[k].uncertainty) for k,e in edge.items()}
    elif mode is AllocationMode.DOWNSIDE:
        raw={k:e/max(1e-12,1.0+opportunities[k].downside) for k,e in edge.items()}
    else: raise ValueError(mode)
    gross=sum(abs(v) for v in raw.values())
    scale=1.0/max(1.0,gross)
    return {k:v*scale for k,v in raw.items()}

def target_weights(long_ops: dict[str,Opportunity], short_ops: dict[str,Opportunity],
                   safe_value: float, mode: AllocationMode) -> dict[str,float]:
    longs=absolute_claims(long_ops,safe_value,mode)
    shorts=absolute_claims(short_ops,safe_value,mode)
    raw={**longs}
    for k,v in shorts.items(): raw[k]=raw.get(k,0.0)-v
    gross=sum(abs(v) for v in raw.values())
    if gross>1: raw={k:v/gross for k,v in raw.items()}
    return raw

def unified_moves(prev: dict[str,float], target: dict[str,float],
                  values: dict[str,float], safe_value: float,
                  friction: float, uncertainty_hurdle: float=0.0) -> tuple[dict[str,float],list[Move]]:
    """Greedy source→destination economic movement ledger bounded toward targets."""
    names=sorted(set(prev)|set(target))
    cur={k:float(prev.get(k,0.0)) for k in names}
    desired={k:float(target.get(k,0.0)) for k in names}
    moves=[]
    # Represent signed positions as economic destinations; SAFE is residual.
    def destination_value(k,w):
        return values.get(k,0.0) * (1.0 if w>=0 else -1.0)
    # reductions/exits create SAFE capital only when SAFE beats incumbent by hurdle
    for k in names:
        p,t=cur[k],desired[k]
        if p!=0 and (t==0 or np.sign(t)!=np.sign(p) or abs(t)<abs(p)):
            amt=abs(p) if (t==0 or np.sign(t)!=np.sign(p)) else abs(p)-abs(t)
            gain=safe_value-destination_value(k,p)-friction-uncertainty_hurdle
            if gain>0:
                cur[k]=p-np.sign(p)*amt
                label="EXIT_TO_SAFE" if abs(cur[k])<1e-15 else "CONTINUE"
                moves.append(Move(k,"SAFE",amt,gain,label))
    # Direct incumbent→challenger replacements are evaluated before SAFE-funded
    # entries.  A replacement is one economic move, not two independently gated legs.
    donors=[k for k in names if abs(cur[k])>abs(desired[k])+1e-15]
    receivers=[k for k in names if abs(cur[k])<abs(desired[k])-1e-15]
    pairs=[]
    for a in donors:
        for b in receivers:
            gain=destination_value(b,desired[b])-destination_value(a,cur[a])-friction-uncertainty_hurdle
            pairs.append((gain,a,b))
    for gain,a,b in sorted(pairs,reverse=True):
        if gain<=0: continue
        amt=min(abs(cur[a])-abs(desired[a]),abs(desired[b])-abs(cur[b]))
        if amt<=0: continue
        cur[a]-=np.sign(cur[a])*amt; cur[b]+=np.sign(desired[b])*amt
        moves.append(Move(a,b,amt,gain,"REPLACE"))
    # Remaining SAFE funds economically justified entries/increases.
    gross=sum(abs(v) for v in cur.values()); available=max(0.0,1.0-gross)
    candidates=[]
    for k in names:
        p,t=cur[k],desired[k]
        same=(p==0 or np.sign(p)==np.sign(t))
        need=max(0.0,abs(t)-abs(p)) if same else abs(t)
        if need:
            gain=destination_value(k,t)-safe_value-friction-uncertainty_hurdle
            candidates.append((gain,k,need,t))
    for gain,k,need,t in sorted(candidates,reverse=True):
        if gain<=0 or available<=0: continue
        amt=min(need,available); old=cur[k]
        cur[k]=old + np.sign(t)*amt; available-=amt
        label=("SHORT" if old==0 and t<0 else "ENTER" if old==0 else "CONTINUE")
        moves.append(Move("SAFE",k,amt,gain,label))
    # numerical gross invariant
    assert sum(abs(v) for v in cur.values()) <= 1.0+1e-12
    return cur,moves

def transaction_cost(delta_notional: float, bps: float, regulatory_sell: float=0.0,
                     is_sell: bool=False) -> float:
    return abs(delta_notional)*bps/10000.0 + (abs(delta_notional)*regulatory_sell if is_sell else 0.0)

def borrow_cost(short_notional: float, annual_rate: float, calendar_days: int) -> float:
    return abs(short_notional)*annual_rate*calendar_days/365.0
