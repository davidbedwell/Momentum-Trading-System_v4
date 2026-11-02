"""Descriptive paired circular moving-block bootstrap; no new selection."""
from pathlib import Path
import pandas as pd,numpy as np
R=Path(__file__).resolve().parent
s=pd.read_csv(R/'signals.csv',index_col=0,parse_dates=True)
o=pd.read_csv(R/'outcomes.csv',header=[0,1],index_col=0,parse_dates=True)
idx=s.index; ep=pd.Series(idx,index=idx);rng=np.random.default_rng(20261031);rows=[]
for h in [5,10,21,63]:
 valid=(idx.year>=2012)&(idx.year<=2025)&(ep.shift(-h).dt.year.to_numpy()==idx.year)
 sel=(idx.year>=2012)&(idx.year<=2025)
 a=(valid&s['weak&stabilization'].eq(1).to_numpy())[sel]
 for comp in ['unconditional','weak','momentum']:
  b=(valid if comp=='unconditional' else valid&s[comp].eq(1).to_numpy())[sel]
  for metric in ['return','drawdown']:
   y=o[(str(h),metric)].to_numpy()[sel];n=len(y)
   for block in [63,126]:
    effects=[]
    for _ in range(1000):
     starts=rng.integers(0,n,size=int(np.ceil(n/block)));ids=((starts[:,None]+np.arange(block))%n).ravel()[:n]
     aa=a[ids];bb=b[ids];yy=y[ids]
     if aa.sum()>=5 and bb.sum()>=5:effects.append(yy[aa].mean()-yy[bb].mean())
    lo,hi=np.quantile(effects,[.025,.975])
    rows.append(dict(rule='weak&stabilization',comparator=comp,horizon=h,metric=metric,block=block,replicates=len(effects),ci_low=lo,ci_high=hi))
pd.DataFrame(rows).to_csv(R/'bootstrap.csv',index=False)
