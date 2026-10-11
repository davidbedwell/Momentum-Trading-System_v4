"""Multiplicity diagnostics; only pre-specified hypothesis families may be certified."""
import numpy as np
def holm_adjust(pvalues):
 p=np.asarray(pvalues,dtype=float)
 if p.ndim!=1 or not np.isfinite(p).all() or np.any((p<0)|(p>1)):raise ValueError('Invalid p values')
 m=len(p);out=np.empty(m,dtype=float)
 if not m:return out
 order=np.argsort(p,kind='stable')
 adjusted=np.maximum.accumulate((m-np.arange(m))*p[order])
 out[order]=np.minimum(adjusted,1)
 return out
def benjamini_hochberg(pvalues):
 p=np.asarray(pvalues,dtype=float)
 if p.ndim!=1 or not np.isfinite(p).all() or np.any((p<0)|(p>1)):raise ValueError('Invalid p values')
 m=len(p);out=np.empty(m,dtype=float)
 if not m:return out
 order=np.argsort(p,kind='stable')
 adj=np.minimum.accumulate((p[order]*m/(np.arange(m)+1))[::-1])[::-1]
 out[order]=np.minimum(adj,1)
 return out
