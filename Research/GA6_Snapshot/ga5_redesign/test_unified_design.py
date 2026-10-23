import random
import pandas as pd
from ga5_redesign.unified_evolution import cross_any,breed
from ga5_redesign.niche_seeds import initial
from ga5_redesign.market_state import compute,DIMENSIONS

def test_cross_population_breeding():
 a,b=initial('growth'),initial('crash')
 children=breed([a,b],random.Random(4),50)
 assert all(g.valid() for g in children)
 assert all(g.niche in {'growth','crash'} for g in children)
 assert cross_any(a,b,random.Random(1)).valid()

def test_market_state_is_causal():
 dates=pd.date_range('2020-01-01',periods=230,freq='B')
 rows=[{'date':str(date.date()),'ticker':ticker,'close':100+i*(1 if ticker=='A' else .5),'volume':1000+i*2} for i,date in enumerate(dates) for ticker in ('A','B')]
 frame=pd.DataFrame(rows)
 first=compute(frame)
 changed=frame.copy()
 changed.loc[changed.date==str(dates[-1].date()),'close']=100000.
 changed.loc[changed.date==str(dates[-1].date()),'volume']=999999
 second=compute(changed)
 cols=[x for group in DIMENSIONS.values() for x in group]
 pd.testing.assert_frame_equal(first.iloc[:-1][cols],second.iloc[:-1][cols])
 assert 'relative_market_volume_20' in cols
 assert first.iloc[-1][cols].notna().all()
