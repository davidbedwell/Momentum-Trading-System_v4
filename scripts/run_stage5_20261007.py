#!/usr/bin/env python3
from layered_stage_common_20261007 import *
bank=load_bank()[:12]
def task(t):
 d=frame(t);px=d.adj_close.to_numpy();ma=d.adj_close.rolling(20).mean().to_numpy();rv=d.ret1.rolling(20).std().to_numpy();out=[]
 for ci,c in enumerate(bank):
  m=mask(d,c);sg=1 if c['direction']=='LONG' else -1;normal=[];fail=[]
  for i in np.where(m.fillna(False))[0]:
   if i+1>=len(d) or not np.isfinite(ma[i+1]):continue
   adverse=sg*(px[i+1]/px[i]-1);broken=(sg*(px[i+1]-ma[i+1])<0) or (np.isfinite(rv[i]) and adverse<-2*rv[i]);(fail if broken else normal).append(adverse)
  out.append((ci,normal,fail))
 return out
agg=[[[],[]] for _ in bank]
for batch in pmap(task,[p.stem for p in sorted(ROOT.glob('*.parquet'))]):
 for ci,a,b in batch:agg[ci][0]+=a;agg[ci][1]+=b
rows=[]
for i,c in enumerate(bank):
 normal,fail=agg[i];rows.append({'candidate':c,'normal_n':len(normal),'failure_n':len(fail),'normal_next_ev':float(np.mean(normal)) if normal else None,'failure_next_ev':float(np.mean(fail)) if fail else None})
write(5,'thesis-failure',{'workers':WORKERS,'failure_study':rows,'note':'These are learned-study candidate descriptors, not catastrophe stops.'})
