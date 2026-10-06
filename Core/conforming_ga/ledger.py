"""Literal frozen E.4 source-to-destination ledger."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class AssetState:
    value: float
    uncertainty: float=0.0
    exit_cost: float=0.0
    entry_cost: float=0.0

@dataclass(frozen=True)
class LedgerMove:
    source:str; destination:str; amount:float; net_gain:float; label:str

def hurdle_gain(a:AssetState,b:AssetState,kappa:float,lambda_u:float)->float:
    return b.value-a.value-kappa*(a.exit_cost+b.entry_cost)-lambda_u*(a.uncertainty+b.uncertainty)

def move_ledger(prev:dict[str,float], target:dict[str,float], states:dict[str,AssetState],
                *,kappa:float,lambda_u:float)->tuple[dict[str,float],list[LedgerMove]]:
    names=sorted(set(prev)|set(target))
    safe=states.get("SAFE",AssetState(0.0))
    st={**states,"SAFE":safe}
    cur={k:float(prev.get(k,0.0)) for k in names}; want={k:float(target.get(k,0.0)) for k in names}
    moves=[]
    # Sources are excess absolute capital; destinations are deficits, with SAFE as residual.
    def excess(k): return max(0.0,abs(cur[k])-abs(want[k]))
    def deficit(k): return max(0.0,abs(want[k])-abs(cur[k]))
    # Iteratively execute globally best positive net-gain move.
    while True:
        gross=sum(abs(v) for v in cur.values()); safe_now=max(0.0,1.0-gross)
        safe_want=max(0.0,1.0-sum(abs(v) for v in want.values()))
        sources=[(k,excess(k)) for k in names if excess(k)>1e-15]
        if safe_now>safe_want+1e-15:sources.append(("SAFE",safe_now-safe_want))
        dests=[(k,deficit(k)) for k in names if deficit(k)>1e-15]
        if safe_now<safe_want-1e-15:dests.append(("SAFE",safe_want-safe_now))
        cand=[]
        for a,ea in sources:
            for b,db in dests:
                if a==b:continue
                g=hurdle_gain(st[a],st[b],kappa,lambda_u)
                if g>0:cand.append((g,a,b,min(ea,db)))
        if not cand:break
        g,a,b,amt=max(cand,key=lambda z:(z[0],z[1],z[2]))
        if a!="SAFE":cur[a]-=np.sign(cur[a])*amt
        if b!="SAFE":
            sign=np.sign(want[b]) if want[b]!=0 else 1.0
            cur[b]+=sign*amt
        if a=="SAFE": label="SHORT" if want[b]<0 and abs(cur[b])<=amt+1e-15 else "ENTER" if abs(cur[b])<=amt+1e-15 else "CONTINUE"
        elif b=="SAFE": label="EXIT_TO_SAFE" if abs(cur[a])<1e-15 else "CONTINUE"
        else: label="REPLACE"
        moves.append(LedgerMove(a,b,amt,g,label))
        if sum(abs(v) for v in cur.values())>1+1e-12:raise AssertionError("gross")
    return cur,moves
