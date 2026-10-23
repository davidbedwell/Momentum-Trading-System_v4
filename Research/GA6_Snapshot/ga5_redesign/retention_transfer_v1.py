"""Retention/transfer diagnostic with frozen source vocabulary and target adaptation.
All model fits use observations strictly before evaluation dates. No future labels.
"""
import json
from pathlib import Path
import numpy as np,pandas as pd
from sklearn.cluster import KMeans
from scipy.optimize import linear_sum_assignment
R=Path('/opt/mts/ga5_redesign');O=R/'retention_transfer_v1';O.mkdir(exist_ok=True)
F=['trend','momentum','volatility','breadth','relative_strength'];S=np.array([.06,.07,.015,.25,.06]);C=np.array([0,0,.015,.5,0]);K=6
z=pd.read_parquet(R/'exploratory79_ga4_enriched.parquet');z=z[z.ticker.isin(['ACN','AMGN'])].dropna(subset=F).copy();z['date']=pd.to_datetime(z.date)
a=z[z.ticker=='ACN'].sort_values('date').reset_index(drop=True);b=z[z.ticker=='AMGN'].sort_values('date').reset_index(drop=True)
xa=np.clip((a[F].to_numpy()-C)/S,-5,5);xb=np.clip((b[F].to_numpy()-C)/S,-5,5)
# Each evaluation block: train before block, score next 63 days on BOTH stocks.
rows=[]
for bi in range(500,len(b)-63,126):
 date=b.at[bi,'date'];ai=int(a.date.searchsorted(date,'left'));ae=int(a.date.searchsorted(b.at[min(bi+63,len(b)-1),'date'],'left'))
 if ai<500 or ae<=ai:continue
 base=KMeans(n_clusters=K,random_state=37,n_init=5).fit(xa[:ai]);adapt=KMeans(n_clusters=K,random_state=37,n_init=5).fit(np.vstack([xa[:ai],xb[:bi]]))
 dist=np.linalg.norm(base.cluster_centers_[:,None,:]-adapt.cluster_centers_[None,:,:],axis=2);rr,cc=linear_sum_assignment(dist);mapping={int(c):int(r) for r,c in zip(rr,cc)}
 for name,hold in [('ACN',xa[ai:ae]),('AMGN',xb[bi:min(bi+63,len(b))])]:
  if not len(hold):continue
  p=base.predict(hold);q=np.array([mapping[int(t)] for t in adapt.predict(hold)])
  bd=np.linalg.norm(hold[:,None,:]-base.cluster_centers_[None,:,:],axis=2).min(axis=1)
  ad=np.linalg.norm(hold[:,None,:]-adapt.cluster_centers_[None,:,:],axis=2).min(axis=1)
  rows.append({'date':str(date.date()),'stock':name,'n':len(hold),'source_distance':float(bd.mean()),'adapted_distance':float(ad.mean()),'distance_change':float(ad.mean()-bd.mean()),'assignment_retention':float((p==q).mean()),'source_training_rows':ai,'target_training_rows':bi})
log=pd.DataFrame(rows);log.to_csv(O/'holdout_block_metrics.csv',index=False)
summary={}
for name,g in log.groupby('stock'):
 summary[name]={'blocks':len(g),'evaluated_sessions':int(g.n.sum()),'source_distance':float(np.average(g.source_distance,weights=g.n)),'adapted_distance':float(np.average(g.adapted_distance,weights=g.n)),'relative_distance_change':float(np.average(g.distance_change,weights=g.n)/np.average(g.source_distance,weights=g.n)),'assignment_retention':float(np.average(g.assignment_retention,weights=g.n)),'blocks_improved':int((g.distance_change<0).sum())}
report={'status':'DIAGNOSTIC_NOT_CERTIFIED','description':'Chronological frozen-ACN-only versus ACN+past-AMGN model, next-block evaluation on ACN and AMGN','summary':summary,'interpretation_limits':['ACN retention is measured as agreement and geometric representation change, not semantic understanding','Adaptation changes niche centers and matching can be unstable','No baseline for random feature clustering yet','Feature provenance PIT audit pending','No future returns used']}
(O/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
