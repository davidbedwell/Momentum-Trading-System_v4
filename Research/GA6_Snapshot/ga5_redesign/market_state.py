"""Observable multidimensional market-state features; no fixed niche count.
Research features only. All rolling calculations use current/past sessions.
"""
import numpy as np
import pandas as pd

DIMENSIONS={
 'direction_structure':('market_return_20','market_return_63','market_trend_50_200'),
 'conditions_volume':('relative_market_volume_20','market_volume_trend_20'),
 'conditions_volatility':('market_realized_volatility_20','market_volatility_ratio_20_63'),
 'conditions_liquidity':('market_dollar_volume_20',),
 'conditions_breadth':('market_breadth_positive_20',),
 'behavior':('market_momentum_20','market_rotation_dispersion_20'),
}
def compute(frame):
 required={'date','ticker','close','volume'}
 if not required.issubset(frame.columns):raise ValueError('Missing market-state inputs')
 d=frame.sort_values(['ticker','date']).copy()
 if (d['close']<=0).any() or (d['volume']<0).any():raise ValueError('Invalid price/volume')
 g=d.groupby('ticker',sort=False)
 d['ret_1']=g['close'].pct_change(fill_method=None)
 d['ret_20']=g['close'].pct_change(20,fill_method=None)
 d['dollar_volume']=d['close']*d['volume']
 # Cross-sectional equal-weight research proxy; PIT membership must be certified.
 daily=d.groupby('date',sort=True).agg(
  market_return_1=('ret_1','mean'),
  market_breadth_positive_20=('ret_20',lambda x:(x.dropna()>0).mean() if x.notna().any() else np.nan),
  market_volume=('volume','sum'),
  market_dollar_volume=('dollar_volume','sum'),
  market_rotation_dispersion_20=('ret_20','std'))
 r=daily['market_return_1']
 daily['market_return_20']=(1+r).rolling(20,min_periods=20).apply(np.prod,raw=True)-1
 daily['market_return_63']=(1+r).rolling(63,min_periods=63).apply(np.prod,raw=True)-1
 proxy=(1+r.fillna(0)).cumprod()
 ma50=proxy.rolling(50,min_periods=50).mean()
 ma200=proxy.rolling(200,min_periods=200).mean()
 daily['market_trend_50_200']=ma50/ma200-1
 daily['market_realized_volatility_20']=r.rolling(20,min_periods=20).std()
 vol63=r.rolling(63,min_periods=63).std().replace(0,np.nan)
 daily['market_volatility_ratio_20_63']=daily['market_realized_volatility_20']/vol63
 daily['relative_market_volume_20']=daily['market_volume']/daily['market_volume'].rolling(20,min_periods=20).mean()-1
 daily['market_volume_trend_20']=daily['market_volume'].rolling(5,min_periods=5).mean()/daily['market_volume'].rolling(20,min_periods=20).mean()-1
 daily['market_dollar_volume_20']=daily['market_dollar_volume'].rolling(20,min_periods=20).mean()
 daily['market_momentum_20']=daily['market_return_20']
 return daily[[x for v in DIMENSIONS.values() for x in v]].reset_index()
