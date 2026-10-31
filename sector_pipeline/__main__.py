import argparse
import csv
import hashlib
import json
from collections import defaultdict
from .adapters import ROOT, local, read_csv, yahoo, sec_companyfacts, alpha_earnings, fred
from .core import form_rows, metrics, price_issues


def write_csv(path, rows):
    with path.open('w', newline='') as f:
        if rows:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)


def main():
    p = argparse.ArgumentParser(description='Independent exploratory sector research; blind evaluation locked')
    sub = p.add_subparsers(dest='command', required=True)
    smoke = sub.add_parser('smoke')
    smoke.add_argument('--symbols', type=int, default=6)
    smoke.add_argument('--out', default='reports/smoke')
    run = sub.add_parser('run')
    run.add_argument('--prices', required=True)
    run.add_argument('--members', required=True)
    run.add_argument('--years', default='2019')
    run.add_argument('--fundamentals', help='JSON mapping stable symbols to SEC companyfacts')
    run.add_argument('--earnings', help='JSON mapping stable symbols to Alpha Vantage EARNINGS')
    run.add_argument('--out', default='reports/run')
    source = sub.add_parser('fetch')
    source.add_argument('provider', choices=['sec','alpha','fred'])
    source.add_argument('identifier')
    source.add_argument('--asof')
    source.add_argument('--out', required=True)
    args = p.parse_args()
    if args.command == 'fetch':
        if args.provider == 'fred' and not args.asof:
            p.error('FRED requires --asof vintage date')
        data = sec_companyfacts(args.identifier) if args.provider=='sec' else alpha_earnings(args.identifier) if args.provider=='alpha' else fred(args.identifier,args.asof)
        local(args.out).write_text(json.dumps(data))
        return
    manifest_bytes = (ROOT/'manifest.json').read_bytes()
    manifest = json.loads(manifest_bytes)
    out = local(args.out)
    out.mkdir(parents=True, exist_ok=True)
    failures = []
    if args.command == 'smoke':
        sample = read_csv(ROOT/'pilot_2019_sample.csv')[:args.symbols]
        prices = []
        for r in sample:
            try:
                prices.extend(yahoo(r['symbol'],'2017-01-01','2020-08-01'))
            except Exception as e:
                failures.append(dict(symbol=r['symbol'], error=type(e).__name__))
        write_csv(out/'prices.csv', prices)
        members = [dict(symbol=r['symbol'],sector=r['sector'],start='2019-01-01',end='2020-01-01',source='existing outcome-selected pilot; provisional') for r in sample]
        write_csv(out/'members.csv',members)
        years, fundamentals, earnings = [2019], {}, {}
    else:
        years = [int(y) for y in args.years.split(',')]
        if set(years)&set(manifest['blind']):
            p.error('Blind years are locked. Separate reviewed protocol change required before release.')
        if not set(years) <= set(manifest['discovery']+manifest['exploratory']+manifest['crash_separate']):
            p.error('Year not frozen in manifest')
        prices, members = read_csv(args.prices), read_csv(args.members)
        fundamentals = json.loads(local(args.fundamentals).read_text()) if args.fundamentals else {}
        earnings = json.loads(local(args.earnings).read_text()) if args.earnings else {}
    grouped = defaultdict(list)
    seen = set()
    for r in prices:
        key = r['symbol'],r['date']
        if key in seen or float(r['adj_close']) <= 0:
            raise ValueError('Duplicate or nonpositive price')
        seen.add(key)
        grouped[r['symbol']].append(r)
    for g in grouped.values():
        g.sort(key=lambda r:r['date'])
    for i,m in enumerate(members):
        for n in members[i+1:]:
            if m['symbol']==n['symbol'] and max(m['start'],n['start'])<min(m['end'],n['end']):
                raise ValueError('Overlapping membership/sector identity intervals')
    rows = form_rows(grouped,members,years,fundamentals,earnings)
    monthly, summary = metrics(rows)
    write_csv(out/'observations.csv',rows)
    write_csv(out/'monthly_metrics.csv',monthly)
    issues = price_issues(grouped)
    write_csv(out/'price_diagnostics.csv',issues)
    report = dict(status='exploratory incomplete' if rows else 'incomplete: no evaluable rows', predictive_claim=False, manifest_sha256=hashlib.sha256(manifest_bytes).hexdigest(), years=years, sources=['PIT constituent intervals: supplied/provisional pilot', 'Yahoo historical adjusted OHLCV: provisional', 'SEC companyfacts filed dates', 'Alpha Vantage reported dates', 'FRED vintage adapter'], analyst_revisions='unavailable; not assumed free; excluded', price_rows=len(prices), observations=len(rows), failures=failures, price_issues=len(issues), limitations=['PIT constituent and sector certification missing', 'Delisting returns unavailable; survivor/selection bias', 'Yahoo adjustment history provisional; no trading claim', 'H4/H5 missing unless explicitly supplied', 'FRED regime fetched separately; no regime inference without vintage input', 'HAC normal approximation; small samples descriptive only', 'Unresolved price gaps diagnosed, not repaired'], summary=summary)
    (out/'report.json').write_text(json.dumps(report,indent=2,allow_nan=False))
    print(json.dumps({k:report[k] for k in ('status','price_rows','observations','failures')},indent=2))
    if not rows:
        raise SystemExit(2)


if __name__ == '__main__':
    main()
