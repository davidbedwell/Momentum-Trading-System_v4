"""Reconstruct Horizons native stock aliases and market dimensions causally.
External VIX/VVIX/funding/credit must be supplied from dated source records;
no synthetic or zero-filled external stress inputs are permitted.
"""
import numpy as np
import pandas as pd
from .horizons_native_score import STOCK,MARKET
STOCK_SOURCE={'ret5':'return_5__v1','ret20':'return_20__v1','sma20':'close_to_sma_20__v1','range20':'range_position_20__v1','rsi14':'rsi_14__v1','relvol':'relative_volume_20_percentile__v1','dd252':'drawdown_252__v1','rvpct':'realized_vol_20_percentile__v1'}
EXTERNAL=('vix','vvix','funding','credit')

def raw_panel(frame,external=None):
 required={'date','ticker','eligible',*STOCK_SOURCE.values(),'breadth_above_sma_200__v1','breadth_positive_20__v1'}
 missing=required-set(frame.columns)
 if missing:raise ValueError('missing original Horizons source columns: '+str(sorted(missing)))
 p=frame.loc[frame.eligible.fillna(False)].copy()
 if p.duplicated(['date','ticker']).any():raise ValueError('duplicate stock-date')
 p=p.rename(columns={v:k for k,v in STOCK_SOURCE.items()})
 market=p.groupby('date').agg(mret5=('ret5','median'),mret20=('ret20','median'),mdd=('dd252','median'),breadth200=('breadth_above_sma_200__v1','median'),breadth20=('breadth_positive_20__v1','median'),mrv=('rvpct','median')).sort_index()
 market['breadth_vel5']=market.breadth20-market.breadth20.shift(5)
 market['breadth_vel10']=market.breadth20-market.breadth20.shift(10)
 market['breadth_accel']=market.breadth_vel5-market.breadth_vel5.shift(5)
 market['breadth_persist']=market.breadth20.rolling(5,min_periods=3).mean()
 market['prior_destruction']=-market.mdd
 market['price_impulse']=market.mret5
 market['failed_rebound_reduction']=market.mret20-market.mret20.shift(5)
 market['short_trend_repair']=market.mret20-market.mret20.shift(10)
 market['recovery_retention']=market.mret20-market.mret20.rolling(20,min_periods=5).min()
 if external is None:raise ValueError('dated external stress inputs required; no synthetic substitute')
 if not {'date',*EXTERNAL}<=set(external.columns):raise ValueError('incomplete external stress input')
 ext=external.set_index('date').sort_index()
 if ext.index.has_duplicates:raise ValueError('duplicate external dates')
 # Source preprocessing and release lags must be certified before supplying external.
 for name in EXTERNAL:market[name]=ext[name].reindex(market.index)
 if market[list(EXTERNAL)].isna().any().any():raise ValueError('external stress coverage incomplete')
 market['stress_norm']=-(market.vix.pct_change(5).replace([np.inf,-np.inf],np.nan).fillna(0)+market.vvix.pct_change(5).replace([np.inf,-np.inf],np.nan).fillna(0))/2
 return p[['date','ticker',*STOCK]].merge(market[list(MARKET)].reset_index(),on='date',validate='many_to_one')
