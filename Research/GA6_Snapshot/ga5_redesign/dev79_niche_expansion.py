"""DEV79 exploratory niche expansion; no trading evaluation."""
import json,random
from pathlib import Path
import numpy as np,pandas as pd
R=Path(__file__).parent;O=R/'dev79_niche_expansion_v1';O.mkdir(exist_ok=True)
b=json.loads((R/'chronological_memory_corrected_v2/memory.json').read_text());c=json.loads((R/'stocks31_40_corrected_v2/checkpoint.json').read_text());F=b['features'];p=pd.read_parquet(R/'exploratory79_ga4_enriched.parquet');assert p.ticker.nunique()==79 and len(c['ids'])==13
D={}
for t,g in p.groupby('ticker'):
 g=g.sort_values('date').copy();v=g.adj_close;d=v.diff();flip=((np.sign(d)*np.sign(d.shift(1)))<0).astype(float)
 for w in (10,20,40):
  net=(v-v.shift(w)).abs();g[f'efficiency_{w}']=(net/d.abs().rolling(w).sum()).clip(0,1);g[f'reversal_rate_{w}']=flip.rolling(w).mean();g[f'net_to_volatility_{w}']=net/(d.abs().rolling(w).std()*np.sqrt(w))
 ratio=v/g.close;g['range_width_20']=((g.high*ratio).rolling(20).max()-(g.low*ratio).rolling(20).min())/v
 g=g[(g.date>='2008-01-01')&(g.date<'2021-01-01')].replace([np.inf,-np.inf],np.nan).dropna(subset=F);D[t]=np.clip((g[F].to_numpy(float)-b['median'])/b['scale'],-5,5)
assert len(D)==79
runs=[]
for seed in (17,37,71):
 order=sorted(D);random.Random(seed).shuffle(order);centers=np.asarray(c['centers']).copy();ids=c['ids'].copy();counts=c['counts'].copy();curve=[];events=[]
 for n,t in enumerate(order,1):
  novel=[];promoted=0
  for k,v in enumerate(D[t]):
   ds=np.linalg.norm(centers-v,axis=1);j=int(ds.argmin())
   if ds[j]>4:
    novel.append((k,v));novel=[(ix,x) for ix,x in novel if k-ix<=90];near=[(ix,x) for ix,x in novel if np.linalg.norm(x-v)<2]
    if len(near)>=12 and len({ix for ix,x in near})>=8:
     candidate=np.mean([x for ix,x in near],axis=0)
     if np.linalg.norm(centers-candidate,axis=1).min()>4:
      ids.append(f'NICHE-{len(ids)+1:04d}');centers=np.vstack((centers,candidate));counts.append(len(near));promoted+=1;events.append({'step':n,'stock':t,'id':ids[-1]});novel=[(ix,x) for ix,x in novel if np.linalg.norm(x-candidate)>2]
   else:centers[j]=.9995*centers[j]+.0005*v;counts[j]+=1
  curve.append({'seed':seed,'stocks_seen':n,'stock':t,'new':promoted,'total':len(ids)})
  if n%10==0 or n==79:print('PROGRESS',seed,n,len(ids),flush=True)
 runs.append({'seed':seed,'curve':curve,'events':events,'ids':ids,'centers':centers.tolist(),'counts':counts})
pd.DataFrame([v for r in runs for v in r['curve']]).to_csv(O/'discovery_curves.csv',index=False)
(O/'candidate_memories.json').write_text(json.dumps([{k:r[k] for k in ('seed','ids','centers','counts')} for r in runs]))
report={'status':'EXPLORATORY_NOT_CERTIFIED','universe':'DEV79','starting_niches':13,'runs':[{'seed':r['seed'],'final_niches':len(r['ids']),'events':r['events']} for r in runs],'limitations':['PIT feature lineage unverified','13-niche initial memory retrospectively adapted','Stock-order learning is not global-calendar chronological','Random orders not sector-balanced','Novelty thresholds heuristic; proposed niches unvalidated','No blind data accessed']}
(O/'report.json').write_text(json.dumps(report,indent=2));print('FINAL',[(r['seed'],len(r['ids'])) for r in runs],flush=True)
