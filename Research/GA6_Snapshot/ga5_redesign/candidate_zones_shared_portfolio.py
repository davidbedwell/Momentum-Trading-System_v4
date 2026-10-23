import pandas as pd,numpy as np,json
from pathlib import Path
r=Path('/opt/mts/ga5_redesign');o=r/'final_predictive_signal_audit_20261020';a=pd.read_csv(o/'chronological_frozen12_nonoverlap.csv')
t=a[a.period=='test'].merge(a[a.period=='validation'],on=['niche','horizon','feature'],suffixes=('_test','_val'))
chosen=t[(t.edge_test>0)&(t.edge_val>0)&(t.net_20bps_test>0)&(t.net_20bps_val>0)].copy()
# Research diagnostic: retrospective selection from validation AND test; not a certified prospective portfolio.
p=pd.read_parquet(r/'exploratory79_ga4_enriched.parquet').sort_values(['ticker','date']);l=pd.read_parquet(r/'dev79_niche_ga_v1/labels.parquet');p.date=p.date.astype(str).str[:10];l.date=l.date.astype(str).str[:10];p=p.merge(l[['date','ticker','research_niche']],on=['date','ticker'],how='left');p['year']=p.date.str[:4].astype(int)
rows=[]
for z in chosen.itertuples():
 h=int(z.horizon);f=z.feature;n=z.niche
 train=p[(p.research_niche==n)&p.year.between(2006,2016)][f].replace([np.inf,-np.inf],np.nan).dropna()
 if len(train)<100:continue
 # Direction frozen by training edge: rank of selected value vs baseline reconstructed with training future close returns.
 g=p[p.research_niche==n].sort_values(['ticker','date']).copy();g['fwd']=g.groupby('ticker').close.shift(-h)/g.close-1
 tr=g[g.year.between(2006,2016)][[f,'fwd']].replace([np.inf,-np.inf],np.nan).dropna()
 lo,hi=tr[f].quantile([.2,.8]);up=tr[tr[f]>=hi].fwd.mean();dn=tr[tr[f]<=lo].fwd.mean();direction=1 if up>dn else -1;threshold=float(hi if direction==1 else lo)
 rows.append(dict(niche=n,horizon=h,feature=f,direction=direction,threshold=threshold))
if not rows:raise RuntimeError('No candidates')
pd.DataFrame(rows).to_csv(o/'candidate_zones_reconstructed.csv',index=False)
# Non-overlapping independent portfolio positions, one open per ticker, next-open execution; 10bps per side, 3-10% per position, daily cash reinvestment.
p=p.sort_values(['date','ticker']);p['next_open']=p.groupby('ticker').open.shift(-1);p['next_date']=p.groupby('ticker').date.shift(-1);p['next_adj_open']=p.next_open*(p.groupby('ticker').adj_close.shift(-1)/p.groupby('ticker').close.shift(-1));p['adj_open']=p.open*p.adj_close/p.close
signals=[]
for z in rows:
 q=p[(p.research_niche==z['niche'])&(p.year>=2022)].copy();f=z['feature'];q=q[q[f]>=z['threshold']] if z['direction']==1 else q[q[f]<=z['threshold']]
 for x in q.itertuples():
  if pd.isna(x.next_adj_open) or x.next_adj_open<=0:continue
  signals.append((x.date,x.ticker,z['horizon'],z['niche'],z['feature']))
sig=pd.DataFrame(signals,columns=['date','ticker','horizon','niche','feature']).drop_duplicates(['date','ticker']).sort_values(['date','ticker'])
sig.to_csv(o/'candidate_zone_signals_2022plus.csv',index=False)
print('CANDIDATES',len(rows),'SIGNALS',len(sig),flush=True)
