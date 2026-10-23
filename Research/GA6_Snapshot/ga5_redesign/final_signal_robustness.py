import pandas as pd,numpy as np,json
from pathlib import Path
r=Path('/opt/mts/ga5_redesign');o=r/'final_predictive_signal_audit_20261020'
a=pd.read_csv(o/'all13_feature_train_validation_test.csv');p=pd.read_parquet(r/'exploratory79_ga4_enriched.parquet');l=pd.read_parquet(r/'dev79_niche_ga_v1/labels.parquet')
p.date=p.date.astype(str).str[:10];l.date=l.date.astype(str).str[:10]
p=p.sort_values(['ticker','date']).merge(l[['date','ticker','research_niche']],on=['date','ticker'],how='left')
px=p.open*p.adj_close/p.close
for h in [5,20,63]:p['f'+str(h)]=px.groupby(p.ticker).shift(-(h+1))/px.groupby(p.ticker).shift(-1)-1
p['year']=p.date.str[:4].astype(int);results=[]
for (n,h,f),v in a[a.period=='train'].groupby(['niche','horizon','feature']):
 direction=int(v.iloc[0].train_direction);train=p[(p.research_niche==n)&p.year.between(2006,2016)][f].replace([np.inf,-np.inf],np.nan).dropna()
 if len(train)<100:continue
 threshold=train.quantile(.8 if direction==1 else .2)
 for period,lo,hi in [('validation',2017,2021),('test',2022,2026)]:
  q=p[(p.research_niche==n)&p.year.between(lo,hi)].copy();dates=np.sort(q.date.unique());q=q[q.date.isin(set(dates[::h]))]
  q=q[[f,'f'+str(h)]].replace([np.inf,-np.inf],np.nan).dropna()
  if len(q)<10:continue
  sel=q[q[f]>=threshold] if direction==1 else q[q[f]<=threshold]
  if len(sel)<8:continue
  results.append(dict(niche=n,horizon=h,feature=f,period=period,n=len(q),selected=len(sel),edge=float(sel['f'+str(h)].mean()-q['f'+str(h)].mean()),net_after_20bps=float(sel['f'+str(h)].mean()-.002)))
v=pd.DataFrame(results);v.to_csv(o/'nonoverlap_next_open.csv',index=False);t=v[v.period=='test'];x=t.merge(v[v.period=='validation'],on=['niche','horizon','feature'],suffixes=('_test','_validation'))
report={'test_combinations':len(t),'test_positive_edge':int((t.edge>0).sum()),'positive_both_periods':int(((x.edge_test>0)&(x.edge_validation>0)).sum()),'positive_net_after_20bps':int((t.net_after_20bps>0).sum()),'median_test_edge':float(t.edge.median()),'status':'DIAGNOSTIC_NOT_CERTIFIED','limitations':['Retrospectively fitted niche centers','Cross-stock correlated observations','20bps illustrative roundtrip cost','No multiple-comparison correction','No executable capital-constrained portfolio']}
(o/'nonoverlap_report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
