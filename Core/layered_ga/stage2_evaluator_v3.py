from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np
import pandas as pd
from .stage2_path_v3 import ExecutionPaths,ProspectiveCosts,signed_excursions
from .stage2_cluster_stats_v3 import row_weighted_cluster_se


@dataclass(frozen=True)
class CurveEvaluation:
    side:str
    points:tuple[dict,...]
    pareto_horizons:tuple[int,...]
    pareto_ranges:tuple[tuple[int,int],...]


def cluster_ids_from_frame(frame:pd.DataFrame)->np.ndarray:
    dates=pd.to_datetime(frame['effective_date']);keys=frame['security_id'].astype(str)+'|'+dates.dt.year.astype(str)
    return pd.factorize(keys,sort=True)[0].astype(np.int32)


def _tail_mean(v:np.ndarray,fraction:float=.05)->float:
    if len(v)==0:return float('nan')
    k=max(1,int(math.ceil(len(v)*fraction)))
    return float(np.partition(v,k-1)[:k].mean())


def _pareto_indices(points:list[dict])->list[int]:
    # Maximize EV and LCB95; MAE is reported as risk evidence, not optimized.
    ids=[i for i,p in enumerate(points) if all(np.isfinite(p.get(k,np.nan)) for k in ('ev_net','lcb95','mae_mean'))]
    keep=[]
    for i in ids:
        a=points[i];dominated=False
        for j in ids:
            if i==j:continue
            b=points[j]
            weak=(b['ev_net']>=a['ev_net'] and b['lcb95']>=a['lcb95'])
            strict=(b['ev_net']>a['ev_net'] or b['lcb95']>a['lcb95'])
            if weak and strict:
                dominated=True;break
        if not dominated:keep.append(i)
    return keep


def _ranges(horizons:list[int])->tuple[tuple[int,int],...]:
    if not horizons:return ()
    hs=sorted(horizons);out=[];a=b=hs[0]
    for h in hs[1:]:
        if h==b+1:b=h
        else:out.append((a,b));a=b=h
    out.append((a,b));return tuple(out)


def evaluate_curve(mask:np.ndarray,paths:ExecutionPaths,costs:ProspectiveCosts,side:str,cluster_ids:np.ndarray,*,min_raw_n:int=200,min_effective_n:int=20)->CurveEvaluation:
    side=side.upper()
    if side not in ('LONG','SHORT'):raise ValueError('side must be LONG or SHORT')
    mask=np.asarray(mask,dtype=bool)
    if len(mask)!=paths.endpoint_return.shape[0] or len(cluster_ids)!=len(mask):raise ValueError('alignment mismatch')
    sign=1.0 if side=='LONG' else -1.0
    cmatrix=costs.long_roundtrip if side=='LONG' else costs.short_roundtrip
    adverse,favorable=signed_excursions(paths,side)
    H=paths.endpoint_return.shape[1];ncl=int(cluster_ids.max())+1 if len(cluster_ids) else 0
    pts=[]
    for j in range(H):
        gross=sign*paths.endpoint_return[:,j];c=cmatrix[:,j]
        valid=mask & np.isfinite(gross)&np.isfinite(c)
        ix=np.flatnonzero(valid);raw_n=len(ix)
        if raw_n<min_raw_n:
            pts.append({'horizon':j+1,'n':raw_n,'effective_n':0,'ev_net':np.nan,'lcb95':np.nan,'mae_mean':np.nan,'mfe_mean':np.nan});continue
        v=gross[ix]-c[ix];ids=cluster_ids[ix]
        sums=np.bincount(ids,weights=v,minlength=ncl);cnt=np.bincount(ids,minlength=ncl);used=cnt>0
        cm=sums[used]/cnt[used];ne=len(cm)
        if ne<min_effective_n:
            pts.append({'horizon':j+1,'n':raw_n,'effective_n':ne,'ev_net':np.nan,'lcb95':np.nan,'mae_mean':np.nan,'mfe_mean':np.nan});continue
        ev=float(v.mean())
        # Row-weighted point estimate requires row-weighted cluster-robust SE.
        # Treat security-year clusters as independent; coverage under shared
        # calendar shocks must be separately validated before certification.
        se=row_weighted_cluster_se(v,ids)
        lcb=ev-1.96*se
        wins=v[v>0];loss=v[v<0];ma=adverse[ix,j].astype(float);mf=favorable[ix,j].astype(float);ma=ma[np.isfinite(ma)];mf=mf[np.isfinite(mf)]
        pts.append({
            'horizon':j+1,'n':raw_n,'effective_n':ne,'ev_net':ev,'se_cluster':se,'lcb95':float(lcb),
            'win_rate':float((v>0).mean()),'avg_win':float(wins.mean()) if len(wins) else 0.0,'median_win':float(np.median(wins)) if len(wins) else 0.0,
            'avg_loss':float(loss.mean()) if len(loss) else 0.0,'median_loss':float(np.median(loss)) if len(loss) else 0.0,
            'payoff_ratio':float(wins.mean()/abs(loss.mean())) if len(wins) and len(loss) and loss.mean()!=0 else np.nan,
            'cvar5':_tail_mean(v,.05),'mae_mean':float(ma.mean()) if len(ma) else np.nan,'mae_median':float(np.median(ma)) if len(ma) else np.nan,
            'mae_tail5':_tail_mean(ma,.05) if len(ma) else np.nan,'mfe_mean':float(mf.mean()) if len(mf) else np.nan,'mfe_median':float(np.median(mf)) if len(mf) else np.nan,
            'positive_cluster_fraction':float((cm>0).mean()),'capital_time_efficiency':ev/(j+1),
        })
    pi=_pareto_indices(pts);ph=[pts[i]['horizon'] for i in pi]
    return CurveEvaluation(side,tuple(pts),tuple(ph),_ranges(ph))


def pooled_phenotype_front(evaluations:list[tuple[str,CurveEvaluation]])->list[dict]:
    """Global nondominated genome+horizon phenotypes; no scalar EV/MAE exchange rate."""
    flat=[]
    for genome_id,ev in evaluations:
        for p in ev.points:
            if all(np.isfinite(p.get(k,np.nan)) for k in ('ev_net','lcb95','mae_mean')):
                flat.append({'genome_id':genome_id,'side':ev.side,**p})
    keep=[]
    for i,a in enumerate(flat):
        dominated=False
        for j,b in enumerate(flat):
            if i==j:continue
            weak=(b['ev_net']>=a['ev_net'] and b['lcb95']>=a['lcb95'])
            strict=(b['ev_net']>a['ev_net'] or b['lcb95']>a['lcb95'])
            if weak and strict:dominated=True;break
        if not dominated:keep.append(a)
    return keep
