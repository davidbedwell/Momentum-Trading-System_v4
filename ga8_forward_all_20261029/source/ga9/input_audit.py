"""Read-only DEV79 integrity and legacy grammar inventory, without runtime imports."""
import ast
import hashlib
from pathlib import Path
import numpy as np
import pandas as pd
MTS=Path('/opt/mts')

def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def inspect_prices(frame):
    """Inspect bars only; never compute returns or strategy scores on holdout."""
    required = {'date', 'ticker', 'open', 'high', 'low', 'close', 'adj_close', 'volume'}
    missing = sorted(required - set(frame.columns))
    if missing:
        return {'missing_columns': missing, 'usable': False}
    d = frame.copy()
    d['date'] = pd.to_datetime(d.date)
    d = d[(d.date >= '2022-01-01') & (d.date < '2027-01-01')]
    prices = d[['open', 'high', 'low', 'close', 'adj_close']]
    bad = (~np.isfinite(prices) | (prices <= 0)).any(axis=1)
    bad_range = ((d.high < d[['open', 'close', 'low']].max(axis=1)) |
                 (d.low > d[['open', 'close', 'high']].min(axis=1)))
    sessions = pd.DatetimeIndex(sorted(d.date.unique()))
    symbols = []
    for ticker, g in d.groupby('ticker'):
        internal = sessions[(sessions >= g.date.min()) & (sessions <= g.date.max())]
        symbols.append({'ticker': ticker, 'first': str(g.date.min().date()),
                        'last': str(g.date.max().date()), 'rows': len(g),
                        'missing_peer_sessions_inside_observed_lifetime':
                        len(internal.difference(g.date)),
                        'absent_peer_sessions_before_first_bar': int((sessions < g.date.min()).sum())})
    years = []
    for year, g in d.groupby(d.date.dt.year):
        years.append({'year': int(year), 'rows': len(g), 'symbols': g.ticker.nunique(),
                      'sessions': g.date.nunique()})
    duplicates = int(d.duplicated(['ticker', 'date']).sum())
    nulls = int(d[list(required)].isna().sum().sum())
    return {'missing_columns': [], 'rows': len(d), 'symbols': d.ticker.nunique(),
            'first': str(d.date.min().date()), 'last': str(d.date.max().date()),
            'peer_sessions': len(sessions), 'years': years, 'per_symbol': symbols,
            'duplicate_bars': duplicates, 'null_required_values': nulls,
            'invalid_price_rows': int(bad.sum()), 'invalid_ohlc_range_rows': int(bad_range.sum()),
            'usable': not (duplicates or nulls or bad.any() or bad_range.any()),
            'calendar_basis': 'Observed peer-session union; not an independent exchange calendar.',
            'cutoff_note': '2026 is partial through source cutoff; no future or missing bars filled.'}

def grammar_inventory():
    # Parse source instead of importing the old grammar: its registry accesses a
    # protected predictor file and importing it would couple GA8 to legacy runtime.
    source = MTS / 'ga5_chromosome_contract.py'
    tree = ast.parse(source.read_text())
    genome = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Genome')
    fields = [n.target.id for n in genome.body if isinstance(n, ast.AnnAssign)]
    families = ['trend', 'momentum', 'volatility', 'volume', 'recursive', 'sector',
                'breadth', 'relative_strength']
    return {'source': str(source), 'sha256': sha256(source), 'genome_fields': fields,
            'families': families, 'entry_combinations': 'Legacy structural entry trees exist; not evaluated.',
            'native_capabilities': ['entry', 'hold', 'exit', 'regime', 'sizing', 'replacement',
                                    'stop_loss', 'trailing_stop', 'time_exit', 'scale_in', 'scale_out'],
            'legacy_caveats': ['13 niche IDs are identifiers, not causal membership proof.',
                              'Legacy GA4 registry requires inaccessible archived predictors.',
                              'Recompute backward-only features from bars for GA8; do not trust archived ranks.',
                              'Do not import old fitness, winners, or 2009-2018 performance as evidence.']}
