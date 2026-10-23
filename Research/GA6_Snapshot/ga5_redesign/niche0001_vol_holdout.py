import pandas as pd,numpy as np,json
from pathlib import Path
p=Path('/opt/mts/ga5_redesign/dev79_niche_origin_500x1000_20261019/niche0001_signal_study')
d=pd.read_parquet(p/'intratrade_time_t_samples.parquet')
d['year']=d.date.dt.year
train=d[d.year<=2016].copy();test=d[d.year>=2017].copy()
q=train.vol.quantile(.8)
rows=[]
for name,g in [('train',train),('holdout',test)]:
 for cohort,h in [('all',g)]+list(g.groupby('cohort')):
  high=h[h.vol>=q];other=h[h.vol<q]
  rows.append({'period':name,'cohort':cohort,'n':len(h),'high_vol_n':len(high),'high_vol_adverse_rate':float(high.future_adverse5.mean()) if len(high) else None,'other_adverse_rate':float(other.future_adverse5.mean()) if len(other) else None,'high_vol_mean_future_min':float(high.future_min5.mean()) if len(high) else None,'other_mean_future_min':float(other.future_min5.mean()) if len(other) else None,'threshold':float(q)})
pd.DataFrame(rows).to_csv(p/'volatility_chronological_split.csv',index=False)
print(pd.DataFrame(rows).to_string(index=False),flush=True)
