import json
from pathlib import Path
import numpy as np,pandas as pd
R=Path('/opt/mts/ga5_redesign');O=R/'precert_niche_distinction_v1';O.mkdir(exist_ok=True)
m=json.load(open(R/'chronological_memory_validation_v1/memory.json'));old=json.load(open(R/'iterative_20_memory_v1/checkpoint.json'));tickers=old['accepted']+['ARE','ATO','BEN','BG','BLDR','BNY','CBOE','CDNS','CDW','CFG'];F=m['features'];p=pd.read_parquet(R/'exploratory79_ga4_enriched.parquet');p=p[p.ticker.isin(tickers)].copy();p['date']=pd.to_datetime(p.date);parts=[]
for t,g in p.groupby('ticker'):
 g=g.sort_values('date').copy();c=g.adj_close.astype(float);delta=c.diff();flip=((np.sign(delta)*np.sign(delta.shift(1)))<0).astype(float)
 for w in (10,20,40):
  net=(c-c.shift(w)).abs();g[f'efficiency_{w}']=(net/delta.abs().rolling(w).sum().replace(0,np.nan)).clip(0,1);g[f'reversal_rate_{w}']=flip.rolling(w).mean();g[f'net_to_volatility_{w}']=net/(delta.abs().rolling(w).std()*np.sqrt(w)).replace(0,np.nan)
 ratio=g.adj_close/g.close.replace(0,np.nan);g['range_width_20']=((g.high*ratio).rolling(20).max()-(g.low*ratio).rolling(20).min())/c.replace(0,np.nan);g['volume_variability_20']=g.volume.rolling(20).std()/g.volume.rolling(20).mean().replace(0,np.nan);parts.append(g)
p=pd.concat(parts).replace([np.inf,-np.inf],np.nan).dropna(subset=F);p=p[p.date>='2023-01-01'].sort_values(['date','ticker']).reset_index(drop=True);cent=np.array(m['centers']);x=np.clip((p[F].to_numpy()-np.array(m['median']))/np.array(m['scale']),-5,5);d=np.linalg.norm(x[:,None,:]-cent[None,:,:],axis=2);a=d.argmin(axis=1);p['niche']=a;p['year']=p.date.dt.year;counts=np.bincount(a,minlength=len(cent));pairs=[]
for i in range(len(cent)):
 for j in range(i+1,len(cent)):
  distance=float(np.linalg.norm(cent[i]-cent[j]));ni=counts[i];nj=counts[j];
  if ni<30 or nj<30:continue
  # Subtle differences: per-niche distribution on key behavioral metrics, years and stocks.
  xi=p[p.niche==i];xj=p[p.niche==j];features={}
  for f in ['efficiency_20','reversal_rate_20','volatility','momentum','trend','breadth','relative_strength','volume_variability_20']:
   v1=xi[f].to_numpy(float);v2=xj[f].to_numpy(float);spread=float(np.sqrt((np.var(v1)+np.var(v2))/2));features[f]={'mean_i':float(v1.mean()),'mean_j':float(v2.mean()),'standardized_difference':float((v1.mean()-v2.mean())/max(spread,1e-8))}
  years={str(y):{'i':int((xi.year==y).sum()),'j':int((xj.year==y).sum())} for y in sorted(p.year.unique())};stocks_i=set(xi.ticker);stocks_j=set(xj.ticker);top=sorted(features.items(),key=lambda z:abs(z[1]['standardized_difference']),reverse=True)[:4]
  # Merging changes assignment labels, but does it conceal meaningful observed profile differences?
  distinct=any(abs(v['standardized_difference'])>=.5 for v in features.values());pairs.append({'i':m['ids'][i],'j':m['ids'][j],'center_distance':distance,'holdout_n_i':int(ni),'holdout_n_j':int(nj),'top_distinctions':top,'all_distinctions':features,'stock_overlap_jaccard':len(stocks_i&stocks_j)/len(stocks_i|stocks_j),'year_support':years,'possible_behavioral_distinction':distinct,'recommendation':'PRESERVE_AND_TEST' if distinct else 'REVIEW_FOR_POSSIBLE_REDUNDANCY'})
pairs.sort(key=lambda v:v['center_distance']);report={'status':'PRECERT_DIAGNOSTIC_NOT_CERTIFIED','holdout_rows':len(p),'niches':len(cent),'holdout_niche_counts':dict(zip(m['ids'],map(int,counts))),'pairs_ranked_by_proximity':pairs,'closest_pair_reviews':pairs[:12],'criteria':'Preserve if any key behavior shows >=0.5 pooled SD difference; this is a screening threshold, not a significance test','limitations':['Shared holdout already consumed by prior acceptance testing','Point-in-time provenance of derived predictors not verified','Pair differences are descriptive; no multiplicity adjustment or bootstrap significance','Unobserved subtle distinctions may exist even for pairs flagged possible redundancy','No niche merged or deleted']};(O/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps({'rows':len(p),'niches':len(cent),'closest_pairs':[{'i':z['i'],'j':z['j'],'distance':round(z['center_distance'],3),'distinct':z['possible_behavioral_distinction'],'top':[(f,round(v['standardized_difference'],2)) for f,v in z['top_distinctions'][:2]]} for z in pairs[:10]]},indent=2))
