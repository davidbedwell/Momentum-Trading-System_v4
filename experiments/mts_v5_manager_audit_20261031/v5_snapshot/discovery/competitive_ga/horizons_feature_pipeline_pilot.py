"""Bounded, non-production Horizons reconstruction smoke test on scenario 1."""
import pandas as pd
from .synthetic_fiveyear_panel import ROOT
from .horizons_external_stress import load
from .horizons_feature_reconstruction import raw_panel
from .horizons_feature_normalization import normalize
from .horizons_native_score import FEATURES
from .horizons_stress_governance import require_certified

def run(scenario=1,sessions=80,mode='research'):
 require_certified(mode)
 if scenario not in range(1,6):raise ValueError('invalid scenario')
 p=pd.read_parquet(ROOT/f'universe_{scenario}_ga4_native.parquet')
 p['date']=pd.to_datetime(p.date)
 dates=pd.DatetimeIndex(sorted(p.date.unique()))
 stress,meta=load(dates)
 valid=dates[dates<=pd.Timestamp(meta['source_end'])]
 selected=valid[-sessions:]
 # Compute historical market features and percentiles before selecting test window.
 subset=p.loc[p.date.isin(valid)]
 raw=raw_panel(subset,stress)
 normalized=normalize(raw)
 normalized=normalized.loc[normalized.date.isin(selected)]
 return {'scenario':scenario,'sessions':int(normalized.date.nunique()),'tickers':int(normalized.ticker.nunique()),'rows':len(normalized),'features':len(FEATURES),'missing_values':int(normalized[list(FEATURES)].isna().sum().sum()),'source_end':meta['source_end'],'excluded_future_dates':meta['excluded_dates'],'first':str(selected.min().date()),'last':str(selected.max().date())}
if __name__=='__main__':print(run())
