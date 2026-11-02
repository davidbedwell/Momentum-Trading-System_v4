"""Disk-backed native features with an immutable caller-supplied proof seal.

Stock-local recursion always sees the entire authorized prefix. Only the native
cross-sectional stage is windowed: its sole longitudinal dependency is the
20-observation percentile difference. Cache identities include source bytes.
"""
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from .first_year_features import RAW, SOURCE, COLUMNS
from .first_year_manifest import digest, validate_panel
from .first_year_parity import load_native

TRANSITIVE = Path('/opt/mts/thunder-migration/mts-layered-run-20261007/Reconstruction/Certified-Stage2-Source-20261007/MTS_V4/derived_feature_factory.py')


def inventory(path=RAW):
    """Decode identity/calendar columns only, never prices or outcomes."""
    dates = {}
    for batch in pq.ParquetFile(path).iter_batches(columns=['Date', 'Ticker'], batch_size=32000):
        for d, t in batch.to_pandas().itertuples(index=False, name=None):
            d = pd.Timestamp(d).strftime('%Y-%m-%d')
            names = dates.setdefault(d, set())
            if t in names:
                raise ValueError('duplicate source identity')
            names.add(t)
    sessions = tuple(sorted(dates))
    if not sessions:
        raise ValueError('empty source')
    tickers = tuple(sorted(dates[sessions[0]]))
    if len(tickers) != 500 or any(v != set(tickers) for v in dates.values()):
        raise ValueError('source requires rectangular 500-name calendar')
    return sessions, tickers


def chunks(*, calendar, as_of, tickers, cache, raw_path=RAW, chunk_sessions=32):
    calendar.permit(as_of)  # Must precede source hashes, cache reads and price I/O.
    if type(chunk_sessions) is not int or not 1 <= chunk_sessions <= 128:
        raise ValueError('bounded chunk size required')
    if len(tickers) != 500 or len(set(tickers)) != 500:
        raise ValueError('full 500-name universe required')
    dates = [d for d in calendar.sessions if d <= as_of]
    if len(dates) > 1260:
        raise ValueError('1260-session engineering bound')
    root = Path(cache).resolve()
    repo = Path(__file__).resolve().parents[2]
    if not (root.is_relative_to('/tmp') or root.is_relative_to(repo)):
        raise ValueError('cache must remain in workspace or /tmp')
    provenance = dict(as_of=as_of, dates=dates, tickers=sorted(tickers),
        hashes={str(p): digest(p) for p in (Path(raw_path), SOURCE, TRANSITIVE, Path(__file__))})
    key = hashlib.sha256(json.dumps(provenance, sort_keys=True).encode()).hexdigest()
    root = root / key
    root.mkdir(parents=True, exist_ok=True)
    (root / 'provenance.json').write_text(json.dumps(provenance, sort_keys=True))
    factory = load_native(SOURCE, 'mts_stream_native_factory')
    # Each file contains one complete local history, including all recursive
    # state. Never truncate to the nominal maximum rolling lookback.
    for i, ticker in enumerate(tickers):
        target = root / f'{i:03}.parquet'
        seal = target.with_suffix('.sha256')
        if target.exists() and seal.exists() and digest(target) == seal.read_text():
            continue
        raw = pd.read_parquet(raw_path, columns=COLUMNS,
            filters=[('Date', '<=', pd.Timestamp(as_of)), ('Ticker', '==', ticker)])
        raw = raw.rename(columns=str.lower).sort_values('date')
        if list(pd.to_datetime(raw.date).dt.strftime('%Y-%m-%d')) != dates or raw.sector.nunique() != 1:
            raise ValueError('invalid local calendar or changing sector')
        values = raw[['open', 'high', 'low', 'close', 'volume']].to_numpy(dtype=float)
        if (not np.isfinite(values).all() or (values[:, :4] <= 0).any() or
                (values[:, 4] < 0).any() or
                (raw.high < raw[['open', 'low', 'close']].max(axis=1)).any() or
                (raw.low > raw[['open', 'high', 'close']].min(axis=1)).any()):
            raise ValueError('invalid local OHLCV')
        local = factory.build_stock_local_frame(raw, ticker, str(raw.sector.iloc[0]), None)
        local.to_parquet(target, index=False)
        seal.write_text(digest(target))
    for start in range(0, len(dates), chunk_sessions):
        end = min(start + chunk_sessions, len(dates))
        lo = dates[max(0, start - 20)]
        hi = dates[end - 1]
        local = pd.concat([pd.read_parquet(root / f'{i:03}.parquet',
            filters=[('effective_date', '>=', lo), ('effective_date', '<=', hi)])
            for i in range(500)], ignore_index=True)
        full = factory.recompute_cross_sectional(local).rename(columns={'effective_date': 'date'})
        full['date'] = pd.to_datetime(full.date).dt.strftime('%Y-%m-%d')
        full = full.loc[full.date >= dates[start]].reset_index(drop=True)
        # Validate a chunk with a minimal calendar-free rectangular identity
        # check; validate_panel intentionally requires a full prefix.
        expected = pd.MultiIndex.from_product([dates[start:end], tickers])
        actual = pd.MultiIndex.from_frame(full[['date', 'ticker']])
        if actual.has_duplicates or len(actual) != len(expected) or len(expected.difference(actual)):
            raise ValueError('incomplete cross-sectional chunk')
        aliases = {f'ga4_{c}': np.tanh(pd.to_numeric(full[c], errors='coerce').astype(float).clip(-1e8, 1e8))
                   for c in full if c.endswith('__v1')}
        yield pd.concat([full, pd.DataFrame(aliases)], axis=1)
