"""Native Horizons signed target weights, including causal downside transform.
Reference parity mode cap=1. Manager execution must apply separate risk gates.
"""
import numpy as np
from .horizons_causal_rank import evaluate

def targets(g,panel,previous=None,cap=.10,prior_returns=None):
 if not 0<cap<=1:raise ValueError('invalid cap')
 previous=previous or {}
 ranked=evaluate(g,panel)
 names=sorted(ranked)
 raw=np.asarray([ranked[t]['raw'] for t in names])
 s=np.asarray([ranked[t]['strength'] for t in names])
 mode=g['alloc']
 if mode=='uncertainty':s=s/(np.std(raw)+1e-6)
 elif mode=='downside':
  if prior_returns is None:raise ValueError('lagged returns required for downside allocation')
  hist=np.asarray(prior_returns,dtype=float)
  if hist.ndim!=2 or hist.shape[1]!=len(names):raise ValueError('lagged return panel shape mismatch')
  s=s/(np.std(np.minimum(np.nan_to_num(hist,nan=0.),0.))+1e-4 if hist.size else 1e-4)
 elif mode!='strength':raise ValueError('unknown allocation')
 gross=np.abs(s).sum()
 target=s/gross if gross>0 else s
 old=np.asarray([float(previous.get(t,0.)) for t in names])
 if np.abs(old).sum()>0 and np.abs(target).sum()>0:
  keep=(np.sign(old)==np.sign(target)) & (np.abs(target)+float(g['replace_margin'])>=np.abs(old))
  target=np.where(keep,np.maximum(np.abs(old),np.abs(target))*np.sign(target),target)
  total=np.abs(target).sum()
  if total>1:target=target/total
 return {t:float(np.sign(v)*min(abs(v),cap)) for t,v in zip(names,target) if abs(v)>1e-15}
