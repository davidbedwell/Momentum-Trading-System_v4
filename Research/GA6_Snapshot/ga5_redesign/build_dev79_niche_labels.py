"""Frozen 13-center research labels, not independently PIT certified."""
import json,hashlib
from pathlib import Path
import numpy as np,pandas as pd
R=Path(__file__).parent;O=R/'dev79_niche_ga_v1';O.mkdir(exist_ok=True)
b=json.loads((R/'chronological_memory_corrected_v2/memory.json').read_text());c=json.loads((R/'stocks31_40_corrected_v2/checkpoint.json').read_text());F=b['features'];centers=np.asarray(c['centers']);assert centers.shape==(13,len(F))
p=pd.read_parquet(R/'exploratory79_ga4_enriched.parquet');assert p.ticker.nunique()==79
out=[]
for t,g in p.groupby('ticker'):
 g=g.sort_values('date').copy();v=g.adj_close;d=v.diff();flip=((np.sign(d)*np.sign(d.shift(1)))<0).astype(float)
 for w in (10,20,40):
  net=(v-v.shift(w)).abs();g[f'efficiency_{w}']=(net/d.abs().rolling(w).sum()).clip(0,1);g[f'reversal_rate_{w}']=flip.rolling(w).mean();g[f'net_to_volatility_{w}']=net/(d.abs().rolling(w).std()*np.sqrt(w))
 ratio=v/g.close;g['range_width_20']=((g.high*ratio).rolling(20).max()-(g.low*ratio).rolling(20).min())/v
 g=g.replace([np.inf,-np.inf],np.nan);valid=g[F].notna().all(axis=1);x=np.clip((g.loc[valid,F].to_numpy(float)-b['median'])/b['scale'],-5,5);dist=np.linalg.norm(x[:,None,:]-centers[None,:,:],axis=2);labels=np.argmin(dist,axis=1)
 z=g.loc[valid,['date','ticker']].copy();z['research_niche']=[c['ids'][i] for i in labels];z['niche_distance']=dist[np.arange(len(labels)),labels];out.append(z)
labels=pd.concat(out).sort_values(['date','ticker']);labels.to_parquet(O/'labels.parquet',index=False);counts=labels.groupby('research_niche').agg(rows=('ticker','size'),stocks=('ticker','nunique')).reset_index().to_dict('records');report={'status':'RESEARCH_ONLY','universe':'DEV79','niches':13,'labeled_rows':len(labels),'niche_counts':counts,'limitations':['Retrospectively adapted 13-center library; research-only','PIT feature provenance unverified','No forward evaluation or profitability inference']};(O/'label_report.json').write_text(json.dumps(report,indent=2));print(json.dumps({'labeled_rows':len(labels),'counts':counts}),flush=True)
