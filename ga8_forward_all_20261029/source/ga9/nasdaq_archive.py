"""Read-only archive adapter. Diagnostic projections never authorize GA9 replay.

Run: python -m ga9.nasdaq_archive --archive PATH --output NEW_DIRECTORY
No vendor requests, strategy evaluation, alias stitching or missing-value filling.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def normalize(path):
    """Map vendor fields without asserting identity or adjustment equivalence."""
    path = Path(path)
    if path.suffix == '.parquet':
        d = pd.read_parquet(path).reset_index().rename(columns={
            'Date': 'date', 'Open': 'open', 'High': 'high', 'Low': 'low',
            'Close': 'close', 'Adj Close': 'adj_close', 'Volume': 'volume',
            'Dividends': 'dividends', 'Stock Splits': 'stock_splits'})
    else:
        d = pd.DataFrame(json.loads(path.read_text())).rename(columns={'adjusted_close': 'adj_close'})
    # Preserve the vendor's local session date, rather than shifting it to UTC.
    d['date'] = pd.DatetimeIndex(pd.to_datetime(d.date)).tz_localize(None).normalize()
    d['ticker'] = path.stem
    d['source_file'] = str(path)
    d['source_sha256'] = digest(path)
    for col in ['dividends', 'stock_splits']:
        if col not in d:
            d[col] = np.nan  # Unknown is never an invented zero.
    return d


def bar_issues(d):
    prices = d[['open', 'high', 'low', 'close', 'adj_close']]
    invalid = (~np.isfinite(prices) | (prices <= 0)).any(axis=1)
    invalid |= (d.high < d[['open', 'low', 'close']].max(axis=1))
    invalid |= (d.low > d[['open', 'high', 'close']].min(axis=1))
    invalid |= ~np.isfinite(d.volume) | (d.volume < 0)
    return {'duplicates': int(d.duplicated(['ticker', 'date']).sum()),
            'invalid_rows': int(invalid.sum()),
            'unknown_action_rows': int(d[['dividends', 'stock_splits']].isna().any(axis=1).sum())}


def snapshot_projection(snapshots, end='2026-01-01'):
    """Explicitly unverified half-open observations, with unknown known_at/ID.

    Deliberately incompatible with membership_mask's required known_at gate.
    No claim that the roster persisted between observations.
    """
    dates = [s['effective_date'] for s in snapshots]
    if dates != sorted(set(dates)):
        raise ValueError('Snapshots must have unique increasing dates')
    rows = []
    for i, s in enumerate(snapshots[:-1]):
        start, stop = max(s['effective_date'], '2022-01-01'), min(dates[i+1], end)
        if start >= stop:
            continue
        if len(s['eligible_tickers']) != len(set(s['eligible_tickers'])):
            raise ValueError('Duplicate snapshot symbols')
        for ticker in s['eligible_tickers']:
            rows.append(dict(ticker=ticker, effective_from=start, effective_to=stop,
                             known_at=None, security_id=None, snapshot_date=dates[i],
                             status='UNVERIFIED_SNAPSHOT_PROJECTION'))
    return pd.DataFrame(rows)


def require_replay_inputs(report):
    """No manifest label or caller-supplied boolean can certify this adapter.

    This archive lacks certified membership/identity/action evidence. A future
    certifying implementation must independently validate those records first.
    """
    raise ValueError('Archive replay blocked: ' + '; '.join(report['blockers']))


def audit(archive, output):
    archive, output = Path(archive), Path(output)
    if not archive.is_dir():
        raise ValueError('Archive directory required')
    output.mkdir(parents=True, exist_ok=False)
    files = sorted(p for p in archive.rglob('*') if p.is_file())
    inventory = {str(p.relative_to(archive)): {'bytes': p.stat().st_size, 'sha256': digest(p)} for p in files}
    read = lambda name: json.loads((archive/name).read_text())
    snapshots = read('eligible_membership_snapshots_2007_2026.json')
    projected = snapshot_projection(snapshots)
    projected.to_csv(output/'membership_UNVERIFIED.csv', index=False)
    identities = read('identity_reconciliation_candidates_20261012.json')['records']
    pd.DataFrame(identities).to_csv(output/'identity_exceptions.csv', index=False)
    bars, summaries = {}, []
    for folder, suffix in [('price_raw', '*.parquet'), ('price_eodhd_raw', '*.json')]:
        for path in sorted((archive/folder).glob(suffix)):
            d = normalize(path)
            bars.setdefault(path.stem, []).append(d)
            summaries.append(dict(ticker=path.stem, source=str(path.relative_to(archive)),
                                  rows=len(d), first=str(d.date.min().date()),
                                  last=str(d.date.max().date()), **bar_issues(d)))
    pd.DataFrame(summaries).to_csv(output/'raw_bar_audit.csv', index=False)
    all_bars = pd.concat([d for parts in bars.values() for d in parts], ignore_index=True)
    # Peer union is useful to quantify gaps, but cannot prove session completeness.
    sessions = pd.DatetimeIndex(sorted(all_bars.date.unique()))
    unresolved = {r['historical_symbol'] for r in identities if not r.get('allow_in_backtest', False)}
    years, gaps, requirements = [], [], []
    for year in range(2022, 2026):
        cal = sessions[(sessions >= f'{year}-01-01') & (sessions < f'{year+1}-01-01')]
        expected, observed, active, missing_symbols = 0, 0, set(), set()
        for r in projected.itertuples():
            needed = cal[(cal >= r.effective_from) & (cal < r.effective_to)]
            # Retrospective coverage correction only; never grants PIT eligibility.
            if r.ticker == 'XLNX':
                from .ticker_lineage import XLNX
                needed = needed[needed <= pd.Timestamp(XLNX.effective_at)]
            if not len(needed):
                continue
            active.add(r.ticker)
            expected += len(needed)
            parts = bars.get(r.ticker, [])
            present = pd.DatetimeIndex([]) if not parts else pd.DatetimeIndex(pd.concat(parts).date.unique())
            missing = needed.difference(present)
            prior = sessions[sessions < r.effective_from][-120:]
            after = sessions[sessions >= r.effective_to][:1]
            requirements.append(dict(year=year, ticker=r.ticker,
                                     effective_from=r.effective_from, effective_to=r.effective_to,
                                     missing_warmup_peer_sessions=len(prior.difference(present)),
                                     observed_warmup_sessions=len(prior),
                                     exit_peer_date=str(after[0].date()) if len(after) else None,
                                     missing_exit_peer_mark=not len(after) or after[0] not in present))
            observed += len(needed)-len(missing)
            if not parts:
                missing_symbols.add(r.ticker)
            gaps.extend({'year': year, 'ticker': r.ticker, 'date': str(day.date())} for day in missing)
        raw = all_bars[(all_bars.date >= f'{year}-01-01') & (all_bars.date < f'{year+1}-01-01')]
        years.append(dict(year=year, snapshots=sum(s['effective_date'].startswith(str(year)) for s in snapshots),
                          peer_sessions=len(cal), projected_symbols=len(active),
                          projected_security_sessions=expected, observed_projected_sessions=observed,
                          missing_projected_sessions=expected-observed, no_raw_file=sorted(missing_symbols),
                          unresolved_identity_symbols=sorted(active & unresolved),
                          raw_rows=len(raw), raw_symbols=int(raw.ticker.nunique()), **bar_issues(raw),
                          certified_PIT_security_sessions=0))
    pd.DataFrame(requirements).to_csv(output/'warmup_exit_UNVERIFIED.csv', index=False)
    pd.DataFrame(gaps, columns=['year','ticker','date']).to_csv(output/'missing_projected_bars.csv', index=False)
    checks = read('SOURCE_AND_FILE_CHECKSUMS.json')
    checksum_errors = [n for n, v in checks.items() if isinstance(v, dict) and 'sha256' in v
                       and (n not in inventory or inventory[n]['sha256'] != v['sha256'])]
    official = read('official_event_crosscheck_20261012.json')
    report = dict(status='BLOCKED_NOT_PIT_CERTIFIED', archive=str(archive), files=len(files),
                  bytes=sum(v['bytes'] for v in inventory.values()), snapshots=len(snapshots),
                  unique_eligible_tickers=len(set(t for s in snapshots for t in s['eligible_tickers'])),
                  raw_files=len(summaries), checksum_errors=checksum_errors,
                  overlapping_vendor_symbols=sorted(t for t, parts in bars.items() if len(parts)>1),
                  source_readiness=read('nas100_readiness_audit_20261012.json'),
                  identity_quarantine=read('protected_alias_quarantine_20261012.json'),
                  calendar_basis='Observed vendor peer-session union; independent exchange calendar unavailable',
                  official_crosscheck=official, years=years,
                  blockers=['Snapshot differences are not exact membership events; known_at and stable security IDs absent',
                            'Only partial official crosscheck; no certified starting roster or complete event chain',
                            'Identity quarantine prohibits trading; unresolved aliases and share classes retained',
                            'EODHD action fields absent; Yahoo raw/adjusted corporate actions not reconciled',
                            'Independent calendar, 120-session warmup and next-open exit marks not certified',
                            'No archive QQQ comparator; benchmark policy must be frozen before replay'],
                  replay_executed=False, long_GA_executed=False)
    (output/'inventory.json').write_text(json.dumps(inventory, indent=2)+'\n')
    (output/'coverage.json').write_text(json.dumps(report, indent=2)+'\n')
    return report


def main():
    p = argparse.ArgumentParser(__doc__)
    p.add_argument('--archive', required=True)
    p.add_argument('--output', required=True)
    args = p.parse_args()
    report = audit(args.archive, args.output)
    print(json.dumps(report, indent=2))
    return 2 if report['blockers'] else 0




def load_alpaca_diagnostics(repair_directory, archive):
    """Admit only source-reproducible raw bars to diagnostics. No replay authority.

    Reparse actual response bytes instead of trusting accepted-row certification
    labels. Corporate actions, adjusted prices and historical identity remain null.
    """
    from ga9.alpaca_repair import blocked_symbols, START, END
    root = Path(repair_directory).resolve()
    report = json.loads((root/'report.json').read_text())
    accepted = json.loads((root/'accepted_raw.json').read_text())
    blocked = blocked_symbols(archive)
    requests = {r.get('source_file'):r for r in report['requests'] if r.get('http_status')==200}
    rows=[]
    for candidate in accepted:
        ticker=candidate['ticker']; name=candidate['source_file']
        path=(root/name).resolve()
        if path.parent != root or ticker in blocked:
            raise ValueError('Quarantined symbol or source path')
        record=requests.get(name)
        if not record or digest(path)!=record['source_sha256'] or candidate['source_sha256']!=record['source_sha256']:
            raise ValueError('Unverified Alpaca response provenance')
        params=record['params']
        if record['endpoint']!='/v2/stocks/bars' or params['feed']!='sip' or params['adjustment']!='raw' or params['symbols']!=ticker or params['asof']=='-':
            raise ValueError('Invalid Alpaca raw request')
        payload=json.loads(path.read_text())
        matches=[b for b in payload['bars'].get(ticker,[]) if b['t']==candidate['t']]
        if len(matches)!=1 or any(matches[0][f]!=candidate[f] for f in ('o','h','l','c','v')):
            raise ValueError('Candidate differs from vendor response')
        day=pd.Timestamp(candidate['t']).tz_convert('America/New_York').date().isoformat()
        if day!=candidate['date'] or not START<=day<=END:
            raise ValueError('Invalid Alpaca session date')
        rows.append(dict(ticker=ticker,date=pd.Timestamp(day),open=candidate['o'], high=candidate['h'],
                         low=candidate['l'],close=candidate['c'],volume=candidate['v'],
                         adj_close=np.nan,dividends=np.nan,stock_splits=np.nan,
                         security_id=None,known_at=None,source_file=str(path),source_sha256=digest(path),
                         status='VENDOR_RAW_ONLY_NOT_REPLAY_CERTIFIED'))
    result=pd.DataFrame(rows)
    if len(result) and (result.duplicated(['ticker','date']).any() or bar_issues(result.assign(adj_close=result.close))['invalid_rows']):
        raise ValueError('Invalid or duplicate diagnostic bars')
    return result

if __name__ == '__main__':
    raise SystemExit(main())
