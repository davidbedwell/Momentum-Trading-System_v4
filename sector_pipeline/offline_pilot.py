"""Authorized contaminated-2019 cache pilot; never calls certified execution/gates."""
import csv, json, hashlib, statistics, datetime
from pathlib import Path
from collections import defaultdict
import pandas as pd
import subprocess
from . import core
from .executor import lookahead

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/offline-provisional-2019'
CACHE=Path('/opt/mts/ga6_h/data/prices')

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def writecsv(name, rows):
    if rows:
        with (OUT/name).open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=sorted({k for r in rows for k in r}));w.writeheader();w.writerows(rows)

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    seal=sha(ROOT/'manifest.json')
    source=ROOT/'universe_2019/membership_2019_source.yaml'
    data=json.loads(subprocess.check_output(['/usr/bin/python3','-c','import sys,json,yaml; print(json.dumps(yaml.safe_load(sys.stdin.read())))'],input=source.read_bytes()))
    active={s:'2019-01-01' for s in data['tickers_on_Jan_1']}; inventory=[]; anomalies=[]
    for date,event in sorted(data['changes'].items()):
        for s in event.get('difference',[]):
            if s in active: inventory.append(dict(symbol=s,start=active.pop(s),end=date))
            else: anomalies.append(dict(date=date,symbol=s,issue='removal absent from active set'))
        for s in event.get('union',[]):
            if s in active: anomalies.append(dict(date=date,symbol=s,issue='addition already active'))
            else: active[s]=date
    inventory.extend(dict(symbol=s,start=d,end='2020-01-01') for s,d in active.items())
    # Existing labels are evidence of an earlier pilot assignment, not historical GICS.
    labels={r['symbol']:r['sector'] for r in csv.DictReader((ROOT/'pilot_2019_sample.csv').open())}
    for m in inventory: m['sector']=labels.get(m['symbol'],'UNKNOWN')
    prices={}; evidence=[]; missing=[]; invalid=[]
    for s in sorted({m['symbol'] for m in inventory}):
        p=CACHE/(s+'.parquet')
        if not p.exists(): missing.append(s);continue
        # Read no formations/outcomes outside the explicitly authorized contaminated 2019 pilot.
        d=pd.read_parquet(p,filters=[('date','>=',pd.Timestamp('2017-01-01')),('date','<',pd.Timestamp('2020-01-01'))])
        records=[]
        for r in d.to_dict('records'):
            vals=[r.get(k) for k in ('Open','Close','Adj Close')]
            if any(v is None or not pd.notna(v) or v<=0 for v in vals):
                invalid.append(dict(symbol=s,date=str(r['date']),issue='missing/nonpositive OHLC adjustment input'));continue
            records.append(dict(symbol=s,date=str(pd.Timestamp(r['date']).date()),adj_close=float(r['Adj Close']),adj_open=float(r['Open']*r['Adj Close']/r['Close']),source='existing Yahoo-style adjusted OHLC cache; provisional'))
        records.sort(key=lambda r:r['date'])
        if records:
            prices[s]=records
            evidence.append(dict(symbol=s,path=str(p),sha256=sha(p),rows_used=len(records),first=records[0]['date'],last=records[-1]['date']))
        else: missing.append(s)
    writecsv('prices_used.csv',[r for v in prices.values() for r in v]);writecsv('membership_used.csv',inventory)
    earnings={p.stem:json.loads(p.read_text()) for p in (ROOT/'earnings_cache').glob('*.json')}
    rows=core.form_rows(prices,inventory,[2019],{},earnings)
    writecsv('observations.csv',rows)
    chosen=[dict(r) for r in rows if r['sector']!='UNKNOWN']
    groups=defaultdict(list)
    for r in chosen: groups[r['asof'],r['sector'],r['horizon']].append(r)
    for g in groups.values():
        median=statistics.median(r['forward_return'] for r in g)
        for r in g:r['excess']=r['forward_return']-median
    monthly,summary=core.metrics(chosen)
    for key,value in summary.items():
        signal,h=key.split('_');value['placebo']=core.placebo(chosen,signal,int(h))
        value['certified_pass']=False
    writecsv('monthly_metrics.csv',monthly)
    sessions=sorted({r['date'] for v in prices.values() for r in v});months={d[:7]:d for d in sessions if d.startswith('2019')}
    coverage=[]
    for t in months.values():
        expected={m['symbol'] for m in inventory if m['start']<=t<m['end']}
        present={s for s,v in prices.items() if any(r['date']==t for r in v)}&expected
        coverage.append(dict(asof=t,expected_members=len(expected),priced=len(present),missing_symbols=sorted(expected-present),unknown_sector=len(expected-set(labels)),outcomes={str(h):sum(r['asof']==t and r['horizon']==h for r in rows) for h in (1,3,6)},known_sector_signal_rows={s:sum(r['asof']==t and r['horizon']==1 and r[s+'_rank'] is not None for r in chosen) for s in core.SIGNALS}))
    report=dict(status='COMPLETED PROVISIONAL contaminated-2019 offline pilot',finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),stage2='SEALED; no certified executor or ledger invoked',certified=False,manifest_sha256_before=seal,manifest_sha256_after=sha(ROOT/'manifest.json'),membership_source_sha256=sha(source),sector_source_sha256=sha(ROOT/'pilot_2019_sample.csv'),membership_intervals=len(inventory),unique_members=len({m['symbol'] for m in inventory}),cached_symbols=len(prices),price_rows=sum(map(len,prices.values())),missing_cache_symbols=missing,invalid_price_rows=invalid,membership_anomalies=anomalies,coverage=coverage,known_sector_symbols=sorted(set(labels)&set(prices)),earnings_cache_symbols=sorted(earnings),source_evidence=evidence,earnings_evidence=[dict(path=str(p.relative_to(ROOT)),sha256=sha(p)) for p in (ROOT/'earnings_cache').glob('*.json')],summary=summary,lookahead=lookahead(chosen),limitations=['2019 is previously contaminated and cannot test Stage1 or release Stage2.','Third-party local membership reconstruction is unverified; no historical membership invented.','Only 15 legacy sample sector labels exist; unverified historical proxies, no full-sector GICS coverage. UNKNOWN excluded.','Available-stock sector median sensitivity, not full-membership sector benchmark; legacy 15-stock sample was outcome-selected.','H4 unavailable: no SEC as-filed cache. H6 unavailable: requires all four original components.','H3 uses actual cached prior eight surprises and reported date+1; retrieval vintage is retrospective.','Price caches are retrospective and survivorship/identity/action provenance unverified. No ticker alias substitution.','No 2020 outcomes read; 1/3/6m right-censored. Month ends derive from observed cache sessions.','Five-stock sectors cannot form both exact top and bottom deciles; unavailable spread/turnover/cost metrics remain null.','No certified passers; frozen 2006-2015 chronological blocks unavailable.'],network=dict(web_tool='SUCCESS: official Wikipedia page accessible using permitted web.run',url='https://en.wikipedia.org/wiki/List_of_S%26P_500_companies',runtime_policy='environment_status tool unavailable; /etc/codex/network-policy.json absent',used_for_offline_pilot=False))
    report['sample_sizes']={f'{signal}_{h}':dict(stock_outcome_rows=sum(r['horizon']==h and r[signal+'_rank'] is not None for r in chosen),symbols=len({r['symbol'] for r in chosen if r['horizon']==h and r[signal+'_rank'] is not None}),sectors=len({r['sector'] for r in chosen if r['horizon']==h and r[signal+'_rank'] is not None})) for signal in core.SIGNALS for h in (1,3,6)}
    (OUT/'report.json').write_text(json.dumps(report,indent=2,allow_nan=False))
    print(json.dumps({k:report[k] for k in ('status','unique_members','cached_symbols','price_rows','known_sector_symbols')}),flush=True)
    for k,v in summary.items():print(k,json.dumps(v),flush=True)
    assert seal==sha(ROOT/'manifest.json')

if __name__=='__main__':run()
