"""Expandable persistent niche memory: recognize, flag novelty, promote recurring new niches.
Original six anchored and immutable IDs. No returns/profitability in learning.
"""
import json
from pathlib import Path
import numpy as np,pandas as pd
from sklearn.cluster import KMeans
R=Path('/opt/mts/ga5_redesign');O=R/'expandable_niche_memory_v1';O.mkdir(exist_ok=True)
F=['trend','momentum','volatility','breadth','relative_strength'];S=np.array([.06,.07,.015,.25,.06]);C=np.array([0,0,.015,.5,0])
z=pd.read_parquet(R/'exploratory79_ga4_enriched.parquet');z=z[z.ticker.isin(['ACN','AMGN'])].dropna(subset=F).copy();z['date']=pd.to_datetime(z.date)
a=z[z.ticker=='ACN'].sort_values('date').reset_index(drop=True);b=z[z.ticker=='AMGN'].sort_values('date').reset_index(drop=True)
xa=np.clip((a[F].to_numpy()-C)/S,-5,5);xb=np.clip((b[F].to_numpy()-C)/S,-5,5)
split=int(.7*len(a));bcut=int(.7*len(b));seed=KMeans(n_clusters=6,random_state=37,n_init=10).fit(xa[:split]);centers=[v.copy() for v in seed.cluster_centers_];anchors=[v.copy() for v in centers];ids=[f'NICHE-{i+1:04d}' for i in range(6)];counts=[int(v) for v in np.bincount(seed.labels_,minlength=6)]
# An unfamiliar observation must recur at >=5 distinct sessions with similar features.
# Avoid one-off outliers and reject proposals too close to existing niche centers.
novel=[];events=[];log=[];radius=1.15;threshold=2.75;min_support=5
for i,v in enumerate(xb[:bcut]):
 date=str(b.at[i,'date'].date());ds=np.linalg.norm(np.array(centers)-v,axis=1);j=int(ds.argmin());nearest=float(ds[j]);action='recognized'
 if nearest>threshold:
  novel.append((i,v.copy()));action='provisional_novelty'
  matching=[(ix,w) for ix,w in novel if i-ix<=126 and np.linalg.norm(w-v)<=radius]
  if len(matching)>=min_support:
   candidate=np.mean([w for _,w in matching],axis=0)
   if float(np.linalg.norm(np.array(centers)-candidate,axis=1).min())>threshold:
    new_id=f'NICHE-{len(ids)+1:04d}';ids.append(new_id);centers.append(candidate);anchors.append(candidate.copy());counts.append(len(matching));action='new_niche_created'
    events.append({'date':date,'action':action,'id':new_id,'support':len(matching),'center':candidate.tolist(),'nearest_prior_distance':float(np.linalg.norm(np.array(centers[:-1])-candidate,axis=1).min())})
    novel=[(ix,w) for ix,w in novel if np.linalg.norm(w-candidate)>radius]
 else:
  # Preserve source anchors while allowing limited incremental adaptation.
  rate=.02;centers[j]=.85*((1-rate)*centers[j]+rate*v)+.15*anchors[j];counts[j]+=1
 log.append({'date':date,'ticker':'AMGN','assigned_id':ids[j] if action!='new_niche_created' else ids[-1],'distance_before_update':nearest,'action':action,'memory_size':len(ids)})
# Frozen holdout: memory cannot learn from these observations.
acn_hold=xa[split:];amgn_hold=xb[bcut:];base=seed.cluster_centers_;current=np.array(centers)
def score(x):
 d0=np.linalg.norm(x[:,None,:]-base[None,:,:],axis=2);d1=np.linalg.norm(x[:,None,:]-current[None,:,:],axis=2)
 return {'n':len(x),'distance_original':float(d0.min(axis=1).mean()),'distance_expanded':float(d1.min(axis=1).mean()),'original_niche_retention':float(np.mean(d0.argmin(axis=1)==d1.argmin(axis=1))),'new_niche_assignment_fraction':float(np.mean(d1.argmin(axis=1)>=6))}
report={'status':'EXPLORATORY_NOT_CERTIFIED','source':'ACN','target':'AMGN','initial_niches':6,'final_niches':len(ids),'new_niches':len(ids)-6,'promotion_events':events,'ACN_holdout':score(acn_hold),'AMGN_holdout':score(amgn_hold),'limitations':['Thresholds and support are provisional heuristics; no false-novelty calibration','New niche formation is geometric, not proven semantic discovery','ACN source training and AMGN target training are separate historical blocks, not synchronized across calendar dates','Existing features need independent PIT audit','Holdout predictions do not update memory']}
(O/'report.json').write_text(json.dumps(report,indent=2));pd.DataFrame(log).to_csv(O/'daily_memory_decisions.csv',index=False)
(O/'memory.json').write_text(json.dumps({'schema':'expandable-niche-memory-v1','features':F,'center':C.tolist(),'scale':S.tolist(),'niches':[{'id':ids[i],'center':centers[i].tolist(),'anchor':anchors[i].tolist(),'count':counts[i],'source':'ACN' if i<6 else 'AMGN'} for i in range(len(ids))],'events':events},indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='promotion_events'},indent=2));print('created_ids',[e['id'] for e in events])
