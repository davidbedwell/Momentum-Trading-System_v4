"""Executable G2 module aggregation and policy-field materialization."""
from __future__ import annotations
import numpy as np
from .g2schema import GenomeG2
from .g2expr import EvalContext,eval_expr,materialize_refs
from .g2features import G2Tape

def _stock_shape(v,T,N):
    a=np.asarray(v,float)
    if a.ndim==0:return np.full((T,N),float(a))
    if a.ndim==1:return np.broadcast_to(a[:,None],(T,N))
    return a
def _market_shape(v,T):
    a=np.asarray(v,float)
    if a.ndim==0:return np.full(T,float(a))
    if a.ndim==2:return np.nanmean(a,axis=1)
    return a

def evaluate_g2_fields(g:GenomeG2,tape:G2Tape):
    T=len(tape.dates);N=len(tape.tickers);c=materialize_refs(g,EvalContext(tape))
    mod_signal=[];mod_app=[];mod_u=[];mod_d=[];mod_w=[]
    fallback_u=np.nan_to_num(tape.stock.get("rv20",np.ones((T,N))),nan=1.0,posinf=1.0,neginf=1.0)
    fallback_d=np.abs(np.nan_to_num(tape.stock.get("dist_low20",fallback_u),nan=1.0))
    for m in g.modules:
        app=np.clip(_stock_shape(eval_expr(m.applicability,c),T,N),0,1)
        sig=_stock_shape(eval_expr(m.signal,c),T,N)
        if m.side_mode=="long_only":sig=np.maximum(sig,0)
        elif m.side_mode=="short_only":sig=np.minimum(sig,0)
        u=fallback_u if m.uncertainty is None else np.abs(_stock_shape(eval_expr(m.uncertainty,c),T,N))
        d=fallback_d if m.downside is None else np.abs(_stock_shape(eval_expr(m.downside,c),T,N))
        mod_signal.append(sig);mod_app.append(app);mod_u.append(u);mod_d.append(d);mod_w.append(max(0.,float(m.weight)))
    S=np.stack(mod_signal);A=np.stack(mod_app);U=np.stack(mod_u);D=np.stack(mod_d)
    W=np.asarray(mod_w,float)[:,None,None];conf=A*W
    if g.aggregator.mode=="appl_weighted_sum":
        O=np.nansum(conf*S,axis=0);den=np.nansum(conf,axis=0)
    elif g.aggregator.mode=="appl_weighted_mean":
        den=np.nansum(conf,axis=0);O=np.divide(np.nansum(conf*S,axis=0),den,out=np.zeros((T,N)),where=den>1e-12)
    elif g.aggregator.mode=="softmax":
        # Missing-history cells are neutral, not evidence. Avoid nanmax on an
        # all-missing module slice and give it zero confidence/zero opportunity.
        z=conf/max(float(g.aggregator.temp),1e-6)
        valid=np.isfinite(S)&np.isfinite(z)
        safez=np.where(valid,z,-np.inf);mx=np.max(safez,axis=0,keepdims=True)
        mx=np.where(np.isfinite(mx),mx,0.0);z=np.where(valid,z-mx,-np.inf)
        ew=np.where(valid,np.exp(np.clip(z,-60,60)),0.0);den=np.sum(ew,axis=0)
        O=np.divide(np.sum(ew*np.where(np.isfinite(S),S,0.0),axis=0),den,out=np.zeros((T,N)),where=den>1e-12);conf=ew
    elif g.aggregator.mode=="max_confidence":
        score=np.where(np.isfinite(S),conf,-np.inf);ix=np.argmax(score,axis=0)
        O=np.take_along_axis(S,ix[None,:,:],axis=0)[0];den=np.max(np.where(np.isfinite(score),score,0),axis=0)
    else:raise ValueError(g.aggregator.mode)
    csum=np.sum(conf,axis=0)
    uncertainty=np.divide(np.sum(conf*U,axis=0),csum,out=fallback_u.copy(),where=csum>1e-12)
    downside=np.divide(np.sum(conf*D,axis=0),csum,out=fallback_d.copy(),where=csum>1e-12)
    if g.opportunity_map.mode=="affine":
        alpha=np.ones(T) if g.opportunity_map.alpha is None else np.maximum(0,_market_shape(eval_expr(g.opportunity_map.alpha,c),T))
        beta=np.zeros(T) if g.opportunity_map.beta is None else _market_shape(eval_expr(g.opportunity_map.beta,c),T)
        E=alpha[:,None]*O+beta[:,None]
    elif g.opportunity_map.mode=="causal_calibrated":
        E=O.copy()
    else:raise ValueError(g.opportunity_map.mode)
    kappa=_market_shape(eval_expr(g.lifecycle.kappa,c),T)
    q=_market_shape(eval_expr(g.lifecycle.q,c),T)
    tau=_market_shape(eval_expr(g.allocation.tau,c),T)
    short_gate=np.clip(_stock_shape(eval_expr(g.short_policy.applicability,c),T,N),0,1)
    return {"opportunity_raw":O,"E":E,"uncertainty":uncertainty,"downside":downside,
            "kappa":kappa,"q":q,"tau":tau,"short_gate":short_gate,"context":c}
