import pathlib,json
import pandas as pd,numpy as np
P=pathlib.Path('/opt/mts/ga6/runs/post_v3_comparison_20261022');D=pathlib.Path('/opt/mts/thunder-migration/mts-certification-20261011/dev87')
t=pd.read_csv(P/'dev87_trade_level_drawdown_features.csv');f=pd.read_parquet(D/'dev87_ga6_enriched.parquet');f['date']=pd.to_datetime(f.date);f=f.sort_values(['ticker','date']);f['decision_for_entry_date']=f.groupby('ticker').date.shift(-1)
cols=['ticker','decision_for_entry_date','trend','momentum','volatility','recursive','breadth','relative_strength']+[x for x in f if x.startswith('ga4_')]
x=f[cols].rename(columns={c:'decision_'+c for c in cols if c not in ['ticker','decision_for_entry_date']})
t['entry_date']=pd.to_datetime(t.entry_date);d=t.merge(x,left_on=['ticker','entry_date'],right_on=['ticker','decision_for_entry_date'],how='left',validate='many_to_one')
d['high_adverse']=d.mae<=-.10
records=[]
for c in [x for x in d if x.startswith('decision_') and x!='decision_for_entry_date']:
 a=d.loc[d.high_adverse,c].dropna();b=d.loc[~d.high_adverse,c].dropna()
 if len(a)<200 or len(b)<200:continue
 sd=np.sqrt((a.var()+b.var())/2)
 if not sd or not np.isfinite(sd):continue
 records.append({'feature':c,'high_adverse_n':len(a),'low_adverse_n':len(b),'high_adverse_median':a.median(),'low_adverse_median':b.median(),'standardized_difference':(a.mean()-b.mean())/sd})
r=pd.DataFrame(records).sort_values('standardized_difference',key=lambda s:s.abs(),ascending=False);r.to_csv(P/'dev87_prior_decision_entry_feature_differences.csv',index=False)
print('prior-decision matched rows',int(d.decision_trend.notna().sum()),'of',len(d));print(r.head(16).to_string(index=False))
