"""Frozen low-cost GA5 predictive information audit, not GA optimization."""
import json
from pathlib import Path
import numpy as np,pandas as pd
from scipy.stats import spearmanr
root=Path('/opt/mts/ga5_redesign');out=root/'final_predictive_signal_audit_20261020';out.mkdir(exist_ok=True)
df=pd.read_parquet(root/'exploratory79_ga4_enriched.parquet')
df=df.sort_values(['ticker','date'])
labels=pd.read_parquet(root/'dev79_niche_ga_v1/labels.parquet')
labels['date']=labels.date.astype(str).str[:10]
df['date']=df.date.astype(str).str[:10]
df=df.merge(labels[['date','ticker','research_niche']],on=['date','ticker'],how='left',validate='one_to_one')
features=[c for c in df if c.startswith('ga4_') and not any(z in c for z in ('sma_20__','sma_50__','sma_200__','atr_14__','atr_20__','dollar_volume__'))]
for h in [5,20,63]:
 df['fwd_'+str(h)]=df.groupby('ticker',sort=False).close.shift(-h)/df.close-1
df=df[df.research_niche.notna()].copy()
df['year']=df.date.str[:4].astype(int)
# Separate periods; no selection using later data.
periods={'train':(2006,2016),'validation':(2017,2021),'test':(2022,2026)}
rows=[];summary=[]
for niche,g in df.groupby('research_niche'):
 for h in [5,20,63]:
  target='fwd_'+str(h)
  train=g[g.year.between(*periods['train'])].dropna(subset=[target])
  valid=g[g.year.between(*periods['validation'])].dropna(subset=[target])
  test=g[g.year.between(*periods['test'])].dropna(subset=[target])
  if min(len(train),len(valid),len(test))<60:continue
  candidates=[]
  for f in features:
   a=train[[f,target]].replace([np.inf,-np.inf],np.nan).dropna()
   if len(a)<100 or a[f].nunique()<10:continue
   qlo,qhi=a[f].quantile([.2,.8])
   if qhi<=qlo:continue
   hi=a[a[f]>=qhi][target];lo=a[a[f]<=qlo][target]
   if len(hi)<20 or len(lo)<20:continue
   edge=hi.mean()-lo.mean()
   candidates.append((abs(edge),f,edge,float(qlo),float(qhi)))
  for _,f,edge,qlo,qhi in sorted(candidates,reverse=True)[:3]:
   direction=1 if edge>0 else -1
   for period,part in [('train',train),('validation',valid),('test',test)]:
    a=part[[f,target]].replace([np.inf,-np.inf],np.nan).dropna()
    selected=a[a[f]>=qhi][target] if direction==1 else a[a[f]<=qlo][target]
    rejected=a[a[f]<=qlo][target] if direction==1 else a[a[f]>=qhi][target]
    rows.append(dict(niche=niche,horizon=h,feature=f,period=period,n=len(a),selected_n=len(selected),rejected_n=len(rejected),selected_mean=float(selected.mean()) if len(selected) else None,baseline_mean=float(a[target].mean()),opposite_mean=float(rejected.mean()) if len(rejected) else None,edge_vs_baseline=float(selected.mean()-a[target].mean()) if len(selected) else None,train_direction=direction))
  print('DONE',niche,h,'train',len(train),'valid',len(valid),'test',len(test),flush=True)
res=pd.DataFrame(rows)
res.to_csv(out/'all13_feature_train_validation_test.csv',index=False)
test=res[res.period=='test'].copy()
val=res[res.period=='validation'].copy()
merged=test.merge(val[['niche','horizon','feature','edge_vs_baseline']],on=['niche','horizon','feature'],suffixes=('_test','_validation'))
report={'status':'DIAGNOSTIC_NOT_CERTIFICATION','rows':len(df),'niches':int(df.research_niche.nunique()),'features_screened':len(features),'test_feature_horizon_pairs':len(test),'positive_test_edge_count':int((test.edge_vs_baseline>0).sum()),'positive_validation_and_test':int(((merged.edge_vs_baseline_test>0)&(merged.edge_vs_baseline_validation>0)).sum()),'limitations':'Full-sample niche labels may have retrospective leakage; returns overlap and are not independent; no transaction costs or executable portfolio; no multiplicity correction; test is diagnostic and must remain untouched in future tuning.'}
(out/'report.json').write_text(json.dumps(report,indent=2))
print('RESULT',json.dumps(report,indent=2),flush=True)
