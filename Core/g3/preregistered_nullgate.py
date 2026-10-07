from __future__ import annotations
from dataclasses import dataclass
import math
import numpy as np
from scipy.stats import wilcoxon

NULL_A="NA_MOVING_BLOCK_BOOTSTRAP_Y"
NULL_B="NB_GUARDED_SHIFT_Y"
NULL_C="NC_GUARDED_SHIFT_X"
FROZEN_NULL_FAMILIES=(NULL_A,NULL_B,NULL_C)
REPLICATES=25
FAMILY_ALPHA=0.05
PER_NULL_ALPHA=FAMILY_ALPHA/3.0

def _guard_bounds(n:int)->tuple[int,int]:
    if n < 8: raise ValueError("series too short for quarter-panel guard")
    return n//4,(3*n)//4

def moving_block_bootstrap_y(y:np.ndarray,seed:int,block_length:int|None=None)->np.ndarray:
    y=np.asarray(y); n=len(y)
    b=int(math.ceil(math.sqrt(n))) if block_length is None else int(block_length)
    if b < 1 or b > n: raise ValueError("invalid block length")
    rng=np.random.default_rng(seed)
    starts=rng.integers(0,n-b+1,size=math.ceil(n/b))
    return np.concatenate([y[s:s+b].copy() for s in starts],axis=0)[:n]

def guarded_shift_rows(a:np.ndarray,seed:int)->np.ndarray:
    a=np.asarray(a); n=len(a); lo,hi=_guard_bounds(n)
    rng=np.random.default_rng(seed)
    shift=int(rng.integers(lo,hi+1))
    return np.roll(a,shift,axis=0)

def apply_frozen_null(x:np.ndarray,y:np.ndarray,family:str,seed:int)->tuple[np.ndarray,np.ndarray]:
    x=np.asarray(x); y=np.asarray(y)
    if len(x)!=len(y): raise ValueError("X/Y length mismatch")
    if family==NULL_A: return x.copy(),moving_block_bootstrap_y(y,seed)
    if family==NULL_B: return x.copy(),guarded_shift_rows(y,seed)
    if family==NULL_C: return guarded_shift_rows(x,seed),y.copy()
    raise ValueError(f"unknown frozen null family {family}")

@dataclass(frozen=True)
class GateTest:
    family:str
    statistic:float
    pvalue:float
    median_paired_difference:float
    significant:bool

@dataclass(frozen=True)
class ReplicatedGateDecision:
    tests:tuple[GateTest,...]
    significant_nulls:int
    state:str

def evaluate_replicated_gate(real:list[float]|np.ndarray,nulls:dict[str,list[float]|np.ndarray])->ReplicatedGateDecision:
    r=np.asarray(real,float)
    if r.shape!=(REPLICATES,) or not np.isfinite(r).all():
        raise ValueError(f"real must contain exactly {REPLICATES} finite paired replicates")
    tests=[]
    for family in FROZEN_NULL_FAMILIES:
        n=np.asarray(nulls[family],float)
        if n.shape!=r.shape or not np.isfinite(n).all(): raise ValueError(f"{family} replicate mismatch")
        d=r-n
        if np.all(d==0):
            stat,p=0.0,1.0
        else:
            stat,p=wilcoxon(d,alternative="greater",zero_method="wilcox",method="auto")
        tests.append(GateTest(family,float(stat),float(p),float(np.median(d)),bool(p<PER_NULL_ALPHA)))
    k=sum(t.significant for t in tests)
    state="STRONG_PASS_3_OF_3" if k==3 else ("PASS_2_OF_3" if k==2 else "FAIL_NO_LARGE_DISCOVERY")
    return ReplicatedGateDecision(tuple(tests),k,state)
