from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib, json, math, pickle, random
from pathlib import Path
from typing import Iterable
import numpy as np

FORBIDDEN_PORTFOLIO_KEYS={"portfolio_CAGR","portfolio_MDD","portfolio_slot_count","sector_target_weights","portfolio_SAFE_fraction","specialist_to_specialist_allocation"}
FORBIDDEN_G2_TOKENS=("g2","conforming_ga","derived_store","opportunity_label","portfolio_outcome")

@dataclass(frozen=True)
class Rule:
    feature:int; threshold:float; direction:int
    def fires(self,x:np.ndarray)->np.ndarray:
        z=x[:,self.feature]
        return z>=self.threshold if self.direction>0 else z<=self.threshold

@dataclass(frozen=True)
class Specialist:
    gate:Rule; signal:Rule; side:int; take_profit:float; stop_loss:float; max_horizon:int; add_at:float; reduce_at:float
    def validate(self,n_features:int)->None:
        assert 0<=self.gate.feature<n_features and 0<=self.signal.feature<n_features
        assert self.side in (-1,1) and self.take_profit>0 and self.stop_loss>0 and self.max_horizon>=1
        assert self.add_at>0 and self.reduce_at>0

@dataclass
class Outcome:
    net_return:float; mfe:float; mae:float; tail_loss:float; duration:int; time_to_profit:int|None; time_to_failure:int|None; turnover:float; costs:float; path_signature:tuple[float,...]; actions:tuple[str,...]

def random_specialist(rng:random.Random,n_features:int)->Specialist:
    r=lambda: Rule(rng.randrange(n_features),rng.uniform(-1.5,1.5),rng.choice((-1,1)))
    return Specialist(r(),r(),rng.choice((-1,1)),rng.uniform(.01,.12),rng.uniform(.005,.08),rng.randint(2,30),rng.uniform(.005,.05),rng.uniform(.005,.05))

def evaluate_one(g:Specialist,features:np.ndarray,future_returns:np.ndarray,cost_bps:float=10.0)->list[Outcome]:
    g.validate(features.shape[1]); fire=g.gate.fires(features)&g.signal.fires(features)
    out=[]; cost=cost_bps/10000
    for t in np.flatnonzero(fire):
        if t>=len(future_returns): continue
        path=np.asarray(future_returns[t,:g.max_horizon],float)*g.side
        if not len(path): continue
        wealth=1.; peak=-1e9; trough=1e9; actions=["enter"]; exposure=1.; turnover=1.; tp=tf=None
        sampled=[]
        for j,r in enumerate(path,1):
            wealth*=1+exposure*r; pnl=wealth-1
            peak=max(peak,pnl); trough=min(trough,pnl); sampled.append(pnl)
            if tp is None and pnl>=g.take_profit: tp=j
            if tf is None and pnl<=-g.stop_loss: tf=j
            if pnl<=-g.add_at and exposure<1.5:
                exposure=1.5; turnover+=.5; actions.append("add")
            if pnl>=g.reduce_at and exposure>0.5:
                previous_exposure=exposure
                exposure=.5
                turnover+=abs(previous_exposure-exposure)
                actions.append("reduce")
            if pnl>=g.take_profit or pnl<=-g.stop_loss:
                actions.append("exit"); break
            actions.append("hold")
        turnover+=exposure; actions.append("exit")
        costs=turnover*cost
        net=(wealth-1)-costs
        sig=tuple(float(x) for x in np.interp(np.linspace(0,max(0,len(sampled)-1),5),np.arange(len(sampled)),sampled)) if sampled else ()
        out.append(Outcome(net,peak,trough,min(0.,trough),len(sampled),tp,tf,turnover,costs,sig,tuple(actions)))
    return out

def quality(outputs:list[Outcome])->dict:
    if not outputs:return {"n":0,"mean":float("-inf"),"tail":float("-inf"),"duration":float("inf")}
    r=np.array([x.net_return for x in outputs])
    return {"n":len(r),"mean":float(r.mean()),"tail":float(np.quantile(r,.1)),"duration":float(np.mean([x.duration for x in outputs]))}

def aggregate_quality_summaries(summaries:list[dict])->dict:
    valid=[x for x in summaries if x["n"]>0]
    n=sum(x["n"] for x in valid)
    if not n:
        return {"n":0,"mean":-1e9,"tail":-1e9,"duration":1e9}
    mean=sum(x["mean"]*x["n"] for x in valid)/n
    tail=min(x["tail"] for x in valid)
    duration=sum(x["duration"]*x["n"] for x in valid)/n
    vals=(mean,tail,duration)
    if not all(np.isfinite(vals)):
        raise RuntimeError(f"non-finite aggregate quality: {vals}")
    return {"n":n,"mean":float(mean),"tail":float(tail),"duration":float(duration)}

def temporal_block_permute(y:np.ndarray,seed:int,block:int=20)->np.ndarray:
    rng=np.random.default_rng(seed); n=len(y); blocks=[y[i:i+block].copy() for i in range(0,n,block)]
    rng.shuffle(blocks); return np.concatenate(blocks,axis=0)[:n]

def guarded_circular_shift(y:np.ndarray,seed:int,min_shift:int=60)->np.ndarray:
    """N3 null: break feature/outcome timing with a large deterministic circular shift."""
    y=np.asarray(y); n=len(y)
    if n < 2*min_shift+1: raise ValueError("series too short for requested circular-shift guard")
    rng=np.random.default_rng(seed)
    shift=int(rng.integers(min_shift,n-min_shift+1))
    return np.roll(y,shift,axis=0)

def datewise_cross_sectional_permute(y_by_ticker:np.ndarray,seed:int,buckets:np.ndarray|None=None)->np.ndarray:
    """N2 null: permute outcomes across stocks per date, optionally within fixed buckets."""
    y=np.asarray(y_by_ticker)
    if y.ndim < 2: raise ValueError("expected [date, ticker, ...] outcome array")
    n_tickers=y.shape[1]
    b=np.zeros(n_tickers,dtype=int) if buckets is None else np.asarray(buckets)
    if b.shape != (n_tickers,): raise ValueError("buckets must have one value per ticker")
    rng=np.random.default_rng(seed); out=y.copy()
    groups=[np.flatnonzero(b==v) for v in np.unique(b)]
    for d in range(y.shape[0]):
        for idx in groups:
            perm=idx.copy(); rng.shuffle(perm); out[d,idx,...]=y[d,perm,...]
    return out

def planted_dataset(seed=1,n=2500,p=6,h=10,effect=.006):
    rng=np.random.default_rng(seed); x=rng.normal(size=(n,p)); y=rng.normal(0,.006,size=(n,h))
    mask=(x[:,0]>.7)&(x[:,1]<-.3); y[mask,:3]+=effect
    return x,y,mask

def assert_independent_path(path:str|Path)->None:
    s=str(Path(path)).lower()
    if any(tok in s for tok in FORBIDDEN_G2_TOKENS): raise ValueError(f"G3 lineage firewall: {path}")

def assert_discovery_payload(payload:dict)->None:
    bad=FORBIDDEN_PORTFOLIO_KEYS.intersection(payload)
    if bad: raise ValueError(f"portfolio metrics forbidden in G3 discovery: {sorted(bad)}")

def checkpoint(path:Path,state:dict)->str:
    b=pickle.dumps(state,protocol=5); path.write_bytes(b); return hashlib.sha256(b).hexdigest()
def restore(path:Path)->dict:return pickle.loads(path.read_bytes())
