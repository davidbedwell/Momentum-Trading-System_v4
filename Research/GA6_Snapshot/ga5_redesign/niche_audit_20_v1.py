import json
from pathlib import Path
import numpy as np,pandas as pd
R=Path('/opt/mts/ga5_redesign');O=R/'iterative_20_memory_v1';m=json.loads((O/'checkpoint.json').read_text());cols=m['features'];tickers=m['accepted'];p=pd.read_parquet(R/'exploratory79_ga4_enriched.parquet');p=p[p.ticker.isin(tickers)].copy();p['date']=pd.to_datetime(p.date)
parts=[]
for t,g in p.groupby('ticker'):
 g=g.sort_values('date').copy();c=g.adj_close.astype(float);delta=c.diff();sign=np.sign(delta);flip=((sign*sign.shift(1))<0).astype(float)
 for w in (10,20,40):
  net=(c-c.shift(w)).abs();g[f'efficiency_{w}']=(net/delta.abs().rolling(w).sum().replace(0,np.nan)).clip(0,1);g[f'reversal_rate_{w}']=flip.rolling(w).mean();g[f'net_to_volatility_{w}']=net/(delta.abs().rolling(w).std()*np.sqrt(w)).replace(0,np.nan)
 g['range_width_20']=(g.high.rolling(20).max()-g.low.rolling(20).min())/c.replace(0,np.nan);g['volume_variability_20']=g.volume.rolling(20).std()/g.volume.rolling(20).mean().replace(0,np.nan);parts.append(g)
p=pd.concat(parts).replace([np.inf,-np.inf],np.nan).dropna(subset=cols);p=p[p.date>='2023-01-01'].sort_values(['date','ticker']);x=np.clip((p[cols].to_numpy()-np.array(m['median']))/np.array(m['scale']),-5,5);cent=np.array(m['centers']);d=np.linalg.norm(x[:,None,:]-cent[None,:,:],axis=2);assignment=d.argmin(axis=1);p=p.assign(niche=assignment,distance=d.min(axis=1));out=[]
for j,nid in enumerate(m['ids']):
 z=p[p.niche==j]; per=z.groupby('ticker').size().sort_values(ascending=False);a={'id':nid,'observations':len(z),'stock_coverage':len(per),'top_stocks':per.head(5).to_dict(),'mean_distance':float(z.distance.mean()) if len(z) else None,'efficiency_20':float(z.efficiency_20.mean()) if len(z) else None,'reversal_rate_20':float(z.reversal_rate_20.mean()) if len(z) else None,'volume_variability_20':float(z.volume_variability_20.mean()) if len(z) else None,'trend':float(z.trend.mean()) if len(z) else None,'volatility':float(z.volatility.mean()) if len(z) else None};out.append(a)
# Raw center pair distances: flag likely duplicate candidates, not conclusive equivalence.
pairs=[]
for i in range(len(cent)):
 for j in range(i+1,len(cent)):
  pairs.append({'a':m['ids'][i],'b':m['ids'][j],'distance':float(np.linalg.norm(cent[i]-cent[j]))})
pairs.sort(key=lambda z:z['distance']);baseline={'efficiency_20':float(p.efficiency_20.mean()),'reversal_rate_20':float(p.reversal_rate_20.mean())};report={'status':'DIAGNOSTIC_NOT_CERTIFIED','holdout':'2023-01-01 through 2026-09-14','rows':len(p),'baseline':baseline,'niches':out,'nearest_pairs':pairs[:12],'caveats':['Final memory is trained using observations from all historical stocks including earlier 2023+? Training loop uses pre-2021 only; 2023+ is held out.','Stock-by-stock 2005-2020 replay is not single-pass chronological memory','2023+ assignments use final frozen memory and are descriptive, not causal no-trade evidence','Center distances in standardized high-dimensional feature space are not sufficient to establish unique niches','Range width mixes raw high/low with adjusted close; invalid when adjustment factors differ']};(O/'niche_semantics_audit.json').write_text(json.dumps(report,indent=2));print(json.dumps({'rows':len(p),'baseline':baseline,'niches':out,'nearest_pairs':pairs[:5]},indent=2))
