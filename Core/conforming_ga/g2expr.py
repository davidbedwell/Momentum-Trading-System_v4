"""Vectorized typed expression evaluator for MTS-GA-G2."""
from __future__ import annotations
from dataclasses import dataclass,field
import numpy as np,pandas as pd
from .g2schema import Expr,CtxUnit,StateUnit,GenomeG2
from .g2features import G2Tape

def _shift(a,k):
    a=np.asarray(a,float);out=np.full_like(a,np.nan,dtype=float)
    if k<len(a):out[k:]=a[:-k]
    return out
def _df(a):return pd.DataFrame(a) if np.asarray(a).ndim==2 else pd.Series(a)
def _roll(a,k,how):
    x=_df(a);r=getattr(x.rolling(k,min_periods=k),how)();return r.to_numpy(float)
def _ema(a,k):
    return _df(a).ewm(span=k,adjust=False,min_periods=k).mean().to_numpy(float)
def _ts_z(a,k=252):
    x=_df(a);m=x.rolling(k,min_periods=max(20,k//2)).mean();s=x.rolling(k,min_periods=max(20,k//2)).std(ddof=0)
    return ((x-m)/s.replace(0,np.nan)).to_numpy(float)
def _ts_pct(a,k=252):
    x=np.asarray(a,float);two=x[:,None] if x.ndim==1 else x;T,N=two.shape;out=np.full_like(two,np.nan)
    minp=max(20,k//2)
    for j in range(N):
        col=two[:,j]
        for t in range(T):
            lo=max(0,t-k+1);z=col[lo:t+1];z=z[np.isfinite(z)]
            if len(z)>=minp and np.isfinite(col[t]):out[t,j]=(np.sum(z<col[t])+0.5*np.sum(z==col[t]))/len(z)
    return out[:,0] if x.ndim==1 else out
def _xs_pct(a):
    x=np.asarray(a,float)
    if x.ndim==1:return np.full_like(x,0.5)
    out=np.full_like(x,np.nan)
    for t,row in enumerate(x):
        ok=np.flatnonzero(np.isfinite(row))
        if not len(ok):continue
        vals=row[ok];order=np.argsort(vals,kind="stable");ranks=np.empty(len(ok),float)
        ranks[order]=(np.arange(len(ok))+0.5)/len(ok);out[t,ok]=ranks
    return out
def _promote(a,ndim,T,N):
    a=np.asarray(a,float)
    if a.ndim==0:return np.full((T,N) if ndim==2 else T,float(a))
    if ndim==2 and a.ndim==1:return np.broadcast_to(a[:,None],(T,N))
    return a

@dataclass
class EvalContext:
    tape:G2Tape
    leaf_cache:dict=field(default_factory=dict)
    ctx_refs:dict[int,np.ndarray]=field(default_factory=dict)
    state_refs:dict[int,np.ndarray]=field(default_factory=dict)
    def leaf(self,scope,name,transform):
        key=(scope,name,transform)
        if key in self.leaf_cache:return self.leaf_cache[key]
        bank={"market":self.tape.market,"sector":self.tape.sector,"stock":self.tape.stock}[scope]
        if name not in bank:raise KeyError(key)
        raw=np.asarray(bank[name],float)
        if transform=="raw":v=raw
        elif transform=="ts_pct":v=_ts_pct(raw,252)
        elif transform=="xs_pct":v=_xs_pct(raw)
        elif transform=="zscore_ts":v=_ts_z(raw,252)
        elif transform=="vol_scaled":
            sd=_df(raw).rolling(60,min_periods=20).std(ddof=0).to_numpy(float);v=raw/np.where(sd==0,np.nan,sd)
        else:raise ValueError(transform)
        self.leaf_cache[key]=v;return v

def eval_expr(e:Expr,c:EvalContext):
    T=len(c.tape.dates);N=len(c.tape.tickers)
    if e.op=="const":return np.asarray(float(e.value))
    if e.op=="feature":return c.leaf(e.scope,e.feature,e.transform)
    if e.op=="ctxref":
        if e.ref_id not in c.ctx_refs:raise KeyError(("ctxref",e.ref_id))
        return c.ctx_refs[e.ref_id]
    if e.op=="stateref":
        if e.ref_id not in c.state_refs:raise KeyError(("stateref",e.ref_id))
        return c.state_refs[e.ref_id]
    args=[eval_expr(a,c) for a in e.args]
    ndim=max([np.asarray(a).ndim for a in args] or [1 if e.scope=="market" else 2])
    if e.scope=="market":ndim=1
    elif e.scope in ("sector","stock"):ndim=2
    args=[_promote(a,ndim,T,N) for a in args]
    if e.op=="delta":return args[0]-_shift(args[0],e.lookback)
    if e.op=="accel":
        k=e.lookback;return (args[0]-2*_shift(args[0],k)+_shift(args[0],2*k))/max(k,1)
    if e.op=="persist":return _roll((args[0]>.5).astype(float),e.lookback,"mean")
    if e.op=="rollmax":return _roll(args[0],e.lookback,"max")
    if e.op=="rollmin":return _roll(args[0],e.lookback,"min")
    if e.op=="ema":return _ema(args[0],e.lookback)
    if e.op=="lag":return _shift(args[0],e.lookback)
    if e.op=="neg":return -args[0]
    if e.op=="abs":return np.abs(args[0])
    if e.op=="add":return args[0]+args[1]
    if e.op=="sub":return args[0]-args[1]
    if e.op=="mul":return args[0]*args[1]
    if e.op=="safediv":return np.divide(args[0],args[1],out=np.zeros_like(args[0],dtype=float),where=np.abs(args[1])>1e-12)
    if e.op=="min":return np.minimum(args[0],args[1])
    if e.op=="max":return np.maximum(args[0],args[1])
    if e.op=="clip":return np.clip(args[0],e.theta-e.scale,e.theta+e.scale)
    if e.op=="softthresh":
        z=np.clip((args[0]-e.theta)/max(abs(e.scale),1e-12),-60,60);return 1/(1+np.exp(-z))
    if e.op=="and":return np.clip(args[0],0,1)*np.clip(args[1],0,1)
    if e.op=="or":
        a=np.clip(args[0],0,1);b=np.clip(args[1],0,1);return a+b-a*b
    if e.op=="not":return 1-np.clip(args[0],0,1)
    if e.op=="ifsoft":
        g=np.clip(args[0],0,1);return g*args[1]+(1-g)*args[2]
    raise ValueError(f"unknown op {e.op}")

def _squash(v,unit:CtxUnit,c:EvalContext):
    if unit.squash=="sigmoid":
        z=np.clip(unit.a*(v-unit.b),-60,60);return 1/(1+np.exp(-z))
    if unit.squash=="tanh01":return (np.tanh(unit.a*(v-unit.b))+1)/2
    if unit.squash=="causal_ts_pct":return _ts_pct(v,252)
    raise ValueError(unit.squash)

def materialize_refs(g:GenomeG2,c:EvalContext):
    for u in g.market_contexts:
        c.ctx_refs[u.innov_id]=_squash(eval_expr(u.expr,c),u,c)
    for u in g.sector_contexts:
        c.ctx_refs[u.innov_id]=_squash(eval_expr(u.expr,c),u,c)
    for s in g.stock_states:
        c.state_refs[s.innov_id]=eval_expr(s.expr,c)
    return c
