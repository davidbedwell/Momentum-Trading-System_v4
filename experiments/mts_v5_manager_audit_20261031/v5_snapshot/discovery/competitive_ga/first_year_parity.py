"""Bounded full-universe parity evidence, never a substitute for PIT provenance."""
import importlib.util
import sys
import numpy as np
import pandas as pd
from .first_year_manifest import validate_panel


def load_native(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    prior = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = prior
    return module


def ga6_features(raw, ga4, *, source='/opt/mts/ga5_feature_families.py'):
    """Original eight-family calculations plus unchanged tanh GA4 aliases.

    Do not rename momentum to recursive: native LEGACY maps momentum_5 to
    recursive, which is a five-session momentum difference, not return_5.
    """
    native = load_native(source, 'mts_native_ga5_families')
    sectors = raw[['ticker', 'sector']].drop_duplicates()
    if sectors.ticker.duplicated().any() or sectors.sector.isna().any():
        raise ValueError('require stable explicit sector mapping')
    if raw.duplicated(['date', 'ticker']).any() or ga4.duplicated(['date', 'ticker']).any():
        raise ValueError('duplicate native feature keys')
    values = native.compute(raw, dict(zip(sectors.ticker, sectors.sector)))
    aliases = [c for c in ga4 if c.startswith('ga4_')]
    merged = values.merge(ga4[['date', 'ticker', *aliases]], on=['date', 'ticker'],
                          how='outer', validate='one_to_one', indicator=True)
    if not merged['_merge'].eq('both').all():
        raise ValueError('GA6/GA4 feature coverage mismatch')
    return merged.drop(columns='_merge').sort_values(['date', 'ticker']).reset_index(drop=True)


def compare(actual, reference, *, columns, calendar, as_of, tickers, rtol=1e-12, atol=1e-12):
    """Check every value AND warmup nonfinite masks across 500 names.

    Reference must be produced independently by the selected native contract;
    this function does not certify reference authenticity by itself.
    """
    for frame in (actual, reference):
        validate_panel(frame, calendar=calendar, as_of=as_of, tickers=tickers)
    columns = tuple(columns)
    if not columns or any(c not in actual or c not in reference for c in columns):
        raise ValueError('missing parity feature columns')
    a = actual.sort_values(['date', 'ticker'])[list(columns)].to_numpy(dtype=float)
    b = reference.sort_values(['date', 'ticker'])[list(columns)].to_numpy(dtype=float)
    if np.isinf(a).any() or np.isinf(b).any():
        raise ValueError('infinite features are not valid warmup')
    if not np.array_equal(np.isnan(a), np.isnan(b)) or not np.allclose(a, b, rtol=rtol, atol=atol, equal_nan=True):
        raise ValueError('native feature parity mismatch')
    return dict(rows=len(actual), tickers=500, sessions=actual.date.nunique(),
                features=len(columns), finite_values=int(np.isfinite(a).sum()),
                warmup_values=int(np.isnan(a).sum()), parity=True)


def required_ga6(candidate, legacy):
    def leaves(node):
        return {node['family']} if 'family' in node else set().union(*(leaves(c) for c in node['children']))
    names = {getattr(candidate.genome, k) for k in
             ('entry_feature', 'hold_feature', 'exit_feature', 'regime_feature', 'sizing_feature', 'replace_feature')}
    return sorted({legacy.get(n, n) for n in names | leaves(candidate.entry_tree)})


def feature_eligibility(frame, required, gate):
    """Native warmup is ineligible, never filled. Gate coverage is mandatory."""
    if frame.ticker.duplicated().any() or set(frame.ticker) != set(gate):
        raise ValueError('require unique full dated cross section')
    if not required or set(required) - set(frame):
        raise ValueError('missing native required features')
    return {row['ticker']: bool(gate[row['ticker']] and
            all(np.isfinite(float(row[c])) for c in required))
            for row in frame.to_dict('records')}
