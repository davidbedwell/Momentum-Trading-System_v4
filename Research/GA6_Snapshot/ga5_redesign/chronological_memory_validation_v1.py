"""Single-pass global-date niche memory validation, research-only.
Strictly no held-out period learning. Raw high/low adjusted using same-day close adjustment factor.
"""
import json,hashlib
from pathlib import Path
import numpy as np,pandas as pd
from sklearn.cluster import MiniBatchKMeans
R=Path('/opt/mts/ga5_redesign');O=R/'chronological_memory_validation_v1';O.mkdir(exist_ok=True)
prior=json.loads((R/'iterative_20_memory_v1/checkpoint.json').read_text());T=prior['accepted'];F=prior['features'];p=pd.read_parquet(R/'exploratory79_ga4_enriched.parquet');p=p[p.ticker.isin(T)].copy();p['date']=pd.to_datetime(p.date);groups=[]
for t,g in p.groupby('ticker'):
 g=g.sort_values('date').copy();c=g.adj_close.astype(float);delta=c.diff();flip=((np.sign(delta)*np.sign(delta.shift(1)))<0).astype(float)
 for w in [10,20,40]:
  net=(c-c.shift(w)).abs();g[f'efficiency_{w}']=(net/delta.abs().rolling(w).sum().replace(0,np.nan)).clip(0,1);g[f'reversal_rate_{w}']=flip.rolling(w).mean();g[f'net_to_volatility_{w}']=net/(delta.abs().rolling(w).std()*np.sqrt(w)).replace(0,np.nan)
 ratio=g.adj_close/g.close.replace(0,np.nan);adjusted_high=g.high*ratio;adjusted_low=g.low*ratio
 g['range_width_20']=(adjusted_high.rolling(20).max()-adjusted_low.rolling(20).min())/c.replace(0,np.nan)
 g['volume_variability_20']=g.volume.rolling(20).std()/g.volume.rolling(20).mean().replace(0,np.nan);groups.append(g)
p=pd.concat(groups).replace([np.inf,-np.inf],np.nan).dropna(subset=F).sort_values(['date','ticker']).reset_index(drop=True)
train=p[p.date<'2021-01-01'];cal=p[(p.date>='2021-01-01')&(p.date<'2023-01-01')];test=p[p.date>='2023-01-01'];source=train[(train.ticker=='ACN')&(train.date<'2008-01-01')];mu=source[F].median().to_numpy();scale=np.maximum((source[F].quantile(.75)-source[F].quantile(.25)).to_numpy(),1e-5)
def tx(df):return np.clip((df[F].to_numpy(float)-mu)/scale,-5,5)
# Seed uses ACN observations through 2007 only, then learns each subsequent date exactly once.
seed=MiniBatchKMeans(n_clusters=6,random_state=37,n_init=5,batch_size=256).fit(tx(source));centers=seed.cluster_centers_.copy();counts=np.bincount(seed.labels_,minlength=6).astype(int).tolist();ids=[f'NICHE-{i+1:04d}' for i in range(6)];anchors=centers.copy();seed_x=tx(source);cd=np.linalg.norm(seed_x[:,None,:]-centers[None,:,:],axis=2);threshold=float(np.quantile(cd.min(axis=1),.995));novel=[];events=[];rejections=[]
# Global calendar clock: train observations 2008-2020, sorted date then ticker.
stream=train[train.date>='2008-01-01'].sort_values(['date','ticker']);sx=tx(stream);dates=stream.date.to_numpy();ticks=stream.ticker.to_numpy()
for k,v in enumerate(sx):
 ds=np.linalg.norm(centers-v,axis=1);j=int(ds.argmin());dist=float(ds[j]);day=dates[k]
 if dist>threshold:
  novel.append((day,v.copy(),ticks[k]));novel=[(dt,w,t) for dt,w,t in novel if (day-dt)/np.timedelta64(1,'D')<=126]
  local=[(dt,w,t) for dt,w,t in novel if np.linalg.norm(w-v)<max(1.,threshold*.5)]
  if len(local)>=10 and len({str(dt) for dt,w,t in local})>=5 and len({t for dt,w,t in local})>=2:
   c=np.mean([w for dt,w,t in local],axis=0)
   if np.linalg.norm(centers-c,axis=1).min()>threshold:
    ids.append(f'NICHE-{len(ids)+1:04d}');centers=np.vstack([centers,c]);counts.append(len(local));events.append({'date':str(day)[:10],'id':ids[-1],'source_stocks':sorted({t for dt,w,t in local}),'support':len(local)});novel=[(dt,w,t) for dt,w,t in novel if np.linalg.norm(w-c)>max(1.,threshold*.5)]
 else:
  rate=.001;centers[j]=(1-rate)*centers[j]+rate*v;counts[j]+=1
# Freeze learned memory and evaluate independent 2023+ without updating any centers.
xt=tx(test);d=np.linalg.norm(xt[:,None,:]-centers[None,:,:],axis=2);a=d.argmin(axis=1);test=test.assign(niche=a,distance=d.min(axis=1));profiles=[]
for j,nid in enumerate(ids):
 z=test[test.niche==j];profiles.append({'id':nid,'observations':len(z),'stocks':int(z.ticker.nunique()),'efficiency_20':float(z.efficiency_20.mean()) if len(z) else None,'reversal_rate_20':float(z.reversal_rate_20.mean()) if len(z) else None,'mean_distance':float(z.distance.mean()) if len(z) else None})
report={'status':'EXPLORATORY_NOT_CERTIFIED','learning_mode':'global_calendar_single_pass','seed_source':'ACN through 2007-12-31','training_end':'2020-12-31','calibration_window':'Initial novelty threshold calibrated on ACN pre-2008 seed only; 2021-2022 excluded from learning','holdout_start':'2023-01-01','stock_count':len(T),'train_rows':len(stream),'test_rows':len(test),'seed_niches':6,'final_niches':len(ids),'promotions':events,'profiles':profiles,'feature_fix':'Adjusted high and low by same-day adj_close/close ratio before computing 20-day range','limitations':['Initial novelty threshold estimated on in-sample seed; potentially optimistic','Source GA4 indicators PIT provenance not independently audited','Heuristic recurrence criteria, no false-discovery control','Original 20-stock checkpoint not directly comparable because chronology and feature definition changed','No trading outcome or no-trade inference']}
(O/'report.json').write_text(json.dumps(report,indent=2));(O/'memory.json').write_text(json.dumps({'ids':ids,'centers':centers.tolist(),'median':mu.tolist(),'scale':scale.tolist(),'features':F,'counts':counts},indent=2));print(json.dumps({'train_rows':len(stream),'test_rows':len(test),'niches':len(ids),'promotions':len(events),'profiles':profiles},indent=2),flush=True)
