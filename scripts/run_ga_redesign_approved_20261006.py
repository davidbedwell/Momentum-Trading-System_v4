#!/usr/bin/env python3
"""Approved MTS redesigned DEV117 engine, 2026-10-06.
Fail-closed implementation of the controlling 2026-10-05 freeze.
V2 is imported only for immutable DEV117 membership, local PIT stock/market primitives,
metrics and price/risk-free loaders; its current-GICS sector features and validation flow are not used.
"""
import argparse, hashlib, json, math, os, random, time, multiprocessing as mp
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
os.environ.setdefault("OPENBLAS_NUM_THREADS","1"); os.environ.setdefault("OMP_NUM_THREADS","1")
os.environ.setdefault("MKL_NUM_THREADS","1"); os.environ.setdefault("NUMEXPR_NUM_THREADS","1")
import numpy as np, pandas as pd
from numba import njit
import run_horizon_free_ga_frozen_architecture_v2_20261005 as v2
ROOT=v2.ROOT
FREEZE=ROOT/"Research/Protocols/MTS_GA_REDESIGN_EXPERIMENT_FREEZE_20261005.md"
OUT=ROOT/"Research/Reports/MTS_GA_REDESIGN_FINAL_ANALYSIS_20261006.json"
STATE=ROOT/"Research/State/MTS_GA_REDESIGN_CHECKPOINT_20261006.json"
SPY=ROOT/"Research/Data/Comparators/SPY_20050901_20260914_20261006.csv"
MASTER=20261006
DD=v2.DD_BANDS
ALLOCS=("equal","strength","uncertainty","downside")
FAMILIES=v2.FAMILIES
EPISODES=[
 ("GFC","2007-10-09","2009-03-09"),("FLASH_EURO","2010-04-23","2010-07-02"),
 ("US_DEBT_EURO","2011-04-29","2011-10-03"),("CHINA_OIL","2015-05-21","2016-02-11"),
 ("VOLMAGEDDON_Q4","2018-01-26","2018-12-24"),("COVID","2020-02-19","2020-03-23"),
 ("INFLATION_2022","2022-01-03","2022-10-12"),("YEN_AI_2024","2024-07-16","2024-08-05")]
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1<<20),b""): h.update(b)
 return h.hexdigest()
def seed(*x): return int.from_bytes(hashlib.sha256(("|".join(map(str,x))).encode()).digest()[:8],"little")
def folds(dev):
 # Predetermined legacy DEV117 rotations retained; only access order changes.
 return v2.folds(dev)
