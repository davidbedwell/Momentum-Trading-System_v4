"""Bonferroni-adjusted heldout paired-cluster inference; never self-certifies."""
import math
from statistics import NormalDist
import numpy as np

def validate(candidates, baseline, returns, clusters, *, attempts, digest, min_clusters=20):
    r=np.asarray(returns,float); b=np.asarray(baseline,bool); ids=np.asarray(clusters)
    if not digest or attempts<len(candidates) or attempts<1: raise ValueError("unfrozen selection")
    if r.ndim!=1 or r.shape!=b.shape or r.shape!=ids.shape: raise ValueError("alignment")
    z=NormalDist().inv_cdf(1-.05/attempts)
    results={}
    for name,mask in candidates.items():
        m=np.asarray(mask,bool)
        if m.shape!=r.shape:raise ValueError("candidate alignment")
        diffs=[]
        for cluster in np.unique(ids[m|b]):
            rows=(ids==cluster)&np.isfinite(r)
            a=r[rows&m];ref=r[rows&b]
            if len(a) and len(ref):diffs.append(float(a.mean()-ref.mean()))
        n=len(diffs)
        if n<min_clusters:results[name]={"clusters":n,"pass":False,"lcb":None};continue
        arr=np.asarray(diffs);lcb=float(arr.mean()-z*arr.std(ddof=1)/math.sqrt(n))
        results[name]={"clusters":n,"mean_delta":float(arr.mean()),"lcb":lcb,"pass":lcb>0}
    return {"attempts":attempts,"selection_digest":digest,"results":results,
            "independently_verified":False,
            "limitation":"Selection provenance, cross-stock calendar dependence and untouched heldout must be independently audited"}
