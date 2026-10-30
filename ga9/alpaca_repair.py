"""Bounded SIP repair evidence. Never authorizes replay or resolves identity by prices."""
import argparse
import hashlib
import json
import os
from pathlib import Path
from datetime import datetime, timezone
import urllib.request
import urllib.parse
import urllib.error
import pandas as pd

START, END = '2022-01-01', '2025-12-31'
PARTITION = Path(__file__).resolve().parents[1]/'Research/Partitions/MTS_V4_REPAIRED_UNTOUCHED_PARTITION_A100_B100_DISCOVERY136_20261007.json'


def credentials(path):
    cfg = {}
    if Path(path).is_file():
        for line in Path(path).read_text().splitlines():
            if '=' in line and not line.lstrip().startswith('#'):
                k, v = line.removeprefix('export ').strip().split('=', 1)
                cfg[k] = v.strip().strip('\"\'')
    cfg.update({k: v for k, v in os.environ.items() if k.startswith(('APCA_', 'ALPACA_'))})
    key = cfg.get('APCA_API_KEY_ID') or cfg.get('ALPACA_API_KEY')
    secret = cfg.get('APCA_API_SECRET_KEY') or cfg.get('ALPACA_SECRET_KEY')
    if not key or not secret:
        raise ValueError('Alpaca credential pair unavailable')
    return {'APCA-API-KEY-ID': key, 'APCA-API-SECRET-KEY': secret}


def blocked_symbols(archive):
    p = json.loads(PARTITION.read_text())
    blocked = {x['ticker'] for group in ('VERIFICATION_A', 'VERIFICATION_B') for x in p[group]}
    q = json.loads((Path(archive)/'protected_alias_quarantine_20261012.json').read_text())
    blocked.update(q['known_protected_aliases_in_eligible_universe'])
    identities = json.loads((Path(archive)/'identity_reconciliation_candidates_20261012.json').read_text())
    blocked.update(r['historical_symbol'] for r in identities['records'] if not r.get('allow_in_backtest', False))
    return blocked


def acquisition_quarantine(archive):
    """Protected issuers/aliases cannot be acquired; unresolved PIT is separate."""
    partition = json.loads(PARTITION.read_text())
    blocked = {x['ticker'] for group in ('VERIFICATION_A', 'VERIFICATION_B')
               for x in partition[group]}
    q = json.loads((Path(archive)/'protected_alias_quarantine_20261012.json').read_text())
    blocked.update(q['known_protected_aliases_in_eligible_universe'])
    blocked.update(q.get('direct_protected_raw_tickers', []))
    blocked.update(q.get('known_protected_aliases_in_raw', {}))
    return blocked


def reuse_benchmark(directory):
    """Reference existing SIP raw QQQ bytes without copying or new requests."""
    root = Path(directory).resolve()
    report = json.loads((root/'report.json').read_text())
    dates, sources = set(), []
    for record in report['requests']:
        params = record.get('params', {})
        if (record.get('http_status') != 200 or record['endpoint'] != '/v2/stocks/bars'
                or params.get('symbols') != 'QQQ' or params.get('feed') != 'sip'
                or params.get('adjustment') != 'raw' or params.get('asof') == '-'):
            continue
        path = (root/record['source_file']).resolve()
        if path.parent != root:
            raise ValueError('Invalid benchmark source path')
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != record['source_sha256']:
            raise ValueError('Benchmark source hash mismatch')
        for bar in json.loads(raw).get('bars', {}).get('QQQ', []):
            day = pd.Timestamp(bar['t']).tz_convert('America/New_York').date().isoformat()
            if START <= day <= END:
                dates.add(day)
        sources.append(dict(source_file=str(path), source_sha256=record['source_sha256']))
    if not dates:
        raise ValueError('No reusable QQQ SIP raw evidence')
    return dict(rows=len(dates), sources=sources, status='VENDOR_RAW_ONLY_NOT_PIT_CERTIFIED')


