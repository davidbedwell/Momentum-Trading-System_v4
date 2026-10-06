"""H.7 null/planted calibration for the production MTS-GA-G2 machinery."""
from __future__ import annotations
from dataclasses import replace
import hashlib
import numpy as np,pandas as pd
from .g2features import G2Tape
from .g2evolution import STOCK_FEATURES,MARKET_FEATURES,SECTOR_FEATURES
from .g2fitness import make_g2_evaluator
from .ga_g2 import evolve_g2
from .g2schema import _walk

def _seed(tag):
    return int.from_bytes(hashlib.sha256(tag.encode()).digest()[:8],"big")

def null_tape(*args,**kwargs):
    raise RuntimeError("NONCONFORMING_LEGACY_NULL_DISABLED: use build_null_tape from partition-local raw data")

def planted_tape(seed:int,T:int=1202,N:int=80)->G2Tape:
    """Synthetic conditional signal embedded in ordinary discoverable G2 feature names."""
    rng=np.random.Generator(np.random.PCG64(seed));dates=pd.bdate_range("2007-01-02",periods=T)
    context=np.zeros(T)
    for i in range(1,T):context[i]=np.clip(.92*context[i-1]+rng.normal(0,.15),-1,1)
    signal=rng.normal(size=(T,N));noise=rng.normal(0,.012,size=(T,N))
    future=noise+(context[:,None]>.25)*.012*np.tanh(signal)
    stock={k:rng.normal(size=(T,N)) for k in STOCK_FEATURES};stock["ret20"]=signal
    stock["rv20"]=np.full((T,N),.012);stock["dist_low20"]=np.full((T,N),.03);stock["dollar_volume20"]=np.full((T,N),100_000_000.)
    market={k:rng.normal(size=T) for k in MARKET_FEATURES};market["breadth_positive20"]=context;market["spy_dd"]=np.zeros(T);market["spy_ret1"]=np.zeros(T)
    sector={k:rng.normal(size=(T,N)) for k in SECTOR_FEATURES}
    op=np.full((T,N),100.0)
    for i in range(1,T):op[i]=op[i-1]*(1.0+future[i-1])
    ex={"open":op,"high":op*1.002,"low":op*.998,"close":op,"volume":np.full((T,N),1_000_000.),
        "dividends":np.zeros((T,N)),"safe_daily":np.zeros(T),"adv_dollars":np.full((T,N),100_000_000.)}
    return G2Tape(dates,tuple(f"P{i:03d}" for i in range(N)),stock,sector,market,ex)

def _has_feature(e,scope,name):
    return any(x.op=="feature" and x.scope==scope and x.feature==name for x in _walk(e))

def _app_references_planted_context(g,m)->bool:
    """The SAME module carrying ret20 must condition applicability on breadth_positive20.
    Accept direct use or a ctxref whose referenced context expression uses the planted feature.
    """
    ctx={u.innov_id:u for u in (*g.market_contexts,*g.sector_contexts)}
    for x in _walk(m.applicability):
        if x.op=="feature" and x.scope=="market" and x.feature=="breadth_positive20":return True
        if x.op=="ctxref" and x.ref_id in ctx and _has_feature(ctx[x.ref_id].expr,"market","breadth_positive20"):return True
    return False

def planted_recovered(g)->bool:
    return any(_has_feature(m.signal,"stock","ret20") and _app_references_planted_context(g,m) for m in g.modules)

def run_null_g2(repo,long_df,tickers,*,master_seed,fold,generations=500,population_size=250,workers=6,checkpoint_dir=None):
    nt=build_null_tape(repo,long_df,tickers,_seed(f"null|{master_seed}|{fold}"))
    return evolve_g2(evaluator=make_g2_evaluator(nt),master_seed=f"{master_seed}|NULL",fold=fold,
      generations=generations,population_size=population_size,workers=workers,checkpoint_dir=checkpoint_dir)

def _archive_recovered(r):
    return any(planted_recovered(g) and float(m["cagr"])>0.0 for a in r["archives"].values() for g,m in a)

