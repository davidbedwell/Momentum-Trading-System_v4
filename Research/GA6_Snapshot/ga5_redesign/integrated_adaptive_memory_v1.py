"""Integrate chop, volume and market factors into persistent expandable niche memory.
Prototype: calibrated novelty, stable identities, chronological train/holdout, no trade outcomes.
"""
import json
from pathlib import Path
import numpy as np,pandas as pd
from sklearn.cluster import KMeans
R=Path('/opt/mts/ga5_redesign');O=R/'integrated_adaptive_memory_v1';O.mkdir(exist_ok=True)
base=pd.read_parquet(R/'exploratory79_ga4_enriched.parquet');chop=pd.read_parquet(R/'chop_features_v1/historical_disorganization_features.parquet')
base=base[base.ticker.isin(['ACN','AMGN'])].copy();base['date']=pd.to_datetime(base.date);chop['date']=pd.to_datetime(chop.date)
cols=['trend','momentum','volatility','breadth','relative_strength','ga4_relative_volume_20__v1','ga4_volume_slope_20__v1','efficiency_10','efficiency_20','efficiency_40','reversal_rate_10','reversal_rate_20','reversal_rate_40','net_to_volatility_10','net_to_volatility_20','net_to_volatility_40','range_width_20','volume_variability_20']
p=base.merge(chop,on=['ticker','date'],how='inner').dropna(subset=cols).sort_values(['ticker','date']);a=p[p.ticker=='ACN'].reset_index(drop=True);b=p[p.ticker=='AMGN'].reset_index(drop=True)
# Robust feature scale learned ONLY from first 56% ACN, then permanently frozen.
split=int(len(a)*.7);nfit=int(split*.8);bcut=int(len(b)*.7)
rawa=a[cols].to_numpy(float);rawb=b[cols].to_numpy(float);median=np.median(rawa[:nfit],axis=0);q1=np.quantile(rawa[:nfit],.25,axis=0);q3=np.quantile(rawa[:nfit],.75,axis=0);scale=np.maximum(q3-q1,1e-5)
xa=np.clip((rawa-median)/scale,-5,5);xb=np.clip((rawb-median)/scale,-5,5)
seed=KMeans(n_clusters=6,random_state=37,n_init=10).fit(xa[:nfit]);centers=[v.copy() for v in seed.cluster_centers_];anchors=[v.copy() for v in centers];ids=[f'NICHE-{i+1:04d}' for i in range(6)];counts=np.bincount(seed.labels_,minlength=6).astype(int).tolist()
cal=xa[nfit:split];dcal=np.linalg.norm(cal[:,None,:]-np.array(centers)[None,:,:],axis=2);assignment=dcal.argmin(axis=1);threshold=[];radii=[]
for j in range(6):
 ds=dcal[assignment==j,j];ds=ds if len(ds)>=20 else dcal.min(axis=1)
 threshold.append(float(np.quantile(ds,.99)));radii.append(float(np.median(ds)))
pending=[];events=[];logs=[]
for i,v in enumerate(xb[:bcut]):
 ds=np.linalg.norm(np.array(centers)-v,axis=1);j=int(ds.argmin());distance=float(ds[j]);action='recognized';date=str(b.at[i,'date'].date())
 if distance>threshold[j]:
  pending.append((i,v.copy()));action='provisional'
  local=[(k,w) for k,w in pending if i-k<=126 and np.linalg.norm(w-v)<=max(.2,radii[j])]
  # Promote only with multiple independent days; criteria are exploratory, not certified.
  if len(local)>=5:
   candidate=np.mean([w for _,w in local],axis=0)
   if float(np.linalg.norm(np.array(centers)-candidate,axis=1).min())>threshold[j]:
    nid=f'NICHE-{len(ids)+1:04d}';ids.append(nid);centers.append(candidate);anchors.append(candidate.copy());counts.append(len(local));threshold.append(threshold[j]);radii.append(radii[j]);action='promoted'
    events.append({'date':date,'id':nid,'support':len(local),'nearest_prior':ids[j]});pending=[(k,w) for k,w in pending if np.linalg.norm(w-candidate)>max(.2,radii[j])]
 else:
  centers[j]=.85*(.98*centers[j]+.02*v)+.15*anchors[j];counts[j]+=1
 logs.append({'date':date,'nearest_id':ids[j],'action':action,'memory_size':len(ids),'distance':distance})
orig=seed.cluster_centers_;current=np.array(centers)
def metrics(x):
 d0=np.linalg.norm(x[:,None,:]-orig[None,:,:],axis=2);d1=np.linalg.norm(x[:,None,:]-current[None,:,:],axis=2)
 return {'sessions':len(x),'mean_distance_before':float(d0.min(axis=1).mean()),'mean_distance_after':float(d1.min(axis=1).mean()),'original_assignment_retention':float(np.mean(d0.argmin(axis=1)==d1.argmin(axis=1))),'new_niche_fraction':float(np.mean(d1.argmin(axis=1)>=6))}
report={'status':'EXPLORATORY_NOT_CERTIFIED','features':cols,'initial_niches':6,'final_niches':len(ids),'new_niches':len(ids)-6,'promotions':events,'ACN_holdout':metrics(xa[split:]),'AMGN_holdout':metrics(xb[bcut:]),'limitations':['No calendar-synchronized cross-stock learning','Feature provenance PIT audit pending','Novelty quantile/window/support hyperparameters still heuristic','Cluster semantic distinctness and false discovery unverified','No learned no-trade policy']}
(O/'report.json').write_text(json.dumps(report,indent=2));(O/'memory.json').write_text(json.dumps({'schema':'integrated-adaptive-memory-v1','features':cols,'normalization_median':median.tolist(),'normalization_scale':scale.tolist(),'niches':[{'id':ids[j],'center':centers[j].tolist(),'anchor':anchors[j].tolist(),'observations':counts[j],'novelty_threshold':threshold[j]} for j in range(len(ids))],'events':events},indent=2));pd.DataFrame(logs).to_csv(O/'learning_decisions.csv',index=False)
print(json.dumps({k:v for k,v in report.items() if k!='promotions'},indent=2));print('promotions',len(events))