class Client:
    def __init__(self, output, headers, budget=240):
        self.output, self.headers, self.budget = Path(output), headers, budget
        self.requests = []

    def get(self, endpoint, params):
        if len(self.requests) >= self.budget:
            raise RuntimeError('Request budget exhausted')
        url = 'https://data.alpaca.markets'+endpoint+'?'+urllib.parse.urlencode(params)
        record = dict(endpoint=endpoint, params=params.copy(), retrieved_at=datetime.now(timezone.utc).isoformat())
        self.requests.append(record)
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=self.headers), timeout=20) as response:
                raw = response.read()
                record['http_status'] = response.status
            data = json.loads(raw)
            name = f'response_{len(self.requests):04d}.json'
            (self.output/name).write_bytes(raw)
            record.update(source_file=name, source_sha256=hashlib.sha256(raw).hexdigest())
            return data, record
        except urllib.error.HTTPError as exc:
            record.update(http_status=exc.code, error_type='HTTPError')
        except Exception as exc:
            # Exception messages and response bodies are deliberately not logged.
            record.update(error_type=type(exc).__name__)
            if isinstance(exc, urllib.error.URLError):
                record.update(reason_type=type(exc.reason).__name__, errno=getattr(exc.reason, 'errno', None))
        raise RuntimeError('Alpaca request failed; inspect sanitized request ledger')

    def pages(self, endpoint, params, max_pages=4):
        result, seen = [], set()
        params = params.copy()
        for _ in range(max_pages):
            data, record = self.get(endpoint, params)
            result.append((data, record))
            token = data.get('next_page_token')
            if not token:
                return result
            if token in seen:
                raise ValueError('Repeated pagination token')
            seen.add(token)
            params['page_token'] = token
        raise ValueError('Pagination bound reached: incomplete response excluded')


def bars(client, symbol, start, end, adjustment='raw', asof=None):
    if not START <= start <= end <= END:
        raise ValueError('Acquisition outside 2022-2025 bound')
    params = dict(symbols=symbol, start=start+'T00:00:00Z',
                  end=end+'T23:59:59Z', timeframe='1Day', feed='sip',
                  adjustment=adjustment, asof=asof or start, limit=10000, sort='asc')
    rows = []
    for data, record in client.pages('/v2/stocks/bars', params):
        if set(data.get('bars', {})) - {symbol}:
            raise ValueError('Unexpected response symbol')
        for bar in data.get('bars', {}).get(symbol, []):
            row = dict(bar, ticker=symbol, source_file=record['source_file'], source_sha256=record['source_sha256'])
            row['date'] = pd.Timestamp(bar['t']).tz_convert('America/New_York').date().isoformat()
            if not start <= row['date'] <= end:
                raise ValueError('Out-of-window bar')
            rows.append(row)
    d = pd.DataFrame(rows)
    if len(d):
        if d.duplicated(['ticker', 'date']).any():
            raise ValueError('Duplicate bars')
        for r in d.itertuples():
            import math
            if not all(math.isfinite(x) and x > 0 for x in (r.o, r.h, r.l, r.c)) or not math.isfinite(r.v) or r.v < 0 or r.h < max(r.o,r.l,r.c) or r.l > min(r.o,r.h,r.c):
                raise ValueError('Invalid OHLCV')
    return rows


def reconcile(variants):
    keyed = {k: {r['date']:r for r in rows} for k,rows in variants.items()}
    dates = set(keyed['raw'])
    if not dates or any(set(v) != dates for v in keyed.values()):
        return dict(status='INCOMPLETE_VARIANTS', rows=0)
    mismatch = sum(any(keyed['raw'][d][f] != keyed['unmapped'][d][f] for f in ('o','h','l','c','v')) for d in dates)
    ratios = []
    for d in sorted(dates):
        r = keyed['raw'][d]
        ratios.append(dict(date=d, split_close_factor=keyed['split'][d]['c']/r['c'],
                           split_volume_factor=keyed['split'][d]['v']/r['v'] if r['v'] else None,
                           dividend_close_factor=keyed['dividend'][d]['c']/r['c'],
                           all_close_factor=keyed['all'][d]['c']/r['c']))
    return dict(status='SYMBOL_MAPPING_MISMATCH' if mismatch else 'CONSISTENT_VENDOR_VARIANTS_NOT_IDENTITY_CERTIFIED',
                rows=len(dates), mapping_mismatches=mismatch, factors=ratios,
                actions_status='REQUIRES_EVENT_LEVEL_SPLIT_AND_DIVIDEND_RECONCILIATION')


