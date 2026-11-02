"""Prior-return-only pairwise correlation exposure veto for research execution.
No same-session or forward returns permitted; caller supplies ordered historical matrix.
"""
import numpy as np

def validate(targets,prior_returns,tickers,lookback=60,min_history=40,threshold=.85,max_cluster=.20):
 if not 0<threshold<1 or not 0<max_cluster<=1:raise ValueError('invalid correlation policy')
 active=[t for t,w in targets.items() if w>1e-12]
 if len(active)<2:return True
 if prior_returns is None:raise ValueError('prior returns required for correlation')
 r=np.asarray(prior_returns,dtype=float)
 if r.ndim!=2 or r.shape[1]!=len(tickers) or r.shape[0]<min_history:raise ValueError('insufficient causal return history')
 if not np.isfinite(r[-lookback:]).all():raise ValueError('missing causal return history')
 index={t:i for i,t in enumerate(tickers)}
 if any(t not in index for t in active):raise ValueError('missing ticker in correlation panel')
 x=r[-lookback:][:,[index[t] for t in active]]
 if np.any(np.std(x,axis=0)<=1e-12):raise ValueError('constant return series cannot establish correlation')
 corr=np.corrcoef(x,rowvar=False)
 # Connected components enforce concentration across chains of correlated names.
 seen=set()
 for i in range(len(active)):
  if i in seen:continue
  group={i};front=[i]
  while front:
   k=front.pop()
   for j in range(len(active)):
    if j not in group and corr[k,j]>=threshold:
     group.add(j);front.append(j)
  seen|=group
  if sum(targets[active[j]] for j in group)>max_cluster+1e-12:raise ValueError('correlated cluster exposure cap')
 return True
