"""Adaptive niche thresholds from ACN calibration, expandable memory, chronological ACN/AMGN replay.
Exploratory representation test, not a certified PIT study.
"""
import json
from pathlib import Path
import numpy as np,pandas as pd
from sklearn.cluster import KMeans
R=Path('/opt/mts/ga5_redesign');O=R/'adaptive_niche_memory_v1';O.mkdir(exist_ok=True)
F=['trend','momentum','volatility','breadth','relative_strength'];S=np.array([.06,.07,.015,.25,.06]);C=np.array([0,0,.015,.5,0])
p=pd.read_parquet(R/'exploratory79_ga4_enriched.parquet');p=p[p.ticker.isin(['ACN','AMGN'])].dropna(subset=F).copy();p['date']=pd.to_datetime(p.date)
a=p[p.ticker=='ACN'].sort_values('date').reset_index(drop=True);b=p[p.ticker=='AMGN'].sort_values('date').reset_index(drop=True)
xa=np.clip((a[F].to_numpy()-C)/S,-5,5);xb=np.clip((b[F].to_numpy()-C)/S,-5,5)
split=int(len(a)*.7);bcut=int(len(b)*.7);nfit=int(split*.8)
seed=KMeans(n_clusters=6,random_state=37,n_init=10).fit(xa[:nfit]);centers=[x.copy() for x in seed.cluster_centers_];anchors=[x.copy() for x in centers];ids=[f'NICHE-{i+1:04d}' for i in range(6)];counts=[int(x) for x in np.bincount(seed.labels_,minlength=6)]
# Calibrate niche-specific tail distances using unseen chronological ACN calibration segment.
cal=xa[nfit:split];cd=np.linalg.norm(cal[:,None,:]-np.array(centers)[None,:,:],axis=2);ci=cd.argmin(axis=1);threshold=[];radius=[]
for j in range(6):
 v=cd[ci==j,j];v=v if len(v)>=15 else cd.min(axis=1)
 threshold.append(float(np.quantile(v,.99)));radius.append(float(np.quantile(v,.5)))
# Candidate density threshold scales with observed recurrence under calibration, not a fixed observation count.
# Each candidate is evaluated by nearest-neighbor density relative to a calibrated local radius.
pending=[];events=[];decisions=[]
for i,v in enumerate(xb[:bcut]):
 d=np.linalg.norm(np.array(centers)-v,axis=1);j=int(d.argmin());dist=float(d[j]);date=str(b.at[i,'date'].date());action='recognized'
 if dist>threshold[j]:
  action='provisional';pending.append((i,v.copy()))
  neighborhood=[(t,w) for t,w in pending if i-t<=126 and np.linalg.norm(w-v)<=max(.2,radius[j])]
  # Empirical support: density must exceed the upper tail expected under ACN calibration.
  cal_neighbors=np.linalg.norm(cal-v,axis=1)<=max(.2,radius[j]);expected=float(cal_neighbors.mean())
  needed=max(3,int(np.ceil(len(neighborhood)*expected))+2)
  if len(neighborhood)>=needed:
   candidate=np.mean([w for _,w in neighborhood],axis=0)
   if np.min(np.linalg.norm(np.array(centers)-candidate,axis=1))>threshold[j]:
    nid=f'NICHE-{len(ids)+1:04d}';ids.append(nid);centers.append(candidate);anchors.append(candidate.copy());counts.append(len(neighborhood));threshold.append(threshold[j]);radius.append(radius[j]);action='promoted'
    events.append({'date':date,'id':nid,'support':len(neighborhood),'parent_nearest':ids[j],'calibrated_distance_threshold':threshold[j]});pending=[(t,w) for t,w in pending if np.linalg.norm(w-candidate)>max(.2,radius[j])]
 else:
  centers[j]=.85*(.98*centers[j]+.02*v)+.15*anchors[j];counts[j]+=1
 decisions.append({'date':date,'action':action,'nearest_id':ids[j],'memory_size':len(ids),'distance':dist,'threshold':threshold[j]})
orig=seed.cluster_centers_;now=np.array(centers)
def metric(x):
 d0=np.linalg.norm(x[:,None,:]-orig[None,:,:],axis=2);d1=np.linalg.norm(x[:,None,:]-now[None,:,:],axis=2)
 return {'sessions':len(x),'mean_distance_before':float(d0.min(axis=1).mean()),'mean_distance_after':float(d1.min(axis=1).mean()),'original_assignment_retention':float(np.mean(d0.argmin(axis=1)==d1.argmin(axis=1))),'new_niche_fraction':float(np.mean(d1.argmin(axis=1)>=6))}
report={'status':'EXPLORATORY_NOT_CERTIFIED','initial_niches':6,'final_niches':len(ids),'promotions':events,'ACN_holdout':metric(xa[split:]),'AMGN_holdout':metric(xb[bcut:]),'calibration_thresholds':threshold[:6],'limitations':['Novelty quantiles .99, window 126 and minimum support floor 3 remain design hyperparameters','Feature PIT provenance unverified','Not globally calendar-synchronized across stocks','Niche semantics and stability not independently certified','Only original five feature families included; volume exists in dataset but is not yet calibrated for this memory']}
(O/'report.json').write_text(json.dumps(report,indent=2));(O/'memory.json').write_text(json.dumps({'ids':ids,'centers':[x.tolist() for x in centers],'anchors':[x.tolist() for x in anchors],'counts':counts,'thresholds':threshold,'radii':radius,'events':events,'features':F},indent=2));pd.DataFrame(decisions).to_csv(O/'decisions.csv',index=False)
print(json.dumps(report,indent=2))
