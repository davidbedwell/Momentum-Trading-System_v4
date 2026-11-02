"""Evaluate all niche centers independently; never force a nearest-only label."""
import numpy as np

def memberships(features, centers, ids, radii):
    x=np.asarray(features,dtype=float)
    c=np.asarray(centers,dtype=float)
    r=np.asarray(radii,dtype=float)
    if x.ndim!=2 or c.ndim!=2 or x.shape[1]!=c.shape[1]:
        raise ValueError("Dimension mismatch")
    if len(ids)!=len(c) or r.shape!=(len(c),) or np.any(r<=0):
        raise ValueError("Invalid radii")
    distances=np.linalg.norm(x[:,None,:]-c[None,:,:],axis=2)
    return [tuple(ids[j] for j in np.flatnonzero(row)) for row in distances<=r], distances
