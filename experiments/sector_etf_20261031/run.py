#!/usr/bin/env python3
"""Bounded free-data acquisition gate. No research outcomes without usable data.

Exit 2 = data blocked; exit 3 = data acquired, analysis deliberately not resumed.
A later successful acquisition requires completion of the frozen analysis, never
an automatic claim of a finished experiment. Standard library only.
"""
import argparse
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
import socket
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parent
SECTORS = 'XLB XLE XLF XLI XLK XLP XLU XLV XLY XLRE XLC'.split()
INCEPTION = {s: '1998-12-16' for s in SECTORS}
INCEPTION.update(XLRE='2015-10-07', XLC='2018-06-18', SPY='1993-01-22', SGOV='2020-05-26')
SYMBOLS = SECTORS + ['SPY', 'SGOV']


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_protocol(root=ROOT):
    lock = json.loads((root / 'preregistration.lock.json').read_text())
    if digest(root / 'PREREGISTRATION.md') != lock['sha256']:
        raise ValueError('Frozen preregistration hash mismatch')
    return lock


def parse_chart(payload, symbol):
    """Accept only explicit adjusted close; reject invented pre-inception history."""
    result = payload['chart']['result'][0]
    prices = result['indicators']['adjclose'][0]['adjclose']
    times = result['timestamp']
    if len(prices) != len(times):
        raise ValueError('Mismatched dates/prices')
    rows = []
    for timestamp, price in zip(times, prices):
        day = dt.datetime.fromtimestamp(timestamp, dt.timezone.utc).date().isoformat()
        if day < INCEPTION[symbol]:
            raise ValueError(f'{symbol}: pre-inception observation')
        if day > '2025-12-31':
            continue
        if price is None:
            continue
        if not math.isfinite(price) or price <= 0:
            raise ValueError('Invalid adjusted price')
        rows.append({'date': day, 'symbol': symbol, 'adjusted_close': price})
    if not rows or len({r['date'] for r in rows}) != len(rows):
        raise ValueError('Empty or duplicated daily data')
    if rows != sorted(rows, key=lambda r: r['date']):
        raise ValueError('Dates not increasing')
    return rows


def chart_url(host, symbol):
    params = urllib.parse.urlencode(dict(period1=725846400, period2=1767225600,
                                        interval='1d', includeAdjustedClose='true', events='div,splits'))
    return f'https://{host}/v8/finance/chart/{symbol}?{params}'


def acquire(root=ROOT, timeout=8):
    lock = verify_protocol(root)
    out = root / 'outputs'
    out.mkdir(exist_ok=True)
    raw = root / 'data' / 'raw'
    raw.mkdir(parents=True, exist_ok=True)
    evidence = {'started_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
                'protocol_sha256': lock['sha256'], 'sources': [],
                'status': 'BLOCKED_DATA', 'outcomes_computed': False,
                'validation_opened': False, 'paid_requests': 0}
    acquired = {}
    for host in ['query1.finance.yahoo.com', 'query2.finance.yahoo.com']:
        record = {'host': host, 'url': chart_url(host, 'SPY')}
        evidence['sources'].append(record)
        try:
            # DNS check is recorded so an unavailable host does not trigger 13 retries.
            socket.getaddrinfo(host, 443)
            for symbol in SYMBOLS:
                url = chart_url(host, symbol)
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=timeout) as response:
                    content = response.read()
                payload = json.loads(content)
                rows = parse_chart(payload, symbol)
                path = raw / f'{symbol}.json'
                path.write_bytes(content)
                acquired[symbol] = {'rows': len(rows), 'sha256': digest(path), 'source_url': url}
            record['status'] = 'downloaded'
            break
        except (OSError, ValueError, KeyError, IndexError, TypeError) as exc:
            record.update(status='failed', error_type=type(exc).__name__, error=str(exc))
    # Stooq is only a connectivity diagnostic; no unverified adjustment is accepted.
    try:
        socket.getaddrinfo('stooq.com', 443)
        evidence['stooq_connectivity'] = 'DNS resolved; not used as adjusted-price source'
    except OSError as exc:
        evidence['stooq_connectivity'] = f'{type(exc).__name__}: {exc}'
    evidence['acquired'] = acquired
    if set(acquired) == set(SYMBOLS):
        evidence['status'] = 'ACQUIRED_NOT_ANALYZED'
    evidence['ended_utc'] = dt.datetime.now(dt.timezone.utc).isoformat()
    (out / 'acquisition.json').write_text(json.dumps(evidence, indent=2) + '\n')
    print(json.dumps(evidence, indent=2))
    return 3 if evidence['status'] == 'ACQUIRED_NOT_ANALYZED' else 2


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--timeout', type=float, default=8)
    args = parser.parse_args()
    raise SystemExit(acquire(timeout=args.timeout))
