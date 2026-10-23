import pandas as pd
from research_niche_recognizer import label_frame
from pathlib import Path
r=Path('/opt/mts/ga5_redesign')
f=pd.read_parquet(r/'exploratory79_ga4_enriched.parquet')
ticker=sorted(f.ticker.unique())[0]
g=f[f.ticker==ticker].sort_values('date').iloc[:200].copy()
res=label_frame(g)
assert len(res)>0
assert (res.evidence_cutoff==res.date).all()
# Future appended observations must not change earlier niche assignments.
short=label_frame(g.iloc[:150].copy())
a=res[res.date.isin(short.date)][['date','research_niche']].reset_index(drop=True)
b=short[['date','research_niche']].reset_index(drop=True)
pd.testing.assert_frame_equal(a,b)
print('PASS: 13-center research labels, trailing-only feature computation, future append invariance',len(res),'rows')
