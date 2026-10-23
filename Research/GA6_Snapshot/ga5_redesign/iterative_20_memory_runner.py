"""20-stock incremental niche memory, per-stock review and rollback.
Research only. Globally time-synchronized updates; 2021-2023 train, 2024+ holdout.
"""
import json,hashlib,traceback
from pathlib import Path
import numpy as np,pandas as pd
from sklearn.cluster import MiniBatchKMeans
R=Path('/opt/mts/ga5_redesign');O=R/'iterative_20_memory_v1';O.mkdir(exist_ok=True)
T=['ACN','AMGN','JNJ','XOM','COST','INTC','HD','DIS','GILD','SO','FCX','NFLX','GE','CME','UPS','CRM','XEL','DECK','T','NUE']
F=['trend','momentum','volatility','breadth','relative_strength','ga4_relative_volume_20__v1','ga4_volume_slope_20__v1','efficiency_10','efficiency_20','efficiency_40','reversal_rate_10','reversal_rate_20','reversal_rate_40','net_to_volatility_10','net_to_volatility_20','net_to_volatility_40','range_width_20','volume_variability_20']
p=pd.read_parquet(R/'exploratory79_ga4_enriched.parquet');p=p[p.ticker.isin(T)].copy();p['date']=pd.to_datetime(p.date);pieces=[]
for ticker,g in p.groupby('ticker'):
 g=g.sort_values('date').copy();c=g.adj_close.astype(float);diff=c.diff();sg=np.sign(diff);flips=((sg*sg.shift(1))<0).astype(float)
 for w in [10,20,40]:
  net=(c-c.shift(w)).abs();travel=diff.abs().rolling(w,min_periods=w).sum();g[f'efficiency_{w}']=(net/travel.replace(0,np.nan)).clip(0,1)
  g[f'reversal_rate_{w}']=flips.rolling(w,min_periods=w).mean();g[f'net_to_volatility_{w}']=net/(diff.abs().rolling(w,min_periods=w).std()*np.sqrt(w)).replace(0,np.nan)
 g['range_width_20']=(g.high.rolling(20).max()-g.low.rolling(20).min())/c.replace(0,np.nan)
 g['volume_variability_20']=g.volume.rolling(20).std()/g.volume.rolling(20).mean().replace(0,np.nan);pieces.append(g)
p=pd.concat(pieces).replace([np.inf,-np.inf],np.nan).dropna(subset=F);p=p.sort_values(['date','ticker']).reset_index(drop=True)
# Restrict learning to fixed calendar span, not stock-relative historical slices.
train=p[(p.date>='2005-01-01')&(p.date<'2021-01-01')];cal=p[(p.date>='2021-01-01')&(p.date<'2023-01-01')];test=p[p.date>='2023-01-01']
source=train[train.ticker=='ACN'];mu=source[F].median().to_numpy();sc=(source[F].quantile(.75)-source[F].quantile(.25)).to_numpy();sc=np.maximum(sc,1e-5)
def transform(df):return np.clip((df[F].to_numpy(float)-mu)/sc,-5,5)
initial=MiniBatchKMeans(n_clusters=6,random_state=37,n_init=5,batch_size=256).fit(transform(source));centers=initial.cluster_centers_.copy();anchors=centers.copy();ids=[f'NICHE-{i+1:04d}' for i in range(6)];counts=np.bincount(initial.labels_,minlength=6).astype(int).tolist()
# ACN calibration controls initial tail novelty radius. No future test observations enter calibration.
cx=transform(cal[cal.ticker=='ACN']);cd=np.linalg.norm(cx[:,None,:]-centers[None,:,:],axis=2);ix=cd.argmin(axis=1);thresholds=[]
for j in range(6):
 v=cd[ix==j,j];thresholds.append(float(np.quantile(v if len(v)>=15 else cd.min(axis=1),.995)))
# Keep initial source center IDs. Repeated novelty is provisional; require cross-date and cross-window persistence.
rows=[];memory=[];accepted=[T[0]];candidate=[];state=centers.copy();base=centers.copy()
def holdout(stock,cc):
 x=transform(test[test.ticker==stock]);d=np.linalg.norm(x[:,None,:]-cc[None,:,:],axis=2);return {'n':len(x),'mean_distance':float(d.min(axis=1).mean()),'assignments':d.argmin(axis=1)}
