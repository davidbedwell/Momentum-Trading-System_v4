"""Causal dynamic-peer construction and diagnostics."""
from __future__ import annotations
import numpy as np

def peer_indices(returns:np.ndarray,t:int,window:int=60,k:int=3):
    r=np.asarray(returns,float)
    if t<window:return [np.array([],dtype=int) for _ in range(r.shape[1])]
    hist=np.nan_to_num(r[t-window:t+1],nan=0.0)
    with np.errstate(invalid="ignore",divide="ignore"):
        corr=np.corrcoef(hist,rowvar=False)
    N=r.shape[1];out=[]
    for i in range(N):
        c=corr[i].copy();c[i]=np.nan
        valid=np.flatnonzero(np.isfinite(c))
        if not len(valid):
            out.append(np.array([],dtype=int));continue
        order=valid[np.argsort(c[valid],kind="stable")]
        out.append(order[-min(k,len(order)):])
    return out

def peer_validity_diagnostic(returns:np.ndarray,window:int=60,k:int=3,last_n:int=200,seed:int=1):
    r=np.asarray(returns,float);rng=np.random.default_rng(seed);N=r.shape[1]
    selected=[];randomized=[];churn=[]
    start=max(window,min(r.shape[0]-1,r.shape[0]-last_n))
    prev=None
    for t in range(start,r.shape[0]):
        p=peer_indices(r,t,window,k)
        p2=peer_indices(r,t,max(20,window+10),k)
        hist=np.nan_to_num(r[t-window:t+1],nan=0.0);corr=np.corrcoef(hist,rowvar=False)
        for i,ps in enumerate(p):
            if len(ps):
                selected.extend([corr[i,j] for j in ps if np.isfinite(corr[i,j])])
                pool=np.array([j for j in range(N) if j!=i])
                rr=rng.choice(pool,size=len(ps),replace=False)
                randomized.extend([corr[i,j] for j in rr if np.isfinite(corr[i,j])])
                if len(p2[i]):
                    churn.append(1-len(set(ps)&set(p2[i]))/max(len(set(ps)|set(p2[i])),1))
    return {"selected_mean_corr":float(np.mean(selected)),"random_mean_corr":float(np.mean(randomized)),
            "selected_minus_random":float(np.mean(selected)-np.mean(randomized)),
            "window_perturbation_mean_jaccard_churn":float(np.mean(churn)) if churn else np.nan,
            "observations":len(selected)}

def peer_indices_tape(returns:np.ndarray,window:int=60,k:int=3):
    """Same trailing Pearson peers as peer_indices(), computed for the whole tape.
    Maintains rolling first/cross moments so each session is O(N^2), not O(window*N^2).
    """
    r=np.nan_to_num(np.asarray(returns,float),nan=0.0)
    T,N=r.shape
    out=[[np.array([],dtype=int) for _ in range(N)] for _ in range(T)]
    n=window+1
    if T<n:return out
    block=r[:n]
    sx=block.sum(axis=0); cross=block.T@block
    for t in range(window,T):
        if t>window:
            old=r[t-n];new=r[t]
            sx += new-old
            cross += np.outer(new,new)-np.outer(old,old)
        cov=cross-sx[:,None]*sx[None,:]/n
        var=np.diag(cov).copy()
        denom=np.sqrt(np.maximum(var,0))[:,None]*np.sqrt(np.maximum(var,0))[None,:]
        with np.errstate(invalid="ignore",divide="ignore"):
            corr=cov/denom
        for i in range(N):
            c=corr[i].copy();c[i]=np.nan
            valid=np.flatnonzero(np.isfinite(c))
            if len(valid):
                order=valid[np.argsort(c[valid],kind="stable")]
                out[t][i]=order[-min(k,len(order)):]
    return out
