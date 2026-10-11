import numpy as np,pandas as pd
from scripts.thirteen_window_regime_execution_20261011 import simulate
cal=pd.bdate_range('2020-01-01',periods=100)
episodes={'one':{'peak':str(cal[10].date()),'trough':str(cal[20].date())}}
r1=np.zeros(100,dtype=bool);r1[34]=True
ret=np.full(100,.01);cash=np.full(100,.0001)
x=simulate(np.ones(100),ret,cash,cal,episodes,r1,cost_bps=10)
assert x['excluded'][20:31].all() and not x['excluded'][19] and not x['excluded'][31]
assert x['exposure'][19]==1 and x['exposure'][20]==0
assert x['forced_liquidation'][20] and x['turnover'][20]==1
assert abs(x['returns'][20]-(cash[20]-.001))<1e-12
assert not x['exposure'][20:35].any()
assert x['exposure'][35]==1 and x['turnover'][35]==1
assert abs(x['returns'][19]-.01)<1e-12
assert abs(x['returns'][35]-(.01-.001))<1e-12
print('THIRTEEN_WINDOW_LIQUIDATION_CASH_R1_TEST_PASS')
