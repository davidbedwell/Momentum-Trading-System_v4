import pandas as pd,numpy as np,json
from pathlib import Path
r=Path('/opt/mts/ga5_redesign');o=r/'final_predictive_signal_audit_20261020';m=json.loads((r/'chronological_memory_corrected_v2/memory.json').read_text());p=pd.read_parquet(r/'exploratory79_ga4_enriched.parquet').sort_values(['ticker','date'])
parts=[]
for ticker,g in p.groupby('ticker'):
 g=g.copy();c=g.adj_close;d=c.diff();flip=((np.sign(d)*np.sign(d.shift(1)))<0).astype(float)
 for w in [10,20,40]:
  net=(c-c.shift(w)).abs();g['efficiency_'+str(w)]=(net/d.abs().rolling(w).sum()).clip(0,1);g['reversal_rate_'+str(w)]=flip.rolling(w).mean();g['net_to_volatility_'+str(w)]=net/(d.abs().rolling(w).std()*np.sqrt(w))
 ratio=g.adj_close/g.close;g['range_width_20']=((g.high*ratio).rolling(20).max()-(g.low*ratio).rolling(20).min())/c
 parts.append(g)
p=pd.concat(parts).sort_values(['ticker','date']);f=m['features'];x=p[f].replace([np.inf,-np.inf],np.nan).to_numpy(float);good=np.isfinite(x).all(axis=1);cent=np.asarray(m['centers']);z=np.clip((x[good]-np.asarray(m['median']))/np.asarray(m['scale']),-5,5);idx=np.linalg.norm(z[:,None,:]-cent[None,:,:],axis=2).argmin(axis=1);p['chronological_niche']=None;p.loc[good,'chronological_niche']=[m['ids'][i] for i in idx]
p.date=p.date.astype(str).str[:10];px=p.open*p.adj_close/p.close
for h in [5,20,63]:p['r'+str(h)]=px.groupby(p.ticker).shift(-(h+1))/px.groupby(p.ticker).shift(-1)-1
p['year']=p.date.str[:4].astype(int);features=[v for v in p if v.startswith('ga4_') and v not in f];results=[]
for niche in m['ids']:
 for h in [5,20,63]:
  train=p[(p.chronological_niche==niche)&p.year.between(2006,2016)].dropna(subset=['r'+str(h)]);v=p[(p.chronological_niche==niche)&p.year.between(2017,2021)];t=p[(p.chronological_niche==niche)&p.year.between(2022,2026)]
  if min(len(train),len(v),len(t))<80:continue
  scores=[]
  for f0 in features:
   a=train[[f0,'r'+str(h)]].replace([np.inf,-np.inf],np.nan).dropna()
   if len(a)<100 or a[f0].nunique()<10:continue
   lo,hi=a[f0].quantile([.2,.8]);upper=a[a[f0]>=hi]['r'+str(h)];lower=a[a[f0]<=lo]['r'+str(h)]
   if min(len(upper),len(lower))<20:continue
   edge=upper.mean()-lower.mean();scores.append((abs(edge),f0,1 if edge>0 else -1,float(hi if edge>0 else lo)))
  for _,f0,direction,threshold in sorted(scores,reverse=True)[:3]:
   for period,part in [('validation',v),('test',t)]:
    dates=np.sort(part.date.unique());part=part[part.date.isin(set(dates[::h]))];part=part[[f0,'r'+str(h)]].replace([np.inf,-np.inf],np.nan).dropna();sel=part[part[f0]>=threshold] if direction==1 else part[part[f0]<=threshold]
    if len(sel)<8:continue
    results.append(dict(niche=niche,horizon=h,feature=f0,period=period,selected=len(sel),edge=float(sel['r'+str(h)].mean()-part['r'+str(h)].mean()),net_20bps=float(sel['r'+str(h)].mean()-.002)))
 print('NICHE',niche,flush=True)
a=pd.DataFrame(results);a.to_csv(o/'chronological_frozen12_nonoverlap.csv',index=False);t=a[a.period=='test'];z=t.merge(a[a.period=='validation'],on=['niche','horizon','feature'],suffixes=('_test','_validation'));report={'frozen_niches':len(m['ids']),'test_combinations':len(t),'positive_test':int((t.edge>0).sum()),'positive_both':int(((z.edge_test>0)&(z.edge_validation>0)).sum()),'median_test_edge':float(t.edge.median()),'positive_absolute_net_20bps':int((t.net_20bps>0).sum()),'status':'CHRONOLOGICAL_FROZEN12_DIAGNOSTIC','limitations':['Pre-2021 fitted 12-center memory; training-period evaluation may not be independent of center formation','Niche 13 not pre-frozen, excluded rather than leaked','Feature PIT provenance remains unverified','Cross-stock dependence and multiple testing not controlled','No portfolio simulation']};(o/'chronological_frozen12_report.json').write_text(json.dumps(report,indent=2));print('RESULT',json.dumps(report,indent=2),flush=True)
