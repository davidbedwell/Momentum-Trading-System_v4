"""Past-only market disorganization features. No future return labels and no trading decisions."""
import json
from pathlib import Path
import numpy as np,pandas as pd
R=Path('/opt/mts/ga5_redesign');O=R/'chop_features_v1';O.mkdir(exist_ok=True)
p=pd.read_parquet(R/'exploratory79_ga4_enriched.parquet');p=p[p.ticker.isin(['ACN','AMGN'])].sort_values(['ticker','date']).copy()
def features(g):
 c=g['adj_close'].astype(float);r=c.diff();direction=np.sign(r);absdiff=r.abs()
 for w in [10,20,40]:
  travel=absdiff.rolling(w,min_periods=w).sum();net=(c-c.shift(w)).abs();g[f'efficiency_{w}']=(net/travel.replace(0,np.nan)).clip(0,1)
  flips=((direction*direction.shift(1))<0).astype(float);g[f'reversal_rate_{w}']=flips.rolling(w,min_periods=w).mean()
  g[f'net_to_volatility_{w}']=net/(absdiff.rolling(w,min_periods=w).std()*np.sqrt(w)).replace(0,np.nan)
 g['range_width_20']=((g.high.rolling(20,min_periods=20).max()-g.low.rolling(20,min_periods=20).min())/c.replace(0,np.nan))
 g['volume_variability_20']=g.volume.rolling(20,min_periods=20).std()/g.volume.rolling(20,min_periods=20).mean().replace(0,np.nan)
 return g
p=pd.concat([features(g.copy()) for _,g in p.groupby('ticker')],ignore_index=True);f=[c for c in p.columns if c.startswith(('efficiency_','reversal_rate_','net_to_volatility_'))]+['range_width_20','volume_variability_20']
result=p[['ticker','date']+f].replace([np.inf,-np.inf],np.nan).dropna();result.to_parquet(O/'historical_disorganization_features.parquet',index=False)
report={'rows':len(result),'stocks':result.ticker.value_counts().to_dict(),'features':f,'interpretation':'Features measure historical path efficiency, reversals, range and volume variability; no niche classification or no-trade policy certified','cautions':['Inputs only through each observation date','Feature-source PIT audit remains pending','These features must be integrated and tested in the expandable memory before claiming learned disorganization niches']}
(O/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
