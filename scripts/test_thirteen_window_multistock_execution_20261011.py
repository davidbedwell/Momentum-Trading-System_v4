import numpy as np,pandas as pd
from scripts.thirteen_window_multistock_execution_20261011 import simulate
cal=pd.bdate_range('2020-01-01',periods=100)
episodes={'one':{'peak':str(cal[10].date()),'trough':str(cal[20].date())}}
r1=np.zeros(100,dtype=bool);r1[34]=True
w=np.tile([.4,.3],(100,1));ret=np.tile([.01,-.02],(100,1));cash=np.full(100,.0001)
r=simulate(w,ret,cash,cal,episodes,r1,cost_bps=10)
assert np.allclose(r['weights'][19],[.4,.3])
assert np.allclose(r['weights'][20],[0,0]) and r['forced_liquidation'][20]
assert np.isclose(r['turnover'][20],.7)
assert np.isclose(r['returns'][20],cash[20]-.0007)
assert np.allclose(r['weights'][20:35],0)
assert np.allclose(r['weights'][35],[.4,.3])
assert np.isclose(r['returns'][35],.4*.01+.3*(-.02)+.3*.0001-.0007)
print('MULTISTOCK_CASH_R1_TEST_PASS')
