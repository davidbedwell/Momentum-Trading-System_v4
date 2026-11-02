"""Predeclared market benchmark policy and independent PIT universe diagnostic."""
from dataclasses import dataclass, replace
from pathlib import Path
import numpy as np
import pandas as pd
from .execution import Panel, load_panel
from .input_audit import inspect_prices

DEFAULT_SPY = Path('/opt/mts/ga6-git-backup/Research/Data/Comparators/SPY_YFINANCE_2005_2026.parquet')
SECONDARY = 'equal_weight_buy_and_hold_complete_PIT_universe'


@dataclass(frozen=True)
class BenchmarkPolicy:
    universe_profile: str = 'broad_us'

    def __post_init__(self):
        if self.universe_profile not in ('broad_us','nasdaq'):
            raise ValueError('Universe profile must be broad_us or nasdaq')

    @property
    def primary(self):
        return 'QQQ' if self.universe_profile == 'nasdaq' else 'SPY'

    def record(self):
        return dict(universe_profile=self.universe_profile,primary=self.primary,secondary=SECONDARY,
                    selection='declared before training and forward; no outcome-based switching')


def align(panel, dates):
    ix=panel.dates.get_indexer(dates)
    if (ix<0).any():
        missing=dates[ix<0].strftime('%Y-%m-%d').tolist()
        raise ValueError(f'Benchmark missing strategy sessions: {missing[:5]}')
    return replace(panel,dates=dates,open=panel.open[ix],close=panel.close[ix],
                   dividends=panel.dividends[ix],returns=panel.returns[ix],
                   features={k:v[ix] for k,v in panel.features.items()},
                   niche=panel.niche[ix],breadth=panel.breadth[ix],
                   eligible=panel.eligible[ix] if panel.eligible is not None else None,
                   screen_score=panel.screen_score[ix] if panel.screen_score is not None else None,
                   screen_mask=panel.screen_mask[ix] if panel.screen_mask is not None else None)


def load_primary(path, policy, end, dates):
    if path is None:
        raise FileNotFoundError(f'{policy.primary} requires --benchmark-data with verified OHLC/dividends; no benchmark fallback')
    path=Path(path)
    d=pd.read_parquet(path)
    # A one-instrument file without ticker must identify the declared ETF in its name.
    if 'ticker' not in d:
        if path.stem.upper().split('_')[0] != policy.primary:
            raise ValueError(f'Unidentified single-instrument file: expected {policy.primary} filename or ticker column')
        d['ticker']=policy.primary
    d=d[d.ticker==policy.primary].copy()
    if d.empty:
        raise ValueError(f'Required primary {policy.primary} is absent; no benchmark fallback')
    d['date']=pd.to_datetime(d.date)
    d=d[(d.date>='2022-01-01')&(d.date<end)].sort_values('date')
    required={'dividends','stock_splits'}
    if not required.issubset(d.columns):
        raise ValueError(f'{policy.primary} missing explicit dividends or split data')
    audit=inspect_prices(d)
    if not audit['usable'] or not np.isfinite(d.dividends).all() or (d.dividends<0).any():
        raise ValueError(f'Invalid {policy.primary} OHLC/dividend data')
    jumps=d.close/d.close.shift(1)
    if (((jumps<.5)|(jumps>1.8)) & (d.stock_splits>0)).any():
        raise ValueError('Ambiguous ETF split normalization')
    c=d.close.to_numpy()[:,None];o=d.open.to_numpy()[:,None];div=d.dividends.to_numpy()[:,None]
    returns=(c+div)/np.vstack([np.full((1,1),np.nan),c[:-1]])-1
    panel=Panel(pd.DatetimeIndex(d.date),[policy.primary],o,c,div,returns,{},
                np.zeros_like(c,dtype=int),np.zeros(len(d)))
    panel=align(panel,dates)
    if not np.isfinite(panel.open).all() or not np.isfinite(panel.close).all():
        raise ValueError('Primary ETF requires every strategy session; no cash substitution')
    return panel,audit


def attach_primary(panel, path, policy, end):
    primary,audit=load_primary(path,policy,end,panel.dates)
    return replace(panel,primary_benchmark=primary),audit


def load_universe(path, symbols, end, dates, membership=None):
    panel,audit=load_panel(path,end=end,sample=symbols,membership=membership)
    return align(panel,dates),audit


def primary_name(panel):
    if panel.primary_benchmark is not None:
        return panel.primary_benchmark.symbols[0]
    if panel.synthetic_benchmark_fixture:
        return 'synthetic_equal_weight_fixture'
    raise ValueError('Primary SPY/QQQ benchmark must be attached; equal-weight fallback is forbidden')


def selection_benchmark(panel,start,end):
    from .objective import benchmark
    name=primary_name(panel)
    source=panel.primary_benchmark if panel.primary_benchmark is not None else panel
    result=benchmark(source,start,end)
    result['benchmark_id']=name
    return result
