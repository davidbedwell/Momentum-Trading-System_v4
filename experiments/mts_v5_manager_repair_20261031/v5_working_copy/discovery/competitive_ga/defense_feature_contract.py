"""Required causal, market-independent detector input contract.

No detector is inferred from dates, missing data, or stock returns alone.
"""
from math import isfinite

REQUIRED=('market_close','market_sma200','below_sma200_streak','funding_stress_percentile_lagged',
          'funding_percentile','volatility_of_volatility_percentile','breadth_20d_bad_percentile',
          'drawdown_bad_percentile','market_10d_return')

def validate(row):
    missing=[name for name in REQUIRED if name not in row]
    if missing: raise ValueError('missing causal defense features: '+','.join(missing))
    for name in REQUIRED:
        value=row[name]
        if not isinstance(value,(int,float)) or not isfinite(value):
            raise ValueError('invalid defense feature: '+name)
    for name in ('funding_stress_percentile_lagged','funding_percentile',
                 'volatility_of_volatility_percentile','breadth_20d_bad_percentile','drawdown_bad_percentile'):
        if not 0<=row[name]<=1:raise ValueError('invalid percentile: '+name)
    if row['market_close']<=0 or row['market_sma200']<=0 or row['below_sma200_streak']<0:
        raise ValueError('invalid market history')
    return row

def known_criteria(row):
    validate(row)
    fast=(all(row[k]>=.95 for k in ('funding_percentile','volatility_of_volatility_percentile',
          'breadth_20d_bad_percentile','drawdown_bad_percentile')) and row['market_10d_return']<=-.10)
    b1=(row['below_sma200_streak']>=10 and row['funding_stress_percentile_lagged']>=.70)
    return {'A_v2_fast_component':fast,'B1':b1}
