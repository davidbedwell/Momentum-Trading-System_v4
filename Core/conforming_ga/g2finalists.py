"""Shared production I.4 training-only finalist selection."""
from __future__ import annotations
import hashlib, math
import numpy as np
from .g2fast import fast_simulate_g2
from .g2schema import genome_hash,active_concept_count

BOOTSTRAP_REPLICATES=2000

def _seed_text(fold:int, identity:str)->tuple[int,str]:
    s=f"fold={fold}|identity={identity}|purpose=I4_stationary_bootstrap"
    h=hashlib.sha256(s.encode()).hexdigest()
    return int(h[:16],16),s

def politis_white_block_length(r):
    x=np.asarray(r,float);x=x[np.isfinite(x)];n=len(x)
    if n<4:return 1
    x=x-x.mean();g0=float(np.dot(x,x)/n)
    if g0<=1e-30:return 1
    maxlag=min(n-1,int(math.ceil(math.sqrt(n)*3)))
    ac=[float(np.dot(x[:-k],x[k:])/(n-k)/g0) for k in range(1,maxlag+1)]
    kn=max(5,int(math.ceil(math.log10(n))));band=2.0*math.sqrt(math.log10(n)/n);m=maxlag
    for k in range(1,maxlag-kn+2):
        if all(abs(ac[j-1])<band for j in range(k,k+kn)):m=k;break
    m=max(1,min(m,maxlag))
    gam=[g0]+[float(np.dot(x[:-k],x[k:])/n) for k in range(1,m+1)]
    G=gam[0]+2*sum(gam[1:]);D=2*sum(k*gam[k] for k in range(1,m+1))
    if abs(G)<1e-30 or abs(D)<1e-30:return max(1,m)
    return int(np.clip(round((2*D*D/(G*G))**(1/3)*n**(1/3)),1,n))

def _stationary_indices(n,L,reps,seed):
    rng=np.random.Generator(np.random.PCG64(seed));p=1.0/max(L,1)
    out=np.empty((reps,n),np.int32)
    for b in range(reps):
        out[b,0]=rng.integers(0,n)
        for t in range(1,n):
            out[b,t]=rng.integers(0,n) if rng.random()<p else (out[b,t-1]+1)%n
    return out

def _cagrs(r,idx):
    x=np.nan_to_num(np.asarray(r,float),nan=0.0);out=np.empty(len(idx))
    for b,ii in enumerate(idx):
        w=float(np.prod(1.0+x[ii]));out[b]=w**(252.0/max(len(x),1))-1.0 if w>0 else -1.0
    return out

def candidate_bootstrap(r,fold,g,reps=BOOTSTRAP_REPLICATES):
    if reps!=BOOTSTRAP_REPLICATES:raise ValueError("I4_REPLICATE_COUNT_DRIFT")
    x=np.nan_to_num(np.asarray(r,float),nan=0.0);L=politis_white_block_length(x)
    seed,derivation=_seed_text(fold,genome_hash(g));idx=_stationary_indices(len(x),L,reps,seed);dist=_cagrs(x,idx)
    return dist,{"replicate_count":reps,"seed_derivation":derivation,"seed":seed,"selected_block_length":L,
      "bootstrap_distribution_summary":{"mean":float(dist.mean()),"std":float(dist.std(ddof=1)),
      "p05":float(np.quantile(dist,.05)),"median":float(np.median(dist)),"p95":float(np.quantile(dist,.95))},
      "cagr_5th_percentile":float(np.quantile(dist,.05)),"complexity_active_concepts":active_concept_count(g)}

def paired_difference_se(ra,rb,fold,ga,gb,reps=BOOTSTRAP_REPLICATES):
    """Common stationary resamples; pair block length chosen from paired difference series."""
    if reps!=BOOTSTRAP_REPLICATES:raise ValueError("I4_REPLICATE_COUNT_DRIFT")
    a=np.nan_to_num(np.asarray(ra,float),nan=0.0);b=np.nan_to_num(np.asarray(rb,float),nan=0.0)
    if len(a)!=len(b):raise ValueError("PAIRED_HISTORY_LENGTH_MISMATCH")
    L=politis_white_block_length(a-b)
    ids="|".join(sorted((genome_hash(ga),genome_hash(gb))))
    seed,derivation=_seed_text(fold,"pair="+ids);idx=_stationary_indices(len(a),L,reps,seed)
    da=_cagrs(a,idx);db=_cagrs(b,idx);diff=da-db
    return float(diff.std(ddof=1)),{"paired_seed_derivation":derivation,"paired_seed":seed,
      "paired_selected_block_length":L,"paired_difference_summary":{"mean":float(diff.mean()),
      "std":float(diff.std(ddof=1)),"p05":float(np.quantile(diff,.05)),"median":float(np.median(diff)),
      "p95":float(np.quantile(diff,.95))}}

def select_band_finalist(tape,fold,band,archive):
    eligible=[(g,m) for g,m in archive if abs(float(m["mdd"]))<=float(band)+1e-12]
    if not eligible:return None
    rows=[]
    for g,m in eligible:
        _,r,*_=fast_simulate_g2(g,tape);dist,ev=candidate_bootstrap(r,fold,g)
        rows.append({"g":g,"m":m,"r":r,"ev":ev})
    rows.sort(key=lambda z:(-z["ev"]["cagr_5th_percentile"],z["ev"]["complexity_active_concepts"],genome_hash(z["g"])))
    leader=rows[0];ties=[leader];comparisons=[]
    for z in rows[1:]:
        eps,pev=paired_difference_se(leader["r"],z["r"],fold,leader["g"],z["g"])
        delta=leader["ev"]["cagr_5th_percentile"]-z["ev"]["cagr_5th_percentile"]
        tied=delta<=eps+1e-15
        comparisons.append({"challenger":genome_hash(z["g"]),"leader_minus_challenger_p05_cagr":delta,
                            "paired_difference_se_epsilon":eps,"within_epsilon":tied,**pev})
        if tied:ties.append(z)
    ties.sort(key=lambda z:(z["ev"]["complexity_active_concepts"],-z["ev"]["cagr_5th_percentile"],genome_hash(z["g"])))
    pick=ties[0];e=dict(pick["ev"]);e["primary_leader"]=genome_hash(leader["g"]);e["leader_relative_comparisons"]=comparisons
    e["epsilon_rule"]="paired stationary-bootstrap SE of CAGR difference; common resamples; p05-CAGR difference compared to epsilon"
    e["complexity_tiebreak_applied"]=len(ties)>1;e["selected_genome_hash"]=genome_hash(pick["g"])
    return pick["g"],pick["m"],e