def run_planted_g2(*,master_seed,seeds=(0,1,2,3),generations=500,population_size=250,workers=6,checkpoint_root=None,check_interval=1):
    """Claude H.7 planted gate: observe recovery every generation, 500 max.

    Disk checkpoints remain on the production controller cadence (10 generations).
    Recovery observation is in-memory after every completed generation.
    """
    results=[];successes=failures=0
    for seed in seeds:
        t=planted_tape(seed);ck=None if checkpoint_root is None else checkpoint_root/f"seed{seed}"
        hit={"generation":None}
        def stop(gen,archives,history):
            if any(planted_recovered(g) and float(m["cagr"])>0.0 for a in archives.values() for g,m in a):
                hit["generation"]=gen;return True
            return False
        r=evolve_g2(evaluator=make_g2_evaluator(t),master_seed=f"{master_seed}|PLANTED|{seed}",fold=0,
          generations=generations,population_size=population_size,workers=workers,checkpoint_dir=ck,generation_stop=stop)
        recovered=hit["generation"] is not None
        used=int(hit["generation"] if recovered else generations)
        results.append({"seed":seed,"recovered":bool(recovered),"generation":used})
        successes+=int(recovered);failures+=int(not recovered)
        if successes>=3:return {"results":results,"recovered":[x["recovered"] for x in results],"passed":True,"decision":"early_pass"}
        if failures>=2:return {"results":results,"recovered":[x["recovered"] for x in results],"passed":False,"decision":"early_futility"}
    return {"results":results,"recovered":[x["recovered"] for x in results],"passed":successes>=3,"decision":"budget_complete"}

def null_long_df(long_df:pd.DataFrame,tickers:tuple[str,...],seed:int,block:int=20)->pd.DataFrame:
    """Common-block permute stock daily state and reconstruct price paths."""
    cols=("open","high","low","close","adj_close","volume","dividends")
    d=long_df[long_df.ticker.isin(tickers)].copy()
    dates=pd.DatetimeIndex(sorted(pd.to_datetime(d.date).unique()))
    mats={c:d.pivot(index="date",columns="ticker",values=c).reindex(index=dates,columns=tickers).to_numpy(float) for c in cols}
    adj=mats["adj_close"];T,N=adj.shape
    rr=np.full((T,N),np.nan);rr[1:]=adj[1:]/adj[:-1]-1.0
    starts=list(range(1,T,block));rng=np.random.Generator(np.random.PCG64(seed))
    order=rng.permutation(len(starts));idx=np.concatenate([np.arange(starts[i],min(starts[i]+block,T)) for i in order])[:T-1]
    pr=rr[idx];nadj=np.empty_like(adj);nadj[0]=adj[0]
    for j in range(1,T):nadj[j]=nadj[j-1]*(1.0+pr[j-1])
    outm={"adj_close":nadj}
    # Preserve the source day's adjusted intraday geometry, but place it on
    # the reconstructed synthetic adjusted-close path. Then derive raw OHLC
    # using that source day's adjustment factor. This prevents original
    # calendar price levels/split factors from leaking into synthetic features.
    src_adj=adj[idx];src_close=mats["close"][idx]
    src_factor=src_adj/src_close
    for c in ("open","high","low"):
        src_adjusted=mats[c][idx]*src_factor
        ratio=src_adjusted/src_adj
        adjusted=np.empty_like(adj);adjusted[0]=mats[c][0]*(adj[0]/mats["close"][0]);adjusted[1:]=nadj[1:]*ratio
        z=np.empty_like(adj);z[0]=mats[c][0];z[1:]=adjusted[1:]/src_factor
        outm[c]=z
    z=np.empty_like(adj);z[0]=mats["close"][0];z[1:]=nadj[1:]/src_factor;outm["close"]=z
    for c in ("volume","dividends"):
        z=np.empty_like(mats[c]);z[0]=mats[c][0];z[1:]=mats[c][idx];outm[c]=z
    return pd.concat([pd.DataFrame({"date":dates,"ticker":t,**{c:outm[c][:,j] for c in cols}}) for j,t in enumerate(tickers)],ignore_index=True)

def build_null_tape(repo,long_df:pd.DataFrame,tickers:tuple[str,...],seed:int,block:int=20,
                    start="2006-09-15",end="2026-09-14")->G2Tape:
    """Re-enter the production feature pipeline after null path construction."""
    from .g2features import build_g2_tape
    return build_g2_tape(repo,null_long_df(long_df,tickers,seed,block),tickers,start=start,end=end)
