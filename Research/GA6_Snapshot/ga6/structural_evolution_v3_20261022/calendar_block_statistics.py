"""Synchronized circular calendar-block bootstrap for exploratory SPA and stepdown tests.
Rows are calendar sessions; columns are candidate net-return differences against one
preregistered benchmark. All tickers/positions must be aggregated by calendar session
upstream. This module never grants scientific certification on its own.
"""
import numpy as np

def validate(differentials,block_length,replications):
 x=np.asarray(differentials,dtype=float)
 if x.ndim!=2 or min(x.shape)<2 or not np.isfinite(x).all():
  raise ValueError("Expected finite calendar-session x candidate differential matrix")
 if not isinstance(block_length,int) or not 2<=block_length<=x.shape[0]:
  raise ValueError("Invalid calendar block length")
 if not isinstance(replications,int) or replications<199:
  raise ValueError("At least 199 bootstrap replications required")
 return x

def bootstrap_indices(n,block_length,replications,seed):
 rng=np.random.default_rng(seed)
 count=(n+block_length-1)//block_length
 starts=rng.integers(0,n,size=(replications,count))
 offsets=np.arange(block_length)
 return ((starts[:,:,None]+offsets)%n).reshape(replications,-1)[:,:n]

def synchronized_bootstrap(differentials,block_length,replications=999,seed=0):
 x=validate(differentials,block_length,replications)
 indices=bootstrap_indices(x.shape[0],block_length,replications,seed)
 centered=x-x.mean(axis=0)
 # One identical calendar-index draw across all strategies, retaining common shocks.
 return x.mean(axis=0),centered[indices].mean(axis=1)

def spa_global(differentials,block_length,replications=999,seed=0):
 """Conservative max-t SPA-style global screen (no Hansen recentering).
 Does not claim to implement Hansen SPA until studentization/recentering audited.
 """
 observed,boot=synchronized_bootstrap(differentials,block_length,replications,seed)
 scale=np.std(np.asarray(differentials,dtype=float),axis=0,ddof=1)
 if np.any(scale<=0):raise ValueError("Zero variance: cannot studentize")
 stat=observed/scale
 null=boot/scale
 maximum=float(np.max(stat))
 p=(1+int(np.sum(np.max(null,axis=1)>=maximum)))/(replications+1)
 return {'max_studentized_mean':maximum,'global_p_value':p,'replications':replications,
         'block_length':block_length,'method':'conservative_synchronized_max_t_screen_not_Hansen_SPA',
         'certification':False}

def stepdown_max_t(differentials,block_length,replications=999,seed=0):
 """Westfall-Young/Romano-Wolf style stepdown max-t with synchronized draws.
 Research implementation; subset-pivotality and dependence calibration unverified.
 """
 x=validate(differentials,block_length,replications)
 observed,boot=synchronized_bootstrap(x,block_length,replications,seed)
 scale=x.std(axis=0,ddof=1)
 if np.any(scale<=0):raise ValueError("Zero variance: cannot studentize")
 statistics=observed/scale
 null=boot/scale
 order=np.argsort(-statistics,kind='stable')
 adjusted=np.zeros(len(order))
 previous=0.
 for position,index in enumerate(order):
  remaining=order[position:]
  p=(1+np.sum(np.max(null[:,remaining],axis=1)>=statistics[index]))/(replications+1)
  previous=max(previous,float(p))
  adjusted[index]=previous
 return {'adjusted_p_values':adjusted.tolist(),'order':order.tolist(),
         'method':'synchronized_stepdown_max_t_research_only','certification':False}