def run(archive, gaps_path, output, credential_file, budget=240, max_symbols=20,
        reuse_qqq=None, max_dates=20):
    if not 1 <= budget <= 500 or not 1 <= max_symbols <= 30 or not 1 <= max_dates <= 252:
        raise ValueError('Invalid repair bounds')
    gaps = pd.read_csv(gaps_path, dtype={'ticker': str, 'date': str}).drop_duplicates(['ticker','date'])
    if not gaps.date.between(START, END).all():
        raise ValueError('Gap list outside acquisition bound')
    # Derive year from dates: a stale or absent year column must not hide gaps.
    parsed = pd.to_datetime(gaps.date, format='%Y-%m-%d', errors='raise')
    gaps['year'] = parsed.dt.year
    blocked = acquisition_quarantine(archive)
    admission_blocked = blocked_symbols(archive)
    eligible = gaps[~gaps.ticker.isin(blocked) & gaps.ticker.ne('QQQ')]
    report = dict(status='BLOCKED_NOT_PIT_CERTIFIED', acquisition_vendor='Alpaca', feed='sip',
                  baseline_gaps=len(gaps), eligible_stock_gaps=len(eligible),
                  skipped_quarantine=sorted(set(gaps.ticker)&blocked),
                  identity_deferred=sorted(set(eligible.ticker)&admission_blocked),
                  raw_recovered_gaps=0, certified_recovered_gaps=0, benchmark_rows=0,
                  accepted_raw_rows=0, work=[], replay_executed=False, long_GA_executed=False)
    output = Path(output); output.mkdir(parents=True, exist_ok=False)
    client = None; recovered = {}; accepted = []
    try:
        if reuse_qqq:
            report['reused_benchmark'] = reuse_benchmark(reuse_qqq)
            report['benchmark_rows'] = report['reused_benchmark']['rows']
        # Rank actual missing non-quarantined stock dates, deterministic on ties.
        counts = eligible.groupby('ticker').size().reset_index(name='gaps')
        symbols = counts.sort_values(['gaps','ticker'], ascending=[False,True]).head(max_symbols).ticker
        tasks = []
        for symbol in symbols:
            for year, group in eligible[eligible.ticker == symbol].groupby('year'):
                dates = sorted(group.date)
                for offset in range(0, len(dates), max_dates):
                    wanted = dates[offset:offset+max_dates]
                    tasks.append((symbol, int(year), wanted))
        report['planned_batches'] = len(tasks)
        if tasks:
            client = Client(output, credentials(credential_file), budget)
        for symbol, year, wanted in tasks:
            if len(client.requests) >= budget:
                report['budget_exhausted'] = True
                break
            start, end = wanted[0], wanted[-1]
            item = dict(ticker=symbol, year=year, start=start, end=end, requested_gap_dates=wanted)
            report['work'].append(item)
            try:
                raw = bars(client, symbol, start, end)
                found = [r for r in raw if r['date'] in wanted]
                item['observed_gap_bars'] = len(found)
                for row in found:
                    row.update(asof=start, feed='sip', adjustment='raw',
                               verified_scope='VENDOR_OHLCV_ONLY', security_id=None,
                               known_at=None, dividends=None, stock_splits=None, adj_close=None)
                    recovered[(symbol,row['date'])] = row
                    if symbol not in admission_blocked:
                        accepted.append(row)
            except (RuntimeError, ValueError) as exc:
                item['error_type'] = type(exc).__name__
                if client.requests and (client.requests[-1].get('http_status') in (401,403,429)
                                        or client.requests[-1].get('error_type') == 'URLError'):
                    break
    except (RuntimeError, ValueError) as exc:
        report['access_blocker'] = type(exc).__name__
    report['requests'] = client.requests if client else []
    report['raw_recovered_gaps'] = len(recovered)
    report['accepted_raw_rows'] = len(accepted)
    report['remaining_raw_gaps'] = len(gaps)-len(recovered)
    report['blockers'] = ['Historical identity, membership, actions and PIT gates remain unchanged']
    (output/'recovered_raw.json').write_text(json.dumps(list(recovered.values()),indent=2)+'\n')
    (output/'accepted_raw.json').write_text(json.dumps(accepted,indent=2)+'\n')
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


