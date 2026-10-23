"""Transfer ACN-trained niche vocabulary to AMGN, then incrementally teach it AMGN.
Historical simulation with explicit chronology: ACN knowledge at date t uses ACN data strictly before t.
No future outcomes or profitability enter learning.
"""
import json
from pathlib import Path
import numpy as np,pandas as pd
from sklearn.cluster import MiniBatchKMeans
from scipy.optimize import linear_sum_assignment
ROOT=Path('/opt/mts/ga5_redesign');OUT=ROOT/'acn_to_amgn_transfer_v1';OUT.mkdir(exist_ok=True)
F=['trend','momentum','volatility','breadth','relative_strength'];S=np.array([.06,.07,.015,.25,.06]);C=np.array([0,0,.015,.5,0]);K=6
raw=pd.read_parquet(ROOT/'exploratory79_ga4_enriched.parquet');raw=raw[raw.ticker.isin(['ACN','AMGN'])].dropna(subset=F).copy();raw['date']=pd.to_datetime(raw.date)
a=raw[raw.ticker=='ACN'].sort_values('date').reset_index(drop=True);b=raw[raw.ticker=='AMGN'].sort_values('date').reset_index(drop=True)
xa=np.clip((a[F].to_numpy()-C)/S,-5,5);xb=np.clip((b[F].to_numpy()-C)/S,-5,5)
# Historical knowledge transfers at same calendar date, never from ACN's future.
# Compare fixed ACN-only vocabulary against online ACN+AMGN adaptation.
rows=[];updates=[];last_base=None;last_adapt=None;previous_centers=None
for i in range(500,len(b),63):
 date=b.at[i,'date'];ai=int(a.date.searchsorted(date,side='left'))
 if ai<500:continue
 base=MiniBatchKMeans(n_clusters=K,random_state=37,n_init=5,batch_size=256,max_iter=100).fit(xa[:ai]);adapt=MiniBatchKMeans(n_clusters=K,random_state=37,n_init=5,batch_size=256,max_iter=100).fit(np.vstack([xa[:ai],xb[:i]]))
 # Align adapted vocabulary to ACN vocabulary by center-distance assignment.
 cost=np.linalg.norm(base.cluster_centers_[:,None,:]-adapt.cluster_centers_[None,:,:],axis=2)
 rr,cc=linear_sum_assignment(cost);mapping={int(c):int(r) for r,c in zip(rr,cc)}
 end=min(i+63,len(b));pb=base.predict(xb[i:end]);pa=adapt.predict(xb[i:end]);pal=np.array([mapping[int(v)] for v in pa]);agreement=float(np.mean(pb==pal))
 for j in range(i,end):
  db=np.linalg.norm(base.cluster_centers_-xb[j],axis=1);da=np.linalg.norm(adapt.cluster_centers_-xb[j],axis=1)
  rows.append({'date':str(b.at[j,'date'].date()),'ticker':'AMGN','acn_training_rows_prior_date':ai,'amgn_training_rows_prior_date':i,'acn_only_niche':int(pb[j-i]),'adapted_niche_aligned':int(pal[j-i]),'same_assignment':bool(pb[j-i]==pal[j-i]),'acn_only_distance':float(db.min()),'adapted_distance':float(da.min()),'trend':float(b.at[j,'trend']),'momentum':float(b.at[j,'momentum']),'volatility':float(b.at[j,'volatility']),'breadth':float(b.at[j,'breadth']),'relative_strength':float(b.at[j,'relative_strength'])})
 updates.append({'date':str(date.date()),'acn_prior_rows':ai,'amgn_prior_rows':i,'block_assignment_agreement':agreement,'center_matching_mean_distance':float(cost[rr,cc].mean())})
log=pd.DataFrame(rows);log.to_csv(OUT/'daily_transfer_predictions.csv',index=False);pd.DataFrame(updates).to_csv(OUT/'learning_updates.csv',index=False)
report={'status':'EXPLORATORY_TRANSFER_NOT_CERTIFIED','source':'ACN','target':'AMGN','features':F,'niches':K,'predictions':len(log),'updates':len(updates),'acn_only_mean_distance':float(log.acn_only_distance.mean()),'adapted_mean_distance':float(log.adapted_distance.mean()),'distance_improvement_fraction':float((log.acn_only_distance-log.adapted_distance).mean()/log.acn_only_distance.mean()),'assignment_agreement':float(log.same_assignment.mean()),'limitations':['Adaptation refits with past AMGN observations; it does not validate stable semantic niche labels','Distance reduction can result mechanically from fitting target data, not proof of useful learning','Both models are fitted using ACN data prior to the target calendar date, avoiding cross-stock future leakage','Source and target feature provenance still requires independent point-in-time audit','No profits or future returns used']}
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
