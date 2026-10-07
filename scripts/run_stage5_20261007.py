#!/usr/bin/env python3
from layered_stage_common_20261007 import *
rows=[]
for c in load_bank()[:12]:
 normal=[];fail=[]
 for p in ROOT.glob('*.parquet'):
  d=frame(p.stem);m=mask(d,c);sg=1 if c['direction']=='LONG' else -1
  # causal deterioration controls measured after signal: opposite MA20 side and 2-sigma adverse move
  idx=np.where(m.fillna(False))[0];px=d.adj_close.to_numpy();ma=d.adj_close.rolling(20).mean().to_numpy();rv=d.ret1.rolling(20).std().to_numpy()
  for i in idx:
   if i+1>=len(d) or not np.isfinite(ma[i+1]):continue
   adverse=sg*(px[i+1]/px[i]-1); broken=(sg*(px[i+1]-ma[i+1])<0) or (np.isfinite(rv[i]) and adverse<-2*rv[i])
   (fail if broken else normal).append(adverse)
 rows.append({'candidate':c,'normal_n':len(normal),'failure_n':len(fail),'normal_next_ev':float(np.mean(normal)) if normal else None,'failure_next_ev':float(np.mean(fail)) if fail else None})
write(5,'thesis-failure',{'failure_study':rows,'note':'These are learned-study candidate descriptors, not catastrophe stops.'})
