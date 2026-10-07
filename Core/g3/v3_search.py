from __future__ import annotations
import numpy as np,time
from Core.g3.starter import Rule
from Core.g3.v3_protocol import V3Specialist
TH=(-1.,0.,1.)
def exact_structural_screen_local(X,Y,pop=48):
 target=np.prod(1+Y[:,:10],axis=1)-1
 atoms=[]; masks=[]
 for f in range(X.shape[1]):
  for d in (-1,1):
   for th in TH:
    atoms.append((f,d,th)); masks.append((X[:,f]>=th) if d>0 else (X[:,f]<=th))
 B=np.asarray(masks,dtype=np.float64); scored=[]
 # Exact triple enumeration, vectorizing the signal dimension.
 for ia,ma in enumerate(masks):
  for ig,mg in enumerate(masks):
   m=ma&mg
   if m.sum()<25: continue
   w=m*target
   cnt=B @ m.astype(np.float64)
   sm=B @ w
   valid=np.flatnonzero(cnt>=25)
   for isg in valid:
    mu=float(sm[isg]/cnt[isg])
    for side in (-1,1): scored.append((side*mu,ia,ig,int(isg),side))
 scored.sort(reverse=True)
 out=[]
 for _,ia,ig,isg,side in scored[:pop]:
  fa,da,tha=atoms[ia];fg,dg,thg=atoms[ig];fs,ds,ths=atoms[isg]
  out.append(V3Specialist(Rule(fa,tha,da),Rule(fg,thg,dg),Rule(fs,ths,ds),side,.08,.06,10,.04,.04))
 return out
if __name__=="__main__":
 rng=np.random.default_rng(7);X=rng.normal(size=(2500,17));Y=rng.normal(0,.01,size=(2500,10));t=time.perf_counter();P=exact_structural_screen_local(X,Y);print("SECONDS",time.perf_counter()-t,"N",len(P))
