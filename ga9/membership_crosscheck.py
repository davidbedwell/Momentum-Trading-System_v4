"""Compare archived secondary rosters and dated official notice facts; no PIT certification."""
import argparse
import hashlib
import json
import re
from pathlib import Path
import pandas as pd


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def compare(archive, output):
    root=Path(archive); out=Path(output); out.mkdir(parents=True,exist_ok=False)
    primary=root/'sources/primary/src/nasdaq_100_ticker_history'
    cross=root/'sources/crosscheck/nasdaq100_components_history.csv'
    ledger=root/'primary_dated_membership_events.json'
    events=json.loads(ledger.read_text())['events']
    secondary=pd.read_csv(cross)
    inputs=[cross,ledger,Path(__file__).with_name('official_notice_facts_20261029.json')]
    states={}
    for year in range(2022,2026):
        path=primary/f'n100-ticker-changes-{year}.yaml'; inputs.append(path)
        # Only extract the explicit scalar baseline block; dated operations come
        # from the separately archived ledger. ON remains a string, never YAML bool.
        block=path.read_text().split('tickers_on_Jan_1:\n',1)[1].split('\nchanges:',1)[0]
        names=re.findall(r'^  - ([A-Z][A-Z0-9.\-]*)\s*$',block,re.M)
        if not names or len(names)!=len(set(names)): raise ValueError('Invalid annual baseline')
        states[year]=set(names)
    def roster(date):
        current=states[int(date[:4])].copy()
        for e in sorted(events,key=lambda e:e['date']):
            if date[:4]+'-01-01'<=e['date']<=date:
                if e['action']=='ADD': current.add(e['ticker'])
                else: current.discard(e['ticker'])
        return current
    dates=sorted({'2022-01-01','2023-01-01','2024-01-01','2025-01-01'} |
                 {e['date'] for e in events if '2022-01-01'<=e['date']<='2025-12-31'} |
                 set(secondary[secondary.date.between('2022-01-01','2025-12-31')].date))
    comparisons=[]
    for date in dates:
        available=secondary[secondary.date<=date]
        if available.empty: raise ValueError('Missing secondary baseline')
        other=set(available.iloc[-1].tickers.split(',')); first=roster(date)
        comparisons.append(dict(date=date, primary_only=sorted(first-other),secondary_only=sorted(other-first),
                                exact=first==other,known_at=None,security_id=None))
    notices=json.loads((Path(__file__).with_name('official_notice_facts_20261029.json')).read_text())
    checks=[]
    for n in notices:
        for action in ('ADD','REMOVE'):
            asserted={e['ticker'] for e in events if e['date']==n['effective_date'] and e['action']==action}
            expected=set(n[action])
            checks.append(dict(source_url=n['source_url'],effective_date=n['effective_date'],
                               announced_at=n['announced_at'],known_at=n['known_at'], action=action,
                               official=sorted(expected),missing_from_primary=sorted(expected-asserted),
                               extra_on_effective_date=sorted(asserted-expected),
                               scope=n['scope']))
    report=dict(status='UNVERIFIED_SECONDARY_COMPARISON', comparisons=comparisons,official_checks=checks,
                exact_roster_dates=sum(x['exact'] for x in comparisons),compared_dates=len(comparisons),
                provenance=[dict(path=str(p),sha256=sha(p)) for p in inputs],
                source_urls=['https://github.com/jmccarrell/n100tickers','https://github.com/thuningxu/sp500nq100'],
                limitation='Agreement is not independent PIT proof. Official notices cover selected events only; stable IDs and starting roster remain unverified.')
    (out/'crosscheck.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(__doc__);p.add_argument('--archive',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();r=compare(a.archive,a.output);print(json.dumps({k:r[k] for k in ('status','exact_roster_dates','compared_dates')},indent=2))
