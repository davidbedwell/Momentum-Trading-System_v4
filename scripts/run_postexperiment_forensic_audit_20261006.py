import json, pathlib, importlib.util, numpy as np, pandas as pd, random, hashlib
ROOT=pathlib.Path("/home/ubuntu/Momentum-Trading-System_v4")
spec=importlib.util.spec_from_file_location("ga",ROOT/"scripts/run_ga_redesign_approved_20261006.py"); ga=importlib.util.module_from_spec(spec);spec.loader.exec_module(ga)
d67,d50,dev,dates,X,RX,rf,names,groups,P,px,COST=ga.build_arrays(); fs=ga.folds(dev); idx={t:i for i,t in enumerate(dev)}
spy=pd.read_csv(ga.SPY,skiprows=[1,2]);spy["Price"]=pd.to_datetime(spy["Price"]);ss=pd.to_numeric(spy["Adj Close"],errors="coerce");ss.index=spy["Price"];spyret=ss.reindex(dates).pct_change().shift(-1).fillna(0).to_numpy()
def metrics(r): return ga.v2.metrics(np.asarray(r),dates)
def forensic(g,ii):
 E,U,D=ga.opportunity(g,X[:,ii,:]); tau=ga.sigmoid(g["risk_appetite_w"]*X[:,ii[0],g["risk_appetite_id"]]+g["risk_appetite_bias"])
 VL=E-g["uncertainty_penalty"]*U-rf[:,None]-g["safe_margin"];VS=-E-g["uncertainty_penalty"]*U-rf[:,None]-g["safe_margin"]-(2*.003/252);V=np.where(VL>0,VL,0);sg=np.ones_like(V)
 if g["short"]:
  take=VS>V;V=np.where(take,VS,V);sg=np.where(take,-1,sg)
 if g["alloc"]=="equal": raw=(V>0).astype(float)
 elif g["alloc"]=="strength": raw=np.maximum(V,0)**g["gamma"]
 elif g["alloc"]=="uncertainty": raw=(np.maximum(V,0)/(U+.05))**g["gamma"]
 else: raw=(np.maximum(V,0)/(D+.05))**g["gamma"]
 raw*=sg; gross=np.abs(raw).sum(1);scale=np.where(gross>0,np.minimum(1,tau)/gross,0);target=raw*scale[:,None]
 p,W,to,dec=ga.simulate(g,X[:,ii,:],RX[:,ii],rf,COST[:,ii])
 prev=np.vstack([np.zeros((1,len(ii))),W[:-1]])
 active=V>0; desired_reduce=active&(np.abs(target)+1e-15<np.abs(prev))&(np.abs(prev)>0)
 executed_reduce=desired_reduce&(np.abs(W)+1e-15<np.abs(prev))
 stuck=desired_reduce&~executed_reduce
 gg=np.abs(W).sum(1); same=gg*spyret+(1-gg)*rf
 eligible=np.nanmean(np.nan_to_num(RX[:,ii],nan=0.0),axis=1); same_elig=gg*eligible+(1-gg)*rf
 return {"m":ga.evaluate(g,X,RX,rf,dates,ii,COST),"desired_active_reductions":int(desired_reduce.sum()),"executed_active_reductions":int(executed_reduce.sum()),"stuck_active_reductions":int(stuck.sum()),"stuck_rate":float(stuck.sum()/max(1,desired_reduce.sum())),"same_exposure_spy":metrics(same),"same_exposure_eligible_equal":metrics(same_elig),"mts_minus_same_spy_total_return":float(np.prod(1+p)-np.prod(1+same)),"mts_minus_same_eligible_total_return":float(np.prod(1+p)-np.prod(1+same_elig))}
out={"status":"FORENSIC_DIAGNOSTIC_CONSUMED_DEV117_ONLY","protected_opened":False,"folds":[]}
for fi,(tr,bl) in enumerate(fs):
 f=json.loads((ROOT/f"Research/State/MTS_GA_REDESIGN_FOLD{fi}_TRAIN_FINALISTS_20261006.json").read_text()); ti=np.array([idx[t] for t in tr]);bi=np.array([idx[t] for t in bl]); rows=[]
 for ri,z in enumerate(f["finalists"]):
  g=z["genome"]; base=forensic(g,bi); R=random.Random(int(hashlib.sha256(f"audit|{fi}|{ri}".encode()).hexdigest()[:16],16)); subs=[]
  for k in range(12):
   pick=np.array(sorted(R.sample(list(ti),37))); subs.append(ga.evaluate(g,X,RX,rf,dates,pick,COST))
  rows.append({"row":ri,"train_reported":z["train"],"blind_forensic":base,"train37_subsamples":{"n":len(subs),"cagr_median":float(np.median([x["cagr"] for x in subs])),"cagr_min":float(np.min([x["cagr"] for x in subs])),"cagr_max":float(np.max([x["cagr"] for x in subs])),"mdd_median":float(np.median([x["mdd"] for x in subs])),"gross_median":float(np.median([x["avg_gross"] for x in subs])),"safe_median":float(np.median([x["safe_fraction"] for x in subs]))}})
 out["folds"].append({"fold":fi,"train_n":80,"blind_n":37,"rows":rows})
op=ROOT/"Research/Reports/MTS_POSTEXPERIMENT_FORENSIC_AUDIT_20261006.json";op.write_text(json.dumps(out,indent=2));print("AUDIT_OUT",op);print("PROTECTED_OPENED",out["protected_opened"])
