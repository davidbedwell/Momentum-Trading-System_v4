"""ACN only: expanding-history unsupervised niche discovery and forward-only stability audit.
No future returns used to form clusters. Results diagnostic, not certified.
"""
import json
from pathlib import Path
import numpy as np,pandas as pd
from sklearn.cluster import MiniBatchKMeans
from sklearn.metrics import adjusted_rand_score
SOURCE=Path('/opt/mts/ga5_redesign/exploratory79_ga4_enriched.parquet')
OUT=Path('/opt/mts/ga5_redesign/acn_niche_walkforward_v1');OUT.mkdir(exist_ok=True)
F=['trend','momentum','volatility','breadth','relative_strength']
d=pd.read_parquet(SOURCE);d=d[d.ticker=='ACN'].sort_values('date').copy().reset_index(drop=True)
d=d.dropna(subset=F).reset_index(drop=True)
# Fixed, documented transformations (no fitting on future observations).
S=np.array([.06,.07,.015,.25,.06]);C=np.array([0,0,.015,.5,0])
x=np.clip((d[F].to_numpy()-C)/S,-5,5)
start=500;interval=63;k=6;rows=[];snapshots=[];model=None
for i in range(start,len(d)):
 if model is None or (i-start)%interval==0:
  # Fit only on rows strictly prior to prediction date.
  model=MiniBatchKMeans(n_clusters=k,random_state=37,n_init=5,batch_size=256,max_iter=100).fit(x[:i]);snapshots.append({'date':str(d.at[i,'date'].date()),'training_rows':i,'centers':model.cluster_centers_.tolist()})
 distances=np.linalg.norm(model.cluster_centers_-x[i],axis=1)
 cluster=int(np.argmin(distances));ordered=np.sort(distances)
 # Confidence is a distance margin, not a calibrated probability.
 margin=float((ordered[1]-ordered[0])/(ordered[1]+1e-9))
 rows.append({'date':str(d.at[i,'date'].date()),'ticker':'ACN','niche_id_at_fit':cluster,'model_version':len(snapshots),'training_rows':i,'nearest_distance':float(ordered[0]),'distance_margin':margin,'trend':float(d.at[i,'trend']),'momentum':float(d.at[i,'momentum']),'volatility':float(d.at[i,'volatility']),'breadth':float(d.at[i,'breadth']),'relative_strength':float(d.at[i,'relative_strength']),'forward_20d_return_audit_only':float(d.at[i+20,'adj_close']/d.at[i,'adj_close']-1) if i+20<len(d) else None})
log=pd.DataFrame(rows);log.to_csv(OUT/'daily_niche_predictions.csv',index=False)
(OUT/'model_snapshots.json').write_text(json.dumps(snapshots))
# Cluster IDs are version-local: transitions across refits cannot be interpreted without alignment.
within=log[log.model_version.eq(log.model_version.shift())]
consistency=float((within.niche_id_at_fit==log.niche_id_at_fit.shift().loc[within.index]).mean())
report={'status':'EXPLORATORY_NOT_CERTIFIED','stock':'ACN','dates':[str(d.date.min().date()),str(d.date.max().date())],'features':F,'clusters':k,'warmup_rows':start,'refit_interval_sessions':interval,'predictions':len(log),'snapshots':len(snapshots),'within_version_day_to_day_persistence':consistency,'mean_distance_margin_not_probability':float(log.distance_margin.mean()),'niche_counts_by_version_local_id':{str(k):int(v) for k,v in log.niche_id_at_fit.value_counts().items()},'limitations':['Unsupervised clusters are not proof of economically meaningful niches','Cluster identities may permute between refits; no cross-version transition claims','Features sourced from existing GA5 data; independent point-in-time audit pending','No supervised predictive accuracy or calibrated confidence claim','20-day forward return stored for retrospective audit only and never used in fitting']}
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
