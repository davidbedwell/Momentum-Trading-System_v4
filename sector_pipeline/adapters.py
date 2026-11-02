"""Explicit source adapters. No automatic vendor substitution or credential logging."""
import csv
import datetime as dt
import json
import os
from pathlib import Path
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def local(path):
    p = Path(path).resolve()
    if not p.is_relative_to(ROOT) or any(x in p.relative_to(ROOT).parts for x in ('.git', '.aws', '.codex', '.agents', 'secrets')):
        raise ValueError('Data and outputs must remain in independent workspace, outside private directories')
    return p


def read_csv(path):
    with local(path).open(newline='') as f:
        return list(csv.DictReader(f))


def fetch(url, agent='IndependentSectorResearch/1.0'):
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': agent}), timeout=30) as r:
        data = json.load(r)
    if any(k in data for k in ('Error Message', 'Information', 'Note')):
        raise ValueError('Provider unavailable, rate limited, or entitlement missing')
    return data


def yahoo(symbol, start, end):
    stamp = lambda s: int(dt.datetime.fromisoformat(s).replace(tzinfo=dt.timezone.utc).timestamp())
    url = 'https://query1.finance.yahoo.com/v8/finance/chart/' + urllib.parse.quote(symbol, safe='') + '?' + urllib.parse.urlencode(dict(period1=stamp(start), period2=stamp(end), interval='1d', events='div,splits'))
    result = fetch(url, 'Mozilla/5.0')['chart']['result'][0]
    q = result['indicators']['quote'][0]
    a = result['indicators']['adjclose'][0]['adjclose']
    rows = []
    for i, ts in enumerate(result['timestamp']):
        if a[i] is None or q['close'][i] is None:
            continue
        factor = a[i] / q['close'][i]
        rows.append(dict(symbol=symbol, date=str(dt.datetime.fromtimestamp(ts, dt.timezone.utc).date()), adj_close=a[i], adj_open=q['open'][i]*factor if q['open'][i] else '', close=q['close'][i], volume=q['volume'][i], source='Yahoo provisional'))
    return rows


def sec_companyfacts(cik):
    agent = os.environ.get('SEC_USER_AGENT')
    if not agent:
        raise ValueError('Set SEC_USER_AGENT with contact information')
    return fetch(f'https://data.sec.gov/api/xbrl/companyfacts/CIK{int(cik):010d}.json', agent)


def sec_quality(data, asof, cutoff=None):
    facts = data.get('facts', {}).get('us-gaap', {})
    eligible = {}
    for tag in ('GrossProfit', 'Assets'):
        eligible[tag] = [r for r in facts.get(tag, {}).get('units', {}).get('USD', [])
                         if r.get('filed', '9999') < asof and available(r.get('available_at'), cutoff or asof+'T00:00:00+00:00') and r['end'] <= asof and r.get('form') in ('10-K', '10-Q', '10-K/A', '10-Q/A')]
    # Annual gross profit only; preserve period and filing vintage. No proxy for missing tags.
    gp = [r for r in eligible['GrossProfit'] if 'start' in r and 330 <= (dt.date.fromisoformat(r['end'])-dt.date.fromisoformat(r['start'])).days <= 380]
    for g in sorted(gp, key=lambda r: (r['end'], r['filed']), reverse=True):
        assets = [r for r in eligible['Assets'] if r['end'] == g['end'] and r['val'] > 0]
        if assets:
            a = max(assets, key=lambda r: r['filed'])
            return g['val']/a['val']
    return None


def alpha_earnings(symbol):
    key = os.environ.get('ALPHAVANTAGE_API_KEY')
    if not key:
        raise ValueError('ALPHAVANTAGE_API_KEY unavailable; earnings remain missing')
    return fetch('https://www.alphavantage.co/query?' + urllib.parse.urlencode(dict(function='EARNINGS', symbol=symbol, apikey=key)))


def earnings_signal(data, asof, cutoff=None):
    import statistics
    events = sorted([e for e in data.get('quarterlyEarnings', []) if e.get('reportedDate', '9999') < asof and available(e.get('available_at'), cutoff or asof+'T00:00:00+00:00')], key=lambda e: e['reportedDate'])
    # Standardize latest EPS error by prior eight errors; all eight prior observations required.
    def error(e):
        try:
            return float(e['reportedEPS']) - float(e['estimatedEPS'])
        except (ValueError, KeyError, TypeError):
            return None
    if not events or error(events[-1]) is None:
        return None
    prior = [error(e) for e in events[:-1][-8:]]
    if len(prior) != 8 or any(v is None for v in prior):
        return None
    sd = statistics.stdev(prior)
    return error(events[-1])/sd if sd else None


def fred(series, asof):
    key = os.environ.get('FRED_API_KEY')
    if not key:
        raise ValueError('FRED_API_KEY unavailable; regime remains missing')
    return fetch('https://api.stlouisfed.org/fred/series/observations?' + urllib.parse.urlencode(dict(series_id=series, api_key=key, file_type='json', realtime_start=asof, realtime_end=asof, observation_end=asof)))


def timestamp(value):
    parsed = dt.datetime.fromisoformat(value.replace('Z','+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('Availability timestamps require timezone')
    return parsed


def available(value, cutoff):
    # Legacy pure adapters accept absent timestamps; certified executor requires them.
    return value is None or timestamp(value) <= timestamp(cutoff)


def checkpoint_source(provider, request, cache):
    """Explicit resumable source operation. No fallback or automatic subscriptions.

    Intended for authorized source preparation; the research CLI never fetches data.
    """
    from .storage import resume_source
    loaders = {'sec':sec_companyfacts,'alpha':alpha_earnings,'yahoo':yahoo,'fred':fred}
    if provider not in loaders:
        raise ValueError('Unknown source provider')
    return resume_source(local(cache),provider,request,lambda:loaders[provider](**request))
