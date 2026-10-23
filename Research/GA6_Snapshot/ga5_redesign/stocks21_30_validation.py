"""Sequential 21-30 transfer-first audit. No production memory mutation."""
import json,hashlib
from pathlib import Path
import numpy as np,pandas as pd
R=Path('/opt/mts/ga5_redesign');O=R/'stocks21_30_validation_v1';O.mkdir(exist_ok=True)
base_path=R/'chronological_memory_validation_v1/memory.json';base=base_path.read_bytes();baseline=json.loads(base);previous=json.loads((R/'iterative_20_memory_v1/checkpoint.json').read_text())['accepted'];new=['ARE','ATO','BEN','BG','BLDR','BNY','CBOE','CDNS','CDW','CFG'];F=baseline['features'];p=pd.read_parquet(R/'exploratory79_ga4_enriched.parquet');p=p[p.ticker.isin(previous+new)].copy();p['date']=pd.to_datetime(p.date);pieces=[]
for ticker,g in p.groupby('ticker'):
 g=g.sort_values('date').copy();c=g.adj_close.astype(float);delta=c.diff();flips=((np.sign(delta)*np.sign(delta.shift(1)))<0).astype(float)
 for w in (10,20,40):
  net=(c-c.shift(w)).abs();g[f'efficiency_{w}']=(net/delta.abs().rolling(w).sum().replace(0,np.nan)).clip(0,1);g[f'reversal_rate_{w}']=flips.rolling(w).mean();g[f'net_to_volatility_{w}']=net/(delta.abs().rolling(w).std()*np.sqrt(w)).replace(0,np.nan)
 ratio=g.adj_close/g.close.replace(0,np.nan);g['range_width_20']=((g.high*ratio).rolling(20).max()-(g.low*ratio).rolling(20).min())/c.replace(0,np.nan);g['volume_variability_20']=g.volume.rolling(20).std()/g.volume.rolling(20).mean().replace(0,np.nan);pieces.append(g)
p=pd.concat(pieces).replace([np.inf,-np.inf],np.nan).dropna(subset=F).sort_values(['date','ticker']);mu=np.array(baseline['median']);scale=np.array(baseline['scale']);centers=np.array(baseline['centers']);ids=baseline['ids'].copy();counts=baseline['counts'].copy();accepted=previous.copy();log=[]
def tx(g):return np.clip((g[F].to_numpy(float)-mu)/scale,-5,5)
def score(t,cc):
 g=p[(p.ticker==t)&(p.date>='2023-01-01')];x=tx(g);d=np.linalg.norm(x[:,None,:]-cc[None,:,:],axis=2);return d.argmin(axis=1),float(d.min(axis=1).mean())
# No reuse of 2023+ outcomes in learning; all ten are tested against frozen baseline before adaptation.
for step,t in enumerate(new,21):
 before=centers.copy();old_ids=ids.copy();old_counts=counts.copy();pre={s:score(s,before) for s in accepted};first=score(t,before);train=p[(p.ticker==t)&(p.date<'2021-01-01')&(p.date>='2008-01-01')];novel=[];events=[];threshold=4.0
 # Adaptation only with stock-specific chronological pre-2021 data; prior-stock memory is frozen starting point.
 for dt,v in zip(train.date.to_numpy(),tx(train)):
  d=np.linalg.norm(centers-v,axis=1);j=int(d.argmin());distance=float(d[j]);
  if distance>threshold:
   novel.append((dt,v.copy()));novel=[(day,x) for day,x in novel if (dt-day)/np.timedelta64(1,'D')<=126];near=[(day,x) for day,x in novel if np.linalg.norm(x-v)<2.0]
   if len(near)>=12 and len({str(day) for day,x in near})>=8:
    c=np.mean([x for day,x in near],axis=0)
    if np.linalg.norm(centers-c,axis=1).min()>threshold:
     ids.append(f'NICHE-{len(ids)+1:04d}');centers=np.vstack([centers,c]);counts.append(len(near));events.append({'date':str(dt)[:10],'id':ids[-1],'support':len(near)});novel=[(day,x) for day,x in novel if np.linalg.norm(x-c)>2.0]
  else:
   centers[j]=.9995*centers[j]+.0005*v;counts[j]+=1
 reviews=[]
 for s in accepted:
  after=score(s,centers);a,b=pre[s];reviews.append({'stock':s,'retention':float(np.mean(a==after[0])),'distance_degradation_pct':float((after[1]/b-1)*100)})
 worst=min(x['retention'] for x in reviews);maxbad=max(x['distance_degradation_pct'] for x in reviews);novelty=first[1];pass_gate=worst>=.80 and maxbad<=5
 if pass_gate:accepted.append(t)
 else:centers=before;ids=old_ids;counts=old_counts
 entry={'step':step,'stock':t,'accepted':pass_gate,'prelearning_holdout_distance':novelty,'candidate_promotions':events,'committed_promotions':len(events) if pass_gate else 0,'worst_retention':worst,'max_distance_degradation_pct':maxbad,'review':reviews,'learning_rows':len(train),'niches':len(ids)};log.append(entry);(O/f'step_{step}_{t}.json').write_text(json.dumps(entry,indent=2));(O/'checkpoint.json').write_text(json.dumps({'accepted':accepted,'ids':ids,'centers':centers.tolist(),'counts':counts,'source_sha256':hashlib.sha256(base).hexdigest()},indent=2));print(json.dumps({k:entry[k] for k in ['step','stock','accepted','committed_promotions','worst_retention','max_distance_degradation_pct','niches']}),flush=True)
report={'status':'EXPLORATORY_NOT_CERTIFIED','baseline_sha256':hashlib.sha256(base).hexdigest(),'new_stocks':new,'accepted_new':[t for t in new if t in accepted],'rejected_new':[t for t in new if t not in accepted],'initial_niches':len(baseline['ids']),'final_niches':len(ids),'steps':log,'limitations':['No verification of all 10 tickers against frozen stock-partition source; exploratory79 dataset not certified','Pre-2021 replay starts from frozen memory already learned from pre-2021 observations, so this is incremental stock adaptation, not an independent 30-stock single-pass chronology','Feature PIT provenance unresolved','Novelty threshold 4.0 is heuristic','No holdout outcome is used to train, but acceptance is based on holdout performance, so repeated checks consume holdout','Not certification evidence until independent final holdout']};(O/'report.json').write_text(json.dumps(report,indent=2));print('FINAL',json.dumps({'accepted':len(report['accepted_new']),'rejected':report['rejected_new'],'niches':len(ids)}),flush=True)