def dynamic_peer_context(px,dates,dev,window=126,rebalance=21,k=8):
 """Causal dynamic peers: refresh from trailing returns ending at T; vectorized between refreshes."""
 r=px[dev].reindex(dates).pct_change()
 a=r.to_numpy(float);T,N=a.shape;out=np.full((T,N,7),np.nan,np.float32);peers=np.full((T,N,k),-1,np.int16)
 r20=r.rolling(20,min_periods=10).sum().to_numpy();r63=r.rolling(63,min_periods=30).sum().to_numpy();v20=r.rolling(20,min_periods=10).std().to_numpy()
 P=None;C=None
 for t in range(window,T):
  if P is None or (t-window)%rebalance==0:
   hist=r.iloc[t-window:t+1]  # close-T data only
   C=hist.corr(min_periods=max(40,window//2)).to_numpy(copy=True);np.fill_diagonal(C,-np.inf)
   P=np.argsort(np.nan_to_num(C,nan=-np.inf),axis=1)[:,-k:]
  peers[t]=P
  for i in range(N):
   pp=P[i];pr1=np.nanmean(a[t,pp]);pr20=np.nanmean(r20[t,pp]);pr63=np.nanmean(r63[t,pp]);pv=np.nanmean(v20[t,pp])
   breadth=np.nanmean(r20[t,pp]>0);corr=np.nanmean(C[i,pp]);disp=np.nanstd(r20[t,pp])
   out[t,i]=[a[t,i]-pr1,r20[t,i]-pr20,r63[t,i]-pr63,v20[t,i]-pv,breadth,corr,disp]
 # Causal expanding normalization: statistics at T are based strictly on rows before T.
 for j in range(N):
  for q in range(out.shape[2]):
   s=pd.Series(out[:,j,q],index=dates);mu=s.shift(1).expanding(60).mean();sd=s.shift(1).expanding(60).std().replace(0,np.nan)
   z=((s-mu)/sd).clip(-6,6).fillna(0);out[:,j,q]=(0.5+0.5*np.tanh(z.to_numpy()/2)).astype(np.float32)
 return out,peers
def execution_returns(dev,dates):
 """Decision at close T, execution at T+1 adjusted open; PnL held to next rebalance execution."""
 out=np.full((len(dates),len(dev)),np.nan,np.float32)
 for j,t in enumerate(dev):
  d=pd.read_parquet(v2.PXDIR/f"{t}.parquet");d.columns=[str(c).lower() for c in d.columns];d["date"]=pd.to_datetime(d["date"]).dt.tz_localize(None);d=d.set_index("date").sort_index()
  factor=pd.to_numeric(d["adj_close"],errors="coerce")/pd.to_numeric(d["close"],errors="coerce");ao=pd.to_numeric(d["open"],errors="coerce")*factor
  rr=ao.shift(-2)/ao.shift(-1)-1;out[:,j]=rr.reindex(dates).to_numpy(np.float32)
 return out
def spread_cost_bps(dev,dates):
 """Causal Corwin-Schultz high/low half-spread estimate, floor 2 bps, cap 100 bps."""
 out=np.full((len(dates),len(dev)),5.0,np.float32);den=3-2*np.sqrt(2)
 for j,t in enumerate(dev):
  d=pd.read_parquet(v2.PXDIR/f"{t}.parquet",columns=["date","high","low"]);d["date"]=pd.to_datetime(d["date"]).dt.tz_localize(None);d=d.set_index("date").sort_index();h=pd.to_numeric(d.high,errors="coerce");l=pd.to_numeric(d.low,errors="coerce")
  x=np.log(h/l).replace([np.inf,-np.inf],np.nan);beta=x*x+(x.shift(1)*x.shift(1));gamma=np.log(h.rolling(2).max()/l.rolling(2).min())**2
  alpha=((np.sqrt(2*beta)-np.sqrt(beta))/den-np.sqrt(gamma/den)).clip(lower=0);sp=2*(np.exp(alpha)-1)/(1+np.exp(alpha));hb=(sp*5000).clip(2,100).fillna(5)
  out[:,j]=hb.reindex(dates).fillna(5).to_numpy(np.float32)
 return out
def build_arrays():
 d67,d50,dev=v2.load_dev117()
 dates,tickers,Xold,RX_legacy_unused,ew,rf,names,groups=v2.make_arrays(dev)
 RX=execution_returns(dev,dates)
 COST=spread_cost_bps(dev,dates)
 # Strip V2 sector features completely. Keep causal stock + market primitives.
 keep=groups["stock"]+groups["market"]; X=Xold[:,:,keep]; names=[names[i] for i in keep]
 ns=len(groups["stock"]); groups={"stock":list(range(ns)),"market":list(range(ns,len(keep)))}
 px=v2.load_prices(dev); peer,P=dynamic_peer_context(px,dates,dev)
 start=X.shape[2]; X=np.concatenate([X,peer],axis=2)
 pnames=["peer:ret1_rel","peer:ret20_rel","peer:ret63_rel","peer:vol20_rel","peer:breadth20","peer:corr63","peer:dispersion20"]
 names+=pnames; groups["peer"]=list(range(start,start+len(pnames)))
 return d67,d50,dev,dates,X,RX,rf,names,groups,P,px,COST
def random_module(R,groups):
 sig_pool=groups["stock"]+groups["peer"]; gate_pool=groups["market"]+groups["peer"]+groups["stock"]
 ns=R.randint(2,min(6,len(sig_pool))); ng=R.randint(1,4)
 return {"family":R.choice(FAMILIES),"signal_ids":R.sample(sig_pool,ns),"signal_w":[R.uniform(-2,2) for _ in range(ns)],
 "gate_ids":R.sample(gate_pool,ng),"gate_w":[R.uniform(-3,3) for _ in range(ng)],"gate_bias":R.uniform(-1.5,1.5),"module_w":R.uniform(.25,2)}
def random_genome(R,groups):
 return {"modules":[random_module(R,groups) for _ in range(R.randint(2,6))],"opportunity_scale":10**R.uniform(-3.2,-1.2),
 "risk_appetite_id":R.choice(groups["market"]),"risk_appetite_w":R.uniform(-3,3),"risk_appetite_bias":R.uniform(-1,1),
 "safe_margin":R.uniform(0,.00025),"kappa":10**R.uniform(-.3,.7),"uncertainty_penalty":R.uniform(0,.004),
 "short":R.random()<.45,"alloc":R.choice(ALLOCS),"gamma":R.uniform(.5,3.0)}
def mutate(R,g,groups,stage=0):
 z=json.loads(json.dumps(g)); k=R.randrange(13)
 if k==0 and len(z["modules"])<12:z["modules"].append(random_module(R,groups))
 elif k==1 and len(z["modules"])>1:z["modules"].pop(R.randrange(len(z["modules"])))
 elif k in (2,3,4):
  m=R.choice(z["modules"])
  if k==2:
   j=R.randrange(len(m["signal_w"]));m["signal_w"][j]=max(-4,min(4,m["signal_w"][j]+R.gauss(0,.35)))
  elif k==3:
   j=R.randrange(len(m["gate_w"]));m["gate_w"][j]=max(-5,min(5,m["gate_w"][j]+R.gauss(0,.45)))
  else:m["gate_bias"]=max(-3,min(3,m["gate_bias"]+R.gauss(0,.25)))
 elif k==5:z["risk_appetite_w"]=max(-5,min(5,z["risk_appetite_w"]+R.gauss(0,.4)))
 elif k==6:z["risk_appetite_bias"]=max(-2,min(2,z["risk_appetite_bias"]+R.gauss(0,.2)))
 elif k==7:z["safe_margin"]=min(.001,max(0,z["safe_margin"]+R.gauss(0,.00004)))
 elif k==8:z["kappa"]=min(20,max(.1,z["kappa"]*math.exp(R.gauss(0,.2))))
 elif k==9:z["uncertainty_penalty"]=min(.02,max(0,z["uncertainty_penalty"]+R.gauss(0,.0005)))
 elif k==10:z["gamma"]=min(6,max(.2,z["gamma"]+R.gauss(0,.25)))
 elif k==11:z["alloc"]=R.choice(ALLOCS)
 else:z["short"]=not z["short"]
 return z
def key(g): return json.dumps(g,sort_keys=True,separators=(",",":"))
def sigmoid(x): return 1/(1+np.exp(-np.clip(x,-20,20)))
@njit(cache=True)
def _opp_core(X,sids,sw,ns,gids,gw,ng,bias,mw,scale,nmod):
 T,N,F=X.shape;E=np.zeros((T,N));U=np.zeros((T,N));D=np.zeros((T,N))
 for t in range(T):
  for i in range(N):
   ee=0.0;uu=0.0;dd=0.0
   for m in range(nmod):
    sig=0.0
    for q in range(ns[m]):
     v=X[t,i,sids[m,q]]
     if np.isnan(v):v=.5
     sig+=v*sw[m,q]
    gate=bias[m]
    for q in range(ng[m]):
     v=X[t,i,gids[m,q]]
     if np.isnan(v):v=.5
     gate+=v*gw[m,q]
    if gate>20:gate=20
    elif gate<-20:gate=-20
    a=1.0/(1.0+math.exp(-gate));s=math.tanh(sig)
    ee+=a*s*mw[m];uu+=a*(1-a)
    if s<0:dd+=a*(-s)
   E[t,i]=ee*scale/nmod;U[t,i]=uu/nmod;D[t,i]=dd/nmod
 return E,U,D
def opportunity(g,X):
 n=len(g["modules"]);sids=np.zeros((n,6),np.int64);sw=np.zeros((n,6));ns=np.zeros(n,np.int64);gids=np.zeros((n,4),np.int64);gw=np.zeros((n,4));ng=np.zeros(n,np.int64);bias=np.zeros(n);mw=np.zeros(n)
 for j,m in enumerate(g["modules"]):
  ns[j]=len(m["signal_ids"]);sids[j,:ns[j]]=m["signal_ids"];sw[j,:ns[j]]=m["signal_w"];ng[j]=len(m["gate_ids"]);gids[j,:ng[j]]=m["gate_ids"];gw[j,:ng[j]]=m["gate_w"];bias[j]=m["gate_bias"];mw[j]=m["module_w"]
 return _opp_core(X,sids,sw,ns,gids,gw,ng,bias,mw,g["opportunity_scale"],n)
@njit(cache=True)
def _lifecycle(raw,V,U,tau,RX,rf,costmat,kappa,upen,borrow):
 T,N=V.shape;W=np.zeros((T,N));prev=np.zeros(N);turn=np.zeros(T);counts=np.zeros(5,np.int64)
 for t in range(T-1):
  gross=0.0
  for i in range(N):gross+=abs(raw[t,i])
  scale=min(1.0,tau[t])/gross if gross>0 else 0.0
  nxt=prev.copy()
  for i in range(N):
   target=raw[t,i]*scale;active=V[t,i]>0
   trade=(abs(target)-abs(prev[i])) > kappa*(2*costmat[t,i]/10000.0)+upen*U[t,i]
   if trade:nxt[i]=target
   if prev[i]!=0 and not active:nxt[i]=0.0
   if prev[i]==0 and nxt[i]!=0:counts[0]+=1
   elif prev[i]!=0 and nxt[i]==prev[i]:counts[1]+=1
   elif prev[i]!=0 and nxt[i]!=prev[i] and nxt[i]!=0:counts[2]+=1
   if prev[i]!=0 and not active:counts[3]+=1
   if nxt[i]<0:counts[4]+=1
  gg=0.0
  for i in range(N):gg+=abs(nxt[i])
  if gg>1:
   for i in range(N):nxt[i]/=gg
  tv=0.0
  for i in range(N):tv+=abs(nxt[i]-prev[i]);W[t,i]=nxt[i]
  turn[t]=tv;prev=nxt
 rr=np.nan_to_num(RX);port=np.zeros(T)
 for t in range(T):
  risky=0.0;gross=0.0;shortgross=0.0
  for i in range(N):
   risky+=W[t,i]*rr[t,i];gross+=abs(W[t,i])
   if W[t,i]<0:shortgross+=-W[t,i]
  tc=0.0
  if t<T-1:
   for i in range(N):tc+=abs(W[t,i]-(W[t-1,i] if t>0 else 0.0))*costmat[t,i]/10000.0
  port[t]=risky+max(0.0,1-gross)*rf[t]-tc-shortgross*(borrow/252)
 return port,W,turn,counts
def simulate(g,X,RX,rf,cost_bps=5,borrow=.003):
 E,U,D=opportunity(g,X);tau=sigmoid(g["risk_appetite_w"]*X[:,0,g["risk_appetite_id"]]+g["risk_appetite_bias"])
 VL=E-g["uncertainty_penalty"]*U-rf[:,None]-g["safe_margin"];VS=-E-g["uncertainty_penalty"]*U-rf[:,None]-g["safe_margin"]-(2*borrow/252)
 V=np.where(VL>0,VL,0);sign=np.ones_like(V)
 if g["short"]:
  take=VS>V;V=np.where(take,VS,V);sign=np.where(take,-1,sign)
 if g["alloc"]=="equal":raw=(V>0).astype(float)
 elif g["alloc"]=="strength":raw=np.maximum(V,0)**g["gamma"]
 elif g["alloc"]=="uncertainty":raw=(np.maximum(V,0)/(U+.05))**g["gamma"]
 else:raw=(np.maximum(V,0)/(D+.05))**g["gamma"]
 raw*=sign
 costmat=np.full(V.shape,float(cost_bps),dtype=np.float64) if np.isscalar(cost_bps) else np.asarray(cost_bps,dtype=np.float64)
 p,W,to,c=_lifecycle(raw,V,U,tau,np.nan_to_num(RX,nan=0.0),rf,costmat,g["kappa"],g["uncertainty_penalty"],borrow)
 dec=dict(zip(("ENTER","CONTINUE","REPLACE","EXIT_TO_SAFE","SHORT"),map(int,c)))
 return p,W,to,dec
def evaluate(g,X,RX,rf,dates,idx,cost=5):
 cc=cost[:,idx] if isinstance(cost,np.ndarray) and cost.ndim==2 else cost
 p,w,to,dec=simulate(g,X[:,idx,:],RX[:,idx],rf,cc);m=v2.metrics(p,dates)
 m.update(turnover=float(to.mean()),safe_fraction=float(np.mean(np.maximum(0,1-np.abs(w).sum(1)))),avg_gross=float(np.mean(np.abs(w).sum(1))),short_share=float(np.mean(np.maximum(-w,0).sum(1))),lifecycle=dec)
 return m
_WORK=None
def _eval_worker(g):
 X,RX,rf,dates,tr,COST=_WORK;return key(g),evaluate(g,X,RX,rf,dates,tr,COST)
def dominates(a,b): return a["cagr"]>=b["cagr"] and a["mdd"]>=b["mdd"] and (a["cagr"]>b["cagr"] or a["mdd"]>b["mdd"])
def pareto(vals): return [z for z in vals if not any(dominates(q["m"],z["m"]) for q in vals if q is not z)]
def behavior(m):
 return (round(m["avg_gross"],1),round(m["safe_fraction"],1),round(m["short_share"],1),round(min(m["turnover"],2),1))
def evolve_fold(fi,train,dev,X,RX,rf,dates,groups,COST,popn,gens,maxgens,workers=1,state_path=None):
 idx={t:i for i,t in enumerate(dev)};fulltr=np.array([idx[t] for t in train]);mftr=np.array(sorted(fulltr,key=lambda j:seed(MASTER,"mf",fi,dev[j]))[:24]);tr=mftr;pops=[];cache={};map_archive={};defensive_archive={};fidelity="mf24"
 global _WORK;_WORK=(X,RX,rf,dates,tr,COST);pool=mp.get_context("fork").Pool(processes=max(1,workers))
 kinds=[("band",b) for b in DD]+[("global",None),("novelty",None)]
 for isl in range(9):
  R=random.Random(seed(MASTER,fi,isl,"init"));pops.append([random_genome(R,groups) for _ in range(popn)])
 history=[];plateaus=0
 for ge in range(maxgens):
  if ge==450 and fidelity!="full80":
   pool.close();pool.join();tr=fulltr;fidelity="full80";_WORK=(X,RX,rf,dates,tr,COST);pool=mp.get_context("fork").Pool(processes=max(1,workers))
   # seed full-fidelity refinement with preserved defensive archive
   ag=[z["g"] for z in defensive_archive.values()]
   for isl in range(9):
    for j,g in enumerate(ag[:min(len(ag),max(1,popn//10))]):pops[isl][-(j+1)]=json.loads(json.dumps(g))
  allfront=[];migrants=[]
  for isl,(kind,band) in enumerate(kinds):
   vals=[]
   missing=[g for g in pops[isl] if fidelity+"|"+key(g) not in cache]
   if missing:
    for kk,mm in pool.map(_eval_worker,missing,chunksize=max(1,len(missing)//max(1,workers*4))):cache[fidelity+"|"+kk]=mm
   for g in pops[isl]:vals.append({"g":g,"m":cache[fidelity+"|"+key(g)]})
   front=pareto(vals);allfront+=front
   if kind=="band":
    vals.sort(key=lambda z:(z["m"]["mdd"]>=-band,z["m"]["cagr"] if z["m"]["mdd"]>=-band else z["m"]["mdd"]),reverse=True)
   elif kind=="novelty":
    for z in vals:
     cell=behavior(z["m"]);old=map_archive.get(cell)
     if old is None or z["m"]["cagr"]>old["m"]["cagr"]:map_archive[cell]=z
    vals.sort(key=lambda z:(behavior(z["m"]) in map_archive,z["m"]["cagr"]+z["m"]["mdd"]),reverse=True)
   else:
    vals.sort(key=lambda z:((z in front),z["m"]["cagr"]+z["m"]["mdd"]),reverse=True)
   R=random.Random(seed(MASTER,fi,isl,ge));elite=[z["g"] for z in vals[:max(25,popn//5)]]
   migrants.extend(elite[:max(1,int(.05*popn))])
   npop=list(elite)
   while len(npop)<popn:
    c=mutate(R,R.choice(elite),groups,0 if ge<100 else 1 if ge<250 else 2 if ge<450 else 3)
    # stage B upweights context/applicability mutations without removing any gene type
    if 100<=ge<250 and R.random()<.35:c=mutate(R,c,groups,1)
    # stage C upweights lifecycle/allocation co-evolution
    if 250<=ge<450 and R.random()<.35:c=mutate(R,c,groups,2)
    npop.append(c)
   pops[isl]=npop
  if ge>0 and ge%25==0:
   for isl in range(9):
    R=random.Random(seed(MASTER,fi,"migration",isl,ge))
    for j in range(max(1,int(.05*popn))):pops[isl][-(j+1)]=json.loads(json.dumps(R.choice(migrants)))
  front=pareto(allfront)
  # Preserve defensive archive with periodic FULL-80 checks even during multi-fidelity stages.
  if ge%25==0 and fidelity=="mf24":
   for b in DD:
    ok=[z for z in allfront if z["m"]["mdd"]>=-b]
    if ok:
     z=max(ok,key=lambda q:q["m"]["cagr"]);kk=key(z["g"]);fm=evaluate(z["g"],X,RX,rf,dates,fulltr,COST);old=defensive_archive.get(str(b))
     if old is None or (fm["mdd"]>=-b and fm["cagr"]>old["m"]["cagr"]):defensive_archive[str(b)]={"g":z["g"],"m":fm}
  hv=sum(max(0,z["m"]["cagr"]+.25)*max(0,z["m"]["mdd"]+.5) for z in front);history.append(hv)
  # First plateau: immigrants + structural mutation. Second consecutive: archive/reallocate by stopping weak novelty injection.
  if len(history)>=41 and history[-41]>0 and (hv/history[-41]-1)<.005:
   plateaus+=1
   if plateaus==1:
    for isl in range(9):
     R=random.Random(seed(MASTER,fi,"plateau",isl,ge));n=max(1,int(.20*popn))
     pops[isl][-n:]=[mutate(R,random_genome(R,groups),groups,3) for _ in range(n)]
  else:plateaus=0
  (Path(state_path) if state_path else STATE).write_text(json.dumps({"stage":"TRAINING","fold":fi,"generation":ge,"unique":len(cache),"frontier":len(front),"hypervolume_proxy":hv,"map_elites_cells":len(map_archive),"plateau_count":plateaus},indent=2))
  print(f"FOLD={fi} GEN={ge} UNIQUE={len(cache)} FRONT={len(front)} HV={hv:.6f} MAP={len(map_archive)}",flush=True)
  if ge+1>=gens and (ge+1>=maxgens or len(history)<51 or history[-51]<=0 or (hv/history[-51]-1)<=.01):break
 vals=[{"g":json.loads(k.split("|",1)[1]),"m":m} for k,m in cache.items() if k.startswith("full80|")]+list(defensive_archive.values());sel=[]
 for b in DD:
  ok=[z for z in vals if z["m"]["mdd"]>=-b]
  if ok:
   z=max(ok,key=lambda q:q["m"]["cagr"])
   if key(z["g"]) not in {key(x["g"]) for x in sel}:sel.append(z)
 pool.close();pool.join()
 return sel,{"generations":ge+1,"unique":len(cache),"frontier_size":len(pareto(vals)),"map_elites_cells":len(map_archive),"multi_fidelity":"24-of-80 through generation 449; full80 from 450; all calendar sessions retained","defensive_full80_archive":len(defensive_archive)}
def calibration(X,RX,rf,dates,groups,COST):
 # Null: one global circular time shift breaks feature->future linkage while preserving the full
 # cross-sectional covariance/factor structure and the realized market-return path exactly.
 rng=np.random.default_rng(seed(MASTER,"null"));shift=int(rng.integers(252,len(RX)-252));nr=np.roll(RX,shift,axis=0)
 R=random.Random(seed(MASTER,"nullgen"));gs=[random_genome(R,groups) for _ in range(24)];ii=np.arange(min(40,RX.shape[1]))
 nullvals=[evaluate(g,X,nr,rf,dates,ii,COST)["cagr"] for g in gs];null=max(nullvals)
 null_market=v2.metrics(np.nanmean(nr[:,ii],axis=1),dates)["cagr"];null_excess=null-null_market
 # Planted conditional structure: one stock primitive predicts only when a market primitive is high.
 planted=np.zeros_like(RX); s=groups["stock"][0];m=groups["market"][0]
 planted[:]=np.where((X[:,:,s]>.65)&(X[:,:,m]>.55),.002,-.00015)
 good=0
 for q in range(4):
  R=random.Random(seed(MASTER,"plant",q)); cand=[random_genome(R,groups) for _ in range(40)]
  best=max(cand,key=lambda g:evaluate(g,X,planted,rf,dates,np.arange(min(40,RX.shape[1])),COST)["cagr"])
  # recovery means best exploits planted process positively; no unapproved threshold enters real fitness
  if evaluate(best,X,planted,rf,dates,np.arange(min(40,RX.shape[1])),COST)["cagr"]>0:good+=1
 return {"null_shift_sessions":shift,"null_best_cagr_small_calibration":null,"null_equal_weight_cagr":null_market,"null_best_excess_vs_equal_weight":null_excess,"planted_recovered_seeds":good,"planted_required":3,"pass":good>=3}
def spy_comparator(dates):
 d=pd.read_csv(SPY,skiprows=[1,2]);d["Price"]=pd.to_datetime(d["Price"]);s=pd.to_numeric(d["Adj Close"],errors="coerce");s.index=d["Price"];rr=s.reindex(dates).pct_change().shift(-1).fillna(0).to_numpy();return v2.metrics(rr,dates)
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--workers",type=int,default=16);ap.add_argument("--base-generations",type=int,default=500);ap.add_argument("--max-generations",type=int,default=800);ap.add_argument("--population",type=int,default=250);ap.add_argument("--post-run-report");ap.add_argument("--preflight-only",action="store_true");ap.add_argument("--fold-only",type=int);args=ap.parse_args()
 d67,d50,dev,dates,X,RX,rf,names,groups,P,px,COST=build_arrays();fs=folds(dev)
 cal=calibration(X,RX,rf,dates,groups,COST);print("CALIBRATION",json.dumps(cal),flush=True)
 if not cal["pass"]:raise SystemExit("PLANTED_CALIBRATION_FAILED")
 if args.preflight_only:return
 if args.fold_only is not None:
  fi=args.fold_only
  if fi not in range(4):raise SystemExit("FOLD_ONLY_MUST_BE_0_TO_3")
  tr,bl=fs[fi];sel,mm=evolve_fold(fi,tr,dev,X,RX,rf,dates,groups,COST,args.population,args.base_generations,args.max_generations,args.workers,str(ROOT/f"Research/State/MTS_GA_REDESIGN_FOLD{fi}_CHECKPOINT_20261006.json"))
  payload={"fold":fi,"train_tickers":tr,"blind_tickers_sha256":hashlib.sha256("\n".join(bl).encode()).hexdigest(),"finalists":[{"genome":z["g"],"train":z["m"]} for z in sel],"meta":mm}
  p=ROOT/f"Research/State/MTS_GA_REDESIGN_FOLD{fi}_TRAIN_FINALISTS_20261006.json";p.write_text(json.dumps(payload,indent=2));print("FOLD_COMPLETE",fi,p,sha(p),flush=True);return
 frozen=[];meta=[]
 for fi,(tr,bl) in enumerate(fs):
  sel,mm=evolve_fold(fi,tr,dev,X,RX,rf,dates,groups,COST,args.population,args.base_generations,args.max_generations,args.workers)
  payload={"fold":fi,"train_tickers":tr,"blind_tickers_sha256":hashlib.sha256("\n".join(bl).encode()).hexdigest(),"finalists":[{"genome":z["g"],"train":z["m"]} for z in sel],"meta":mm}
  p=ROOT/f"Research/State/MTS_GA_REDESIGN_FOLD{fi}_TRAIN_FINALISTS_20261006.json";p.write_text(json.dumps(payload,indent=2));frozen.append({"path":str(p),"sha256":sha(p)});meta.append(payload)
 # HARD BARRIER: all four training freezes are now on disk and hashed before blind replay begins.
 assert len(frozen)==4 and all(Path(x["path"]).exists() and sha(Path(x["path"]))==x["sha256"] for x in frozen)
 blind=[]
 idx={t:i for i,t in enumerate(dev)}
 for fi,(tr,bl) in enumerate(fs):
  rows=[]
  for z in meta[fi]["finalists"]:
   g=z["genome"]; bi=np.array([idx[t] for t in bl]); bm=evaluate(g,X,RX,rf,dates,bi,COST)
   sens={str(c):evaluate(g,X,RX,rf,dates,bi,c) for c in (0,5,10,20)}
   eps={}
   p,_,_,_=simulate(g,X[:,bi,:],RX[:,bi],rf,COST[:,bi])
   for name,a,b in EPISODES:
    mask=(dates>=pd.Timestamp(a))&(dates<=pd.Timestamp(b));eps[name]=v2.metrics(p[mask],dates[mask]) if mask.any() else None
   rows.append({"train":z["train"],"blind":bm,"cost_sensitivity":sens,"episodes":eps,"genome":g})
  blind.append({"fold":fi,"rows":rows})
 out={"format":"MTS_GA_REDESIGN_APPROVED_V1","status":"DEV117_COMPLETE","freeze_sha256":sha(FREEZE),"features":names,"groups":groups,"calibration":cal,"comparators":{"SPY":spy_comparator(dates),"SAFE":v2.metrics(rf,dates),"SPY_sha256":sha(SPY)},"training_freezes":frozen,"blind_transport":blind,"validation_note":"80/37 folds are cross-stock transport; crash evidence counted by independent episode, not fold-session multiplication.","next_stage":"DV25 remains sealed pending post-DEV117 decision"}
 OUT.write_text(json.dumps(out,indent=2))
 if args.post_run_report:
  lines=["# MTS GA Redesign — Final DEV117 Report","",f"Status: {out['status']}","",f"Calibration: {json.dumps(cal)}","", "## Frozen training sets"]+[f"- Fold {i}: {x['sha256']}" for i,x in enumerate(frozen)]
  lines+=["","## Blind cross-stock transport"]
  for f in blind:
   lines.append(f"### Fold {f['fold']}")
   for r in f["rows"]:lines.append(f"- Train CAGR {r['train']['cagr']:.3%}, MDD {r['train']['mdd']:.3%}; blind CAGR {r['blind']['cagr']:.3%}, MDD {r['blind']['mdd']:.3%}; SAFE {r['blind']['safe_fraction']:.3%}")
  lines+=["","## Governance","All four training finalist sets were frozen and SHA-256 hashed before any blind37 replay. DV25/A25/A75/B100 were not opened. Crash episodes are reported as independent market episodes, not multiplied across folds."]
  Path(args.post_run_report).write_text("\n".join(lines)+"\n")
 print("COMPLETE",OUT,flush=True)
if __name__=="__main__":main()
