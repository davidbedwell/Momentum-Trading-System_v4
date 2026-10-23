"""Persistent ACN -> AMGN niche memory: stable IDs, online centroid updates, replay and holdout audits.
No return labels or profit criteria. Historical point-in-time feature provenance is not yet certified.
"""
import json,hashlib
from pathlib import Path
import numpy as np,pandas as pd
from sklearn.cluster import KMeans
R=Path('/opt/mts/ga5_redesign');O=R/'persistent_niche_memory_v1';O.mkdir(exist_ok=True)
F=['trend','momentum','volatility','breadth','relative_strength'];S=np.array([.06,.07,.015,.25,.06]);C=np.array([0,0,.015,.5,0]);K=6
z=pd.read_parquet(R/'exploratory79_ga4_enriched.parquet');z=z[z.ticker.isin(['ACN','AMGN'])].dropna(subset=F).copy();z['date']=pd.to_datetime(z.date)
a=z[z.ticker=='ACN'].sort_values('date').reset_index(drop=True);b=z[z.ticker=='AMGN'].sort_values('date').reset_index(drop=True)
xa=np.clip((a[F].to_numpy()-C)/S,-5,5);xb=np.clip((b[F].to_numpy()-C)/S,-5,5)
# Chronological teaching: ACN knowledge is frozen at the handoff date; AMGN is later introduced.
# No claim of contemporaneous 2005-era transfer from future ACN observations.
split=int(len(a)*.70);base=KMeans(n_clusters=K,random_state=37,n_init=10).fit(xa[:split]);centers=base.cluster_centers_.copy();original=centers.copy();counts=np.bincount(base.labels_,minlength=K).astype(int)
# ACN retention benchmark is strictly held out from ACN training.
acn_hold=xa[split:];ref=base.predict(acn_hold);ids=['NICHE-%04d'%(i+1) for i in range(K)]
# Baseline AMGN recognition and fixed holdout evaluation: train on first 70%, test final 30%.
bcut=int(len(b)*.70);target_train=xb[:bcut];target_hold=xb[bcut:]
original_target=base.predict(target_hold);baseline_dist=np.linalg.norm(target_hold[:,None,:]-original[None,:,:],axis=2).min(axis=1)
original_acn_dist=np.linalg.norm(acn_hold[:,None,:]-original[None,:,:],axis=2).min(axis=1)
# Bounded per-niche learning with ACN anchors; old niche identities cannot be reassigned.
anchors=original.copy();events=[];novel=[];threshold=2.75
for i,v in enumerate(target_train):
 distances=np.linalg.norm(centers-v,axis=1);j=int(np.argmin(distances));distance=float(distances[j]);date=str(b.at[i,'date'].date())
 if distance>threshold:novel.append({'date':date,'distance':distance,'nearest_niche':ids[j]})
 # Slow adaptation anchored to ACN; preserve historical definition, no re-clustering.
 rate=.02;candidate=(1-rate)*centers[j]+rate*v
 centers[j]=.85*candidate+.15*anchors[j]
 counts[j]+=1
 if i%63==0:events.append({'date':date,'target_observations':i+1,'novelty_candidates':len(novel),'centers':centers.tolist()})
new_acn=np.argmin(np.linalg.norm(acn_hold[:,None,:]-centers[None,:,:],axis=2),axis=1)
new_target=np.argmin(np.linalg.norm(target_hold[:,None,:]-centers[None,:,:],axis=2),axis=1)
new_acn_dist=np.linalg.norm(acn_hold[:,None,:]-centers[None,:,:],axis=2).min(axis=1)
new_target_dist=np.linalg.norm(target_hold[:,None,:]-centers[None,:,:],axis=2).min(axis=1)
# Distinct replay evidence: the original ACN centers are preserved as permanent anchors.
memory={'schema':'mts-niche-memory-v1','source':'ACN','target':'AMGN','features':F,'normalization_center':C.tolist(),'normalization_scale':S.tolist(),'niches':[{'id':ids[i],'original_center':original[i].tolist(),'current_center':centers[i].tolist(),'observations':int(counts[i]),'source_anchor_preserved':True} for i in range(K)],'novelty_candidates':novel,'updates':events,'handoff_date':str(a.at[split,'date'].date()),'training_scope':'ACN first 70% + AMGN first 70%; separate heldout tails; noncontemporaneous transfer diagnostic'}
(O/'memory.json').write_text(json.dumps(memory,indent=2))
report={'status':'EXPLORATORY_NOT_CERTIFIED','source_training':split,'source_holdout':len(acn_hold),'target_training':bcut,'target_holdout':len(target_hold),'persistent_niches':K,'provisional_novelty_observations':len(novel),'ACN':{'assignment_retention':float(np.mean(ref==new_acn)),'distance_before':float(original_acn_dist.mean()),'distance_after':float(new_acn_dist.mean())},'AMGN':{'assignment_retention_vs_source':float(np.mean(original_target==new_target)),'distance_before':float(baseline_dist.mean()),'distance_after':float(new_target_dist.mean())},'limitations':['Historical handoff uses full early ACN history, so target evaluation is a transfer demonstration, not a calendar-synchronous simulation','Source feature point-in-time audit pending','Centroid distances are representation metrics, not independent semantic correctness','Novelty observations are candidates, not validated new niches','Anchoring preserves old niche IDs but may constrain adaptation']}
(O/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
