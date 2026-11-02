from pathlib import Path
import numpy as np
import pandas as pd
p=Path(__file__).resolve().parent
x=pd.read_csv(p/'stock_month_features.csv',parse_dates=['execution_date','feature_date','exit_date']);s=pd.read_csv(p/'single_commonality.csv');f=pd.read_csv(p/'characteristic_flags.csv')
assert x.execution_date.dt.year.between(2009,2018).all()
assert x.feature_date.lt(x.execution_date).all()
assert x.exit_date.dropna().dt.year.le(2018).all()
assert x.execution_date.nunique()==120
assert x[x.execution_date.dt.to_period('M').eq(pd.Period('2018-12'))].winner.isna().all()
assert not x.duplicated(['execution_date','ticker']).any()
assert np.allclose(x['return'],x.exit_open/x.entry_open-1,equal_nan=True)
for date,g in x[x.winner.notna()].groupby('execution_date'):
 ordered=g.sort_values(['return','ticker'],ascending=[False,True]);k=int(np.ceil(len(g)/4));assert ordered.winner.iloc[:k].eq(1).all();assert ordered.winner.iloc[k:].eq(0).all()
for row in s[s.scope.eq('pooled')].itertuples():
 z=f[row.characteristic];known=z.notna()&x.winner.notna();yes=z.eq(True);w=x.winner.eq(1)
 assert row.winner_numerator==int((known&yes&w).sum())
 assert row.nonwinner_numerator==int((known&yes&~w).sum())
 assert row.winner_denominator==int((known&w).sum())
 assert row.nonwinner_denominator==int((known&~w).sum())
 for prefix in ['winner','nonwinner']:
  a=getattr(row,prefix+'_numerator');n=getattr(row,prefix+'_denominator');v=getattr(row,prefix+'_prevalence');assert np.isclose(v,a/n)
  assert getattr(row,prefix+'_ci95_low')<=v+1e-12<=getattr(row,prefix+'_ci95_high')+1e-12
co=pd.read_csv(p/'cooccurrence_pooled.csv');assert co.winner_numerator.ge(20).all() and co.nonwinner_numerator.ge(20).all()
for row in co.itertuples():
 z=f[row.characteristic.split(' & ')];known=z.notna().all(axis=1)&x.winner.notna();yes=z.fillna(False).astype(bool).all(axis=1);w=x.winner.eq(1)
 assert row.winner_numerator==int((known&yes&w).sum())
 assert row.nonwinner_numerator==int((known&yes&~w).sum())
print('PASS: boundary, prior-close alignment, monthly ranks/ties, returns, all pooled single and combination counts, prevalence and intervals')