for number,ticker in enumerate(T[1:],start=2):
 before=state.copy();before_ids=ids.copy();before_counts=counts.copy();x=transform(train[train.ticker==ticker]);dates=train[train.ticker==ticker].date.to_numpy();order=np.argsort(dates);x=x[order];dates=dates[order]
 # Globally chronological replay: each date includes ACN and all already accepted stocks; no future-date samples.
 replay=train[train.ticker.isin(accepted+[ticker])].sort_values(['date','ticker']);rx=transform(replay);rd=replay.date.to_numpy();rt=replay.ticker.to_numpy()
 provisional=[];created=[];updates=0
 for i,v in enumerate(rx):
  ds=np.linalg.norm(state-v,axis=1);j=int(ds.argmin());dist=float(ds[j]);threshold=thresholds[min(j,5)]
  if rt[i]==ticker and dist>threshold:
   provisional.append((rd[i],v.copy()))
   local=[w for dt,w in provisional if (rd[i]-dt)/np.timedelta64(1,'D')<=180 and np.linalg.norm(w-v)<max(1.,threshold*.5)]
   if len(local)>=8 and len({str(dt) for dt,w in provisional if np.linalg.norm(w-v)<max(1.,threshold*.5)})>=8:
    center=np.mean(local,axis=0)
    if np.linalg.norm(state-center,axis=1).min()>threshold:
     nid=f'NICHE-{len(ids)+1:04d}';ids.append(nid);state=np.vstack([state,center]);counts.append(len(local));created.append(nid);provisional=[(dt,w) for dt,w in provisional if np.linalg.norm(w-center)>max(1.,threshold*.5)]
  else:
   # Anchored update prevents erasure of previously learned source prototypes.
   rate=.003;state[j]=(1-rate)*state[j]+rate*v;state[j]=.999*state[j]+.001*anchors[min(j,len(anchors)-1)] if j<len(anchors) else state[j];counts[j]+=1;updates+=1
 # Compare each previously learned stock on its identical frozen holdout before vs after.
 audit=[]
 for old in accepted:
  b0=holdout(old,before);b1=holdout(old,state);agreement=float(np.mean(b0['assignments']==b1['assignments']));degrade=(b1['mean_distance']-b0['mean_distance'])/max(b0['mean_distance'],1e-9)
  audit.append({'stock':old,'retention':agreement,'distance_change_pct':float(degrade*100)})
 worst=min(a['retention'] for a in audit);max_degrade=max(a['distance_change_pct'] for a in audit)
 # Acceptance rule is predeclared and consistent across iterations.
 accept=worst>=.80 and max_degrade<=5.0
 if not accept:state=before;ids=before_ids;counts=before_counts
 else:accepted.append(ticker)
 entry={'step':number,'stock':ticker,'accepted':accept,'proposed_niches':created,'new_niches_committed':len(created) if accept else 0,'total_niches':len(ids),'worst_previous_stock_retention':worst,'max_previous_stock_distance_degradation_pct':max_degrade,'review':audit,'learning_rows':len(replay),'notes':'Rollback on rejection; no hyperparameter auto-tuning'}
 rows.append(entry);(O/f'step_{number:02d}_{ticker}.json').write_text(json.dumps(entry,indent=2));(O/'checkpoint.json').write_text(json.dumps({'completed':number,'accepted':accepted,'ids':ids,'centers':state.tolist(),'counts':counts,'features':F,'median':mu.tolist(),'scale':sc.tolist(),'thresholds':thresholds},indent=2));print(json.dumps({k:entry[k] for k in ['step','stock','accepted','new_niches_committed','total_niches','worst_previous_stock_retention','max_previous_stock_distance_degradation_pct']}),flush=True)
report={'status':'EXPLORATORY_UNCERTIFIED','requested_stocks':T,'accepted':accepted,'steps':rows,'final_niches':len(ids),'limitations':['Preexisting derived feature PIT provenance not audited','Fixed 6-source initial clusters and heuristic novelty/acceptance criteria','Repeated replay of earlier history, not a genuine single-pass streaming deployment','Calibration based on 2021-2022 ACN and holdout 2023 onward; 2005-2020 replay only','No external semantic validity or false discovery calibration','No profitability or trade decision assessment']}
(O/'report.json').write_text(json.dumps(report,indent=2));print('FINAL',json.dumps({'accepted':len(accepted),'total_niches':len(ids),'steps':len(rows)}),flush=True)
