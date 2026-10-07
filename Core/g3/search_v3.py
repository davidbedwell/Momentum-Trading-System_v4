from __future__ import annotations
import numpy as np
from Core.g3.starter import Specialist,Rule

SCREEN_THRESHOLDS=(-1.0,0.0,1.0)

def structural_screen(data:dict[str,tuple[np.ndarray,np.ndarray]],population:int)->list[Specialist]:
    """Deterministically screen the existing two-rule vocabulary before lifecycle evolution.
    This is adaptive search work and must be charged equally to real/null arms.
    """
    first=next(iter(data.values())); nf=first[0].shape[1]
    # Screen on 10-session compounded path return; lifecycle is deliberately neutral here.
    pools=[]
    for X,Y in data.values():
        target=np.prod(1.0+Y[:,:10],axis=1)-1.0
        pools.append((X,target))
    scored=[]
    for f1 in range(nf):
      for d1 in (-1,1):
       for th1 in SCREEN_THRESHOLDS:
        for f2 in range(nf):
         for d2 in (-1,1):
          for th2 in SCREEN_THRESHOLDS:
           vals=[]
           for X,target in pools:
            m=((X[:,f1]>=th1) if d1>0 else (X[:,f1]<=th1)) & ((X[:,f2]>=th2) if d2>0 else (X[:,f2]<=th2))
            if m.any(): vals.append(target[m])
           if not vals: continue
           v=np.concatenate(vals)
           if len(v)<25: continue
           mu=float(v.mean())
           for side in (-1,1):
            scored.append((side*mu,len(v),f1,d1,th1,f2,d2,th2,side))
    scored.sort(reverse=True)
    out=[]
    for _,_,f1,d1,th1,f2,d2,th2,side in scored[:population]:
        out.append(Specialist(Rule(f1,th1,d1),Rule(f2,th2,d2),side,.08,.06,10,.04,.04))
    if len(out)<population: raise RuntimeError("structural screen produced insufficient seeds")
    return out
