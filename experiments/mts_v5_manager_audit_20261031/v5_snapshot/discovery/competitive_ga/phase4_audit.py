"""Bounded streaming parity audit. Existing Phase 3 proof seal is preserved."""
import argparse
import json
from pathlib import Path
import resource
import time
import numpy as np
import pandas as pd
from .streaming_first_year import inventory, chunks
from .first_year_features import RAW
from .first_year_manifest import Calendar, digest


def audit(*, cache='/tmp/mts_phase4_stream', reference='/tmp/mts_phase3_feature_audit'):
    wall, cpu = time.perf_counter(), time.process_time()
    sessions, tickers = inventory()
    calendar = Calendar(sessions, '2022-12-30', '2023-06-30', '2023-07-03')
    as_of = calendar.validation_end
    ref = Path(reference)
    provenance = json.loads((ref / 'provenance.json').read_text())
    if provenance['as_of'] != as_of or any(digest(p) != h for p, h in provenance['hashes'].items()):
        raise ValueError('Phase 3 reference provenance changed; rebuild explicitly')
    if digest(ref / 'full.parquet') != (ref / 'full.sha256').read_text():
        raise ValueError('reference content hash mismatch')
    daily = []
    finite = warmup = cells = 0
    for panel in chunks(calendar=calendar, as_of=as_of, tickers=tickers, cache=cache):
        lo, hi = panel.date.min(), panel.date.max()
        reference_panel = pd.read_parquet(ref / 'full.parquet',
            filters=[('date', '>=', pd.Timestamp(lo)), ('date', '<=', pd.Timestamp(hi))])
        columns = [c for c in panel if c.endswith('__v1')]
        a = panel.sort_values(['date', 'ticker'])[columns].to_numpy(dtype=float)
        b = reference_panel.sort_values(['date', 'ticker'])[columns].to_numpy(dtype=float)
        if np.isinf(a).any() or not np.array_equal(np.isnan(a), np.isnan(b)) or not np.allclose(a, b, equal_nan=True, rtol=1e-12, atol=1e-12):
            raise ValueError('stream/full native parity mismatch')
        cells += a.size
        finite += int(np.isfinite(a).sum())
        warmup += int(np.isnan(a).sum())
        for date, section in panel.groupby('date'):
            values = section.sort_values('ticker')[columns]
            daily.append(dict(date=date, tickers=500, next_open=sessions[sessions.index(date)+1],
                features_sha256=__import__('hashlib').sha256(pd.util.hash_pandas_object(values, index=False).to_numpy().tobytes()).hexdigest()))
        print(f'parity {hi}: {len(daily)} sessions', flush=True)
    return dict(status='BLOCKED', scope='engineering_feature_audit_only',
        available_sessions=len(sessions), first_available=sessions[0], last_available=sessions[-1],
        value_sessions=len(daily), value_end=as_of, sealed_sessions=sum(d >= calendar.proof_start for d in sessions),
        proof_values_read=False, metadata_columns_read=['Date', 'Ticker'],
        proof_start=calendar.proof_start, validation_reused='already opened Phase 3 engineering prefix; no tuning',
        parity=dict(features=len(columns), cells=cells, finite=finite, warmup=warmup, passed=True,
                    reference='hash-verified Phase 3 native full-history build'),
        performance=dict(wall_seconds=time.perf_counter()-wall, cpu_seconds=time.process_time()-cpu,
                         peak_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024),
        sources=provenance['hashes'], implementation_sha256=digest(__file__), daily=daily,
        blockers=['Remaining dates sealed by existing Phase 3 calendar; no authority to unseal',
                  'PIT, earnings, corporate actions, niche lineage, model training cutoffs unknown',
                  'GA4 approved exit and Horizons compatible stress provenance absent'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    target = args.output.resolve()
    if not (target.is_relative_to(Path(__file__).resolve().parents[2]) or target.is_relative_to('/tmp')):
        parser.error('workspace or /tmp output required')
    result = audit()
    target.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('daily', 'sources')}, indent=2))
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
