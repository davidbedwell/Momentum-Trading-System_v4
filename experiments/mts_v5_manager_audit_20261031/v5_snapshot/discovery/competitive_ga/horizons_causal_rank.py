"""Horizons original cross-sectional rank/qualification with causal inputs.
Requires an entire current-close 500-stock panel; never ranks one stock alone.
"""
import numpy as np
from .horizons_native_score import score

def evaluate(genome,normalized_by_ticker):
 if len(normalized_by_ticker)<2:raise ValueError('cross-sectional panel required')
 names=sorted(normalized_by_ticker)
 raw=np.asarray([score(genome,normalized_by_ticker[t]) for t in names],float)
 if not np.isfinite(raw).all():raise ValueError('nonfinite score')
 # Original argsort(argsort) convention, including deterministic ticker tie order.
 rank=np.argsort(np.argsort(raw))/(len(names)-1)
 qual=float(genome['qual']);shortqual=float(genome.get('short_qual',1.))
 margin=float(genome.get('safe_margin',0.))/252.
 long=np.maximum(rank-qual,0.)
 short=np.maximum((1.-rank)-shortqual,0.) if genome.get('short',False) else np.zeros_like(long)
 strength=long-short
 strength[np.abs(strength)<=margin]=0.
 return {t:{'raw':float(raw[i]),'rank':float(rank[i]),'strength':float(strength[i]),'qualified':bool(strength[i]>0)} for i,t in enumerate(names)}