def main():
    p=argparse.ArgumentParser(__doc__)
    p.add_argument('--archive',required=True); p.add_argument('--gaps',required=True)
    p.add_argument('--output',required=True); p.add_argument('--credential-file',default='/root/.config/mts/alpaca.env')
    p.add_argument('--max-requests',type=int,default=240); p.add_argument('--max-symbols',type=int,default=20)
    p.add_argument('--reuse-qqq', help='Existing repair directory with hash-verified QQQ responses')
    p.add_argument('--max-dates', type=int, default=20, help='Missing dates per stock/year batch (1..252)')
    a=p.parse_args()
    if not 1<=a.max_requests<=500 or not 1<=a.max_symbols<=30 or not 1<=a.max_dates<=252: p.error('Bounds: 1..500 requests; 1..30 symbols')
    r=run(a.archive,a.gaps,a.output,a.credential_file,a.max_requests,a.max_symbols,a.reuse_qqq,a.max_dates)
    print(json.dumps({k:v for k,v in r.items() if k not in ('work','requests')},indent=2))
    return 2




def reconcile_declared_actions(variants, events, tolerance=0.002):
    """Check normalized declared actions against adjacent vendor factor changes.

    Events require type, ex_date, source_sha256, and old_rate/new_rate (split)
    or cash (dividend). Caller must separately verify vendor schema, event
    completeness, security identity, currency and historical announcement times.
    A successful numeric check never certifies PIT availability.
    """
    import math
    base=reconcile(variants)
    if base['status']!='CONSISTENT_VENDOR_VARIANTS_NOT_IDENTITY_CERTIFIED':
        return dict(status='BLOCKED_VARIANTS',checks=[])
    raw={r['date']:r for r in variants['raw']}
    factors={r['date']:r for r in base['factors']}
    dates=sorted(raw); checks=[]
    for event in events:
        day=event['ex_date']; earlier=[d for d in dates if d<day]
        check=dict(ex_date=day,type=event['type'],status='UNRESOLVED')
        checks.append(check)
        if day not in factors or not earlier or not event.get('source_sha256'):
            continue
        prev=earlier[-1]
        if event['type']=='split':
            old,new=float(event['old_rate']),float(event['new_rate'])
            if old<=0 or new<=0: continue
            expected=old/new
            observed=factors[prev]['split_close_factor']/factors[day]['split_close_factor']
            a,b=factors[prev]['split_volume_factor'],factors[day]['split_volume_factor']
            if a is None or b is None or b==0: continue
            volume_ok=math.isclose(a/b,1/expected,rel_tol=tolerance)
        elif event['type']=='cash_dividend':
            cash=float(event['cash'])
            if cash<0: continue
            expected=1-cash/raw[prev]['c']
            observed=factors[prev]['dividend_close_factor']/factors[day]['dividend_close_factor']
            volume_ok=True
        else: continue
        check.update(expected_factor=expected,observed_factor=observed,
                     status='NUMERIC_MATCH_ONLY' if math.isclose(expected,observed,rel_tol=tolerance) and volume_ok else 'MISMATCH')
    return dict(status='DIAGNOSTIC_NOT_PIT_CERTIFIED',checks=checks)

if __name__=='__main__': raise SystemExit(main())
