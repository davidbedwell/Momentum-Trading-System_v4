"""Explicit, bounded archive restoration. Selection is by identity, never returns.

A file digest identifies bytes, not a training cutoff or PIT certification.
Caller must supply independently governed training dates to daily producers.
"""
import hashlib
import json
from pathlib import Path
import sqlite3


def ga6(path, identities):
    from ga6.structural_evolution_v3_20261022.structural_candidate import StructuralCandidate
    ids = tuple(identities)
    if not 1 <= len(ids) <= 16 or len(set(ids)) != len(ids):
        raise ValueError('require 1..16 distinct archived GA6 identities')
    result = {}
    with sqlite3.connect(Path(path).resolve().as_uri() + '?mode=ro', uri=True) as db:
        for cid in ids:
            rows = db.execute('SELECT definition FROM chromosomes WHERE id=?', (cid,)).fetchall()
            if len(rows) != 1:
                raise ValueError('missing or ambiguous archived GA6 identity')
            result[cid] = StructuralCandidate.restore(json.loads(rows[0][0]))
    return result


def ga7(path, identities):
    from ga7.engine import Genome, validate
    from ga7.runner import FEATURES
    path = Path(path)
    if path.stat().st_size > 16_000_000:
        raise ValueError('checkpoint exceeds bounded archive reader')
    raw = path.read_bytes()
    record = json.loads(raw)
    population = record['population']
    restored = {}
    for item in population:
        genome = validate(Genome(**item), FEATURES)
        restored[genome.identity()] = genome
    ids = tuple(identities)
    if not 1 <= len(ids) <= 16 or len(set(ids)) != len(ids):
        raise ValueError('require 1..16 distinct archived GA7 identities')
    if set(ids) - set(restored):
        raise ValueError('missing archived GA7 identity')
    return {cid: restored[cid] for cid in ids}, hashlib.sha256(raw).hexdigest()


def ga7_bars(frame, *, decision_date, eligibility, columns):
    """Native runner uses eligible-universe percentile ranks, not tanh aliases.

    Explicit columns come from the selected native runner's feature registry.
    Supply the complete intended universe, with externally governed eligibility.
    """
    import pandas as pd
    dates = pd.to_datetime(frame['date']).dt.strftime('%Y-%m-%d')
    if frame.empty or set(dates) != {decision_date} or frame.ticker.duplicated().any():
        raise ValueError('require one dated unique GA7 cross section')
    if set(frame.ticker) != set(eligibility):
        raise ValueError('explicit eligibility required for every ticker')
    if any(type(v) is not bool for v in eligibility.values()):
        raise ValueError('GA7 eligibility must contain explicit booleans')
    if set(columns) - set(frame):
        raise ValueError('missing native GA7 columns')
    bars = {}
    for row in frame.to_dict('records'):
        ticker = row['ticker']
        bars[ticker] = {'close': float(row['close']),
            'eligible': bool(eligibility[ticker]),
            **({'controlling_niche':row['controlling_niche']} if 'controlling_niche' in row else {}),
            'features': {col: float(row[col]) for col in columns}}
    from ga7.fold_features import rank_filtered_sessions
    return rank_filtered_sessions([(decision_date, bars, False)], set(bars), columns)[0][1]
