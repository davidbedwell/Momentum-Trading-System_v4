import numpy as np
import pandas as pd
from study import build
idx=pd.bdate_range('2000-01-01',periods=300)
x=pd.DataFrame(np.tile(np.arange(1.,301)[:,None],(1,25)),index=idx)
f=build(x,idx)
assert f.b200.iloc[200]==1 and pd.isna(f.b200.iloc[199])
assert f.feature_date.iloc[250]==idx[249]
y=x.copy();y.iloc[250:]=100000
pd.testing.assert_frame_equal(f.iloc[:251],build(y,idx).iloc[:251])
x.iloc[220,0]=np.nan
q=build(x,idx)
assert q.n10.iloc[221]==24
for m in [10,20,50,100,200]:
 for h in [5,10,21]:
  np.testing.assert_allclose(f[f'v{m}_{h}'],f[f'd{m}_{h}']/h,equal_nan=True)
print('PASS: prior-close timing, no future leakage, missing eligibility, velocity identity')
from study import fit
rng=np.random.default_rng(71)
g=pd.DataFrame({'entry_date':pd.bdate_range('2010-01-01',periods=600),'chromosome_id':np.tile(['A','B'],300)})
g['year']=g.entry_date.dt.year;g['x']=rng.normal(size=len(g));g['y']=.3*g.x+g.year*2+g.chromosome_id.eq('A')*4
r=fit(g,'x','y')
assert np.isclose(r['effect'],.3*r['within_sd'])
print('PASS: chromosome-year fixed effects recover known continuous slope')
