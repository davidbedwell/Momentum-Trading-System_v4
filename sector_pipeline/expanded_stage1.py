"""Free dated-holdings Stage1 sensitivity; no certified execution or Stage2 access."""
import csv
import datetime as dt
import hashlib
import json
import statistics as st
import subprocess
from collections import defaultdict
from pathlib import Path
import numpy as np
import pandas as pd
from . import core
from .executor import lookahead

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'reports/expanded-stage1'
CACHE = Path('/opt/mts/thunder-migration/mts-v4-market-store-RECONSTRUCTED-20261004/raw_yfinance')
SECTORS = {'Information Technology', 'Consumer Discretionary', 'Consumer Staples',
           'Financials', 'Health Care', 'Industrials', 'Energy', 'Materials', 'Utilities',
           'Telecommunication Services', 'Telecommunications'}

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def writecsv(path, rows):
    if not rows:
        path.write_text(''); return
    with path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=sorted({k for r in rows for k in r}))
        w.writeheader(); w.writerows(rows)

def sector_label(value):
    # Only spelling harmonization of the historical telecom sector, never 2018 GICS backfill.
    if value == 'Telecommunications': return 'Telecommunication Services'
    return value if value in SECTORS else 'UNKNOWN'

def annual_members(sources):
    result = {}; anomalies = []; previous = None
    for year in range(2006, 2016):
        p = sources / f'membership_{year}.yaml'
        data = json.loads(subprocess.check_output(['/usr/bin/python3', '-c',
            'import sys,json,yaml; print(json.dumps(yaml.safe_load(sys.stdin.read())))'], input=p.read_bytes()))
        active = set(data['tickers_on_Jan_1'])
        if previous is not None and active != previous:
            anomalies.append(dict(year=year, issue='annual boundary disagreement',
                                  added=sorted(active-previous), removed=sorted(previous-active)))
        events = sorted((str(d), e) for d,e in data.get('changes', {}).items())
        for month in range(1,13):
            end = core.add_months(f'{year}-{month:02d}-01', 0)
            for date,event in events:
                if date[:7] == end[:7] and date <= end:
                    for s in event.get('difference', []):
                        if s not in active: anomalies.append(dict(date=date,symbol=s,issue='absent removal'))
                        active.discard(s)
                    for s in event.get('union', []):
                        if s in active: anomalies.append(dict(date=date,symbol=s,issue='duplicate addition'))
                        active.add(s)
            result[end[:7]] = set(active)
        previous = active
    return result, anomalies

def load_members(sources):
    annual, anomalies = annual_members(sources)
    historical = []; proxy = []; snapshot = []; rejected = []
    bysymbol = defaultdict(set)
    for r in csv.DictReader((sources/'components_history.csv').open()):
        bysymbol[r['symbol']].add(r['cik'])
    ambiguous = {s for s,ciks in bysymbol.items() if len(ciks)>1}
    for p in sorted(sources.glob('ishares_*.csv')):
        rows = list(csv.DictReader(p.open())); date = rows[0]['date']
        assert '2006-01-01' <= date <= '2015-12-31'
        assert all(r['date']==date for r in rows)
        seen = set(); equities = []
        for r in rows:
            if r['asset_class'] != 'Equity': continue
            s = r['symbol']
            if s in seen:
                rejected.append(dict(asof=date,symbol=s,reason='duplicate snapshot symbol')); continue
            seen.add(s)
            label = sector_label(r['sector'])
            m = dict(symbol=s,start=date,end=str(dt.date.fromisoformat(date)+dt.timedelta(days=1)),
                     sector=label,sector_raw=r['sector'],sector_evidence_date=date,
                     source_file=p.name,source_sha256=sha(p),identity_cusip=r['CUSIP'],identity_isin=r['ISIN'],
                     source_name=r['name'],membership_evidence='dated iShares S&P500 tracker equity holding; index proxy',
                     historical_availability='dated retrospective vendor snapshot; publication timestamp unverified',
                     annual_membership_corroborated=s in annual[date[:7]])
            if s in ambiguous:
                m['sector']='UNKNOWN'
                rejected.append(dict(asof=date,symbol=s,reason='multiple CIKs in free history; cached ticker identity unresolved'))
            historical.append(m); equities.append(m)
        snapshot.append(dict(asof=date,equity_holdings=len(equities),known_sector=sum(m['sector']!='UNKNOWN' for m in equities),
                             annual_members=len(annual[date[:7]]),holdings_only=sorted(seen-annual[date[:7]]),
                             annual_only=sorted(annual[date[:7]]-seen)))
    return historical, snapshot, rejected, anomalies, sorted(ambiguous)

def compact_members(members):
    """Reduce redundant daily snapshot intervals; assert identical monthly universes."""
    bysymbol=defaultdict(list)
    for m in members: bysymbol[m['symbol']].append(m)
    result=[]
    for symbol,group in sorted(bysymbol.items()):
        previous=None
        for m in sorted(group,key=lambda x:x['start']):
            if (previous is not None and previous['sector']==m['sector']
                and core.add_months(previous['last_snapshot'],1)[:7]==m['start'][:7]):
                previous['end']=m['end']; previous['last_snapshot']=m['start']
            else:
                previous=dict(symbol=symbol,sector=m['sector'],start=m['start'],end=m['end'],last_snapshot=m['start'])
                result.append(previous)
    for date in sorted({m['start'] for m in members}):
        original=sorted((m['symbol'],m['sector']) for m in members if m['start']<=date<m['end'])
        compact=sorted((m['symbol'],m['sector']) for m in result if m['start']<=date<m['end'])
        assert original==compact, date
    print('equivalent monthly membership intervals',len(members),'->',len(result),flush=True)
    return result

def fast_placebo(rows, signal, horizon, seed=0):
    """Same permutation statistic as core.placebo; NumPy batches 1000 independent shuffles."""
    groups=defaultdict(list)
    for r in rows:
        if r['horizon']==horizon and r[signal+'_rank'] is not None and r['excess'] is not None:
            groups[r['asof'],r['sector']].append(r)
    prepared=[]
    for (date,_),g in sorted(groups.items()):
        x=np.array(core.ranks([r[signal+'_rank'] for r in g])); y=np.array(core.ranks([r['excess'] for r in g]))
        if len(x)<3: continue
        x-=x.mean(); y-=y.mean(); den=np.linalg.norm(x)*np.linalg.norm(y)
        if den: prepared.append((date,x,y,den))
    if not prepared: return dict(real=None,percentile99=None,passed=False,shuffles=0,seed=seed,status='undefined IC; no valid permutation statistic')
    rng=np.random.default_rng(seed); monthly=defaultdict(list); real=defaultdict(list)
    direction=-1 if signal=='H5' else 1
    for date,x,y,den in prepared:
        # Each row is a uniform permutation, independently within this sector-month.
        permutations=rng.permuted(np.broadcast_to(y,(1000,len(y))),axis=1)
        monthly[date].append(np.einsum('ij,j->i',permutations,x)/den*direction)
        real[date].append(float(np.dot(x,y)/den*direction))
    null=np.sort(np.mean([np.mean(v,axis=0) for v in monthly.values()],axis=0))
    actual=st.mean(st.mean(v) for v in real.values()); cutoff=float(null[989])
    return dict(real=actual,percentile99=cutoff,passed=actual>cutoff,shuffles=1000,seed=seed,
                rng='numpy default_rng PCG64; independent uniform permutations',null_sha256=hashlib.sha256(null.tobytes()).hexdigest())

def evaluate(name, rows):
    folder=OUT/name; folder.mkdir(exist_ok=True)
    chosen=[dict(r) for r in rows if r['sector']!='UNKNOWN']
    groups=defaultdict(list)
    strict=sum(r['excess'] is not None for r in chosen)
    for r in chosen: groups[r['asof'],r['sector'],r['horizon']].append(r)
    for g in groups.values():
        median=st.median(r['forward_return'] for r in g)
        for r in g: r['excess']=r['forward_return']-median
    monthly, summary=core.metrics(chosen)
    samples={}
    for key,value in summary.items():
        signal,h=key.split('_'); h=int(h)
        value['placebo']=fast_placebo(chosen,signal,h)
        direction=-1 if signal=='H5' else 1
        value['direction_oriented_mean']=None if value['mean'] is None else value['mean']*direction
        value['direction_oriented_t']=None if value['t'] is None else value['t']*direction
        value['certified_pass']=False
        g=[r for r in chosen if r['horizon']==h and r[signal+'_rank'] is not None]
        dates=sorted({r['asof'] for r in monthly if r['signal']==signal and r['horizon']==h and r['ic'] is not None})
        samples[key]=dict(stock_outcome_rows=len(g),symbols=len({r['symbol'] for r in g}),sectors=len({r['sector'] for r in g}),
                          first_ic=dates[0] if dates else None,last_ic=dates[-1] if dates else None,
                          block_months=[sum(lo<=int(d[:4])<=hi for d in dates) for lo,hi in ((2006,2008),(2009,2010),(2011,2013),(2014,2015))])
        agg={}
        for metric in ('spread','turnover','net_spread_15bps'):
            bydate=defaultdict(list)
            for r in monthly:
                if r['signal']==signal and r['horizon']==h and r[metric] is not None: bydate[r['asof']].append(r[metric])
            agg[metric]=dict(months=len(bydate),mean=st.mean(st.mean(v) for v in bydate.values()) if bydate else None)
        value['portfolio_diagnostics']=agg
        print(name,key,'IC',value['mean'],'months',value['n'],'placebos',value['placebo']['shuffles'],flush=True)
    writecsv(folder/'monthly_metrics.csv',monthly)
    writecsv(folder/'summary.csv',[dict(test=k,**{kk:vv for kk,vv in v.items() if not isinstance(vv,dict)},**samples[k]) for k,v in summary.items()])
    pd.DataFrame(chosen).to_parquet(folder/'observations.parquet',index=False)
    return dict(summary=summary,sample_sizes=samples,strict_full_holdings_benchmark_rows=strict,
                available_stock_benchmark_rows=len(chosen),lookahead=lookahead(chosen))

def run():
    OUT.mkdir(exist_ok=True); sources=OUT/'sources'
    protected=['manifest.json','CONTROLLING_PROTOCOL_V2.md','RESEARCH_PROTOCOL.md','sector_pipeline/core.py','sector_pipeline/executor.py','sector_pipeline/gate.py']
    before={p:sha(ROOT/p) for p in protected}
    members,snapshots,rejected,anomalies,ambiguous=load_members(sources)
    writecsv(OUT/'membership_used.csv',members);writecsv(OUT/'snapshot_coverage.csv',snapshots)
    writecsv(OUT/'identity_exclusions.csv',rejected)
    universe=sorted({m['symbol'] for m in members});prices={};evidence=[];missing=[];invalid=[]
    for s in universe:
        p=CACHE/(s+'.parquet')
        if not p.exists(): missing.append(s);continue
        # Pushdown filter: no 2016+ price or outcome rows are loaded.
        d=pd.read_parquet(p,filters=[('date','>=',pd.Timestamp('2004-01-01')),('date','<=',pd.Timestamp('2015-12-31'))])
        d=d.rename(columns={'open':'Open','close':'Close','adj_close':'Adj Close'})
        records=[]
        for r in d.to_dict('records'):
            vals=[r.get(k) for k in ('Open','Close','Adj Close')]
            if any(v is None or not pd.notna(v) or v<=0 for v in vals):
                invalid.append(dict(symbol=s,date=str(r['date']),reason='missing/nonpositive OHLC adjustment input'));continue
            records.append(dict(symbol=s,date=str(pd.Timestamp(r['date']).date()),adj_close=float(r['Adj Close']),
                                adj_open=float(r['Open']*r['Adj Close']/r['Close'])))
        records.sort(key=lambda r:r['date'])
        if not records: missing.append(s);continue
        assert len({r['date'] for r in records})==len(records)
        prices[s]=records;evidence.append(dict(symbol=s,path=str(p),sha256=sha(p),rows_used=len(records),first=records[0]['date'],last=records[-1]['date']))
    print('loaded',len(prices),'priced symbols',sum(map(len,prices.values())),'price rows',flush=True)
    pd.DataFrame([r for v in prices.values() for r in v]).to_parquet(OUT/'prices_used.parquet',index=False)
    earnings={p.stem:json.loads(p.read_text()) for p in (ROOT/'earnings_cache').glob('*.json')}
    rows=core.form_rows(prices,compact_members(members),list(range(2006,2016)),{},earnings)
    print('formed',len(rows),'outcome rows',flush=True)
    coverage=[]
    for snap in snapshots:
        date=snap['asof']; expected=[m for m in members if m['start']==date]
        present={s for s in prices if any(r['date']==date for r in prices[s])}
        coverage.append(dict(asof=date,expected_holdings=len(expected),priced=sum(m['symbol'] in present for m in expected),
             known_sector=sum(m['sector']!='UNKNOWN' for m in expected),unknown_sector=sum(m['sector']=='UNKNOWN' for m in expected),
             priced_known_sector=sum(m['symbol'] in present and m['sector']!='UNKNOWN' for m in expected),
             missing_symbols=[m['symbol'] for m in expected if m['symbol'] not in present],
             outcomes={str(h):sum(r['asof']==date and r['horizon']==h for r in rows) for h in (1,3,6)},
             signal_rows={sig:sum(r['asof']==date and r['horizon']==1 and r['sector']!='UNKNOWN' and r[sig+'_rank'] is not None for r in rows) for sig in core.SIGNALS}))
    (OUT/'coverage.json').write_text(json.dumps(coverage,indent=2))
    scenarios={'dated_holdings_available':evaluate('dated_holdings_available',rows)}
    # Re-form ranks after restricting membership; do not reuse full-sample ranks in a new universe.
    corroborated=[m for m in members if m['annual_membership_corroborated']]
    rows2=core.form_rows(prices,compact_members(corroborated),list(range(2006,2016)),{},earnings)
    scenarios['annual_corroborated_available']=evaluate('annual_corroborated_available',rows2)
    after={p:sha(ROOT/p) for p in protected}; assert before==after
    report=dict(status=('COMPLETED PROVISIONAL partial-period Stage1' if any(r['sector']!='UNKNOWN' for r in rows) else 'BLOCKED: no evaluable Stage1 prices'),finished_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
        stage2='SEALED; no 2016+ price rows loaded, no certified execution or ledger invoked',certified=False,
        formation_window_requested=['2006-01-01','2015-12-31'],holdings_snapshot_window=[snapshots[0]['asof'],snapshots[-1]['asof']],
        first_known_sector_snapshot=next(s['asof'] for s in snapshots if s['known_sector']),
        snapshots=len(snapshots),universe_symbols=len(universe),cached_stage1_symbols=len(prices),
        evaluated_known_sector_symbols=len({r['symbol'] for r in rows if r['sector']!='UNKNOWN'}),price_rows=sum(map(len,prices.values())),
        missing_cache_or_stage1_price_symbols=missing,invalid_price_rows=invalid,ambiguous_identity_symbols=ambiguous,
        protected_hashes_before=before,protected_hashes_after=after,coverage=coverage,annual_membership_anomalies=anomalies,
        sources=[dict(path=str(p.relative_to(ROOT)),sha256=sha(p)) for p in sorted(sources.iterdir()) if p.is_file()],
        price_source_evidence=evidence,earnings_source_evidence=[dict(path=str(p.relative_to(ROOT)),sha256=sha(p)) for p in (ROOT/'earnings_cache').glob('*.json')],
        scenarios=scenarios,limitations=[
        'Dated iShares equity holdings are a fund-membership proxy, not independently certified S&P500 PIT constituents or archived PIT GICS.',
        'Historical sector field used only at its matching snapshot date. No forward/backfill; missing, conflicting identities and unmatched symbols remain UNKNOWN.',
        '2006 Jan-Sep has no holdings snapshots; Oct2006-Mar2007 sector fields are missing. No statistical inference for those months.',
        'Retrospective iShares holdings may be revised; historical publication time and classification vintage are unverified. Selection and survivorship bias remain.',
        'Available-stock sector medians exclude missing/delisted prices. Strict full-holdings benchmark coverage is reported separately; no full-index benchmark claim.',
        'Exact ticker matches only; fund-specific symbols such as AAPL* are not silently aliased. Multiple-CIK ticker histories excluded from sector inference.',
        'The earlier 433-stock overlap cache starts in 2016 and has zero Stage1 rows. Existing reconstructed local raw_yfinance cache supplies pre-2016 rows; all matching historical holdings are used without outcome selection.',
        'H3 requires all eight actual prior surprises; existing cache only. H4 has no verified SEC as-filed cache; H6 requires H1,H3,H4,-H5 and remains missing.',
        'All outcomes capped at 2015-12-31, so 1/3/6 month horizons are right-censored; no Stage2 formations or outcomes read.',
        'Monthly calendar derives from observed price sessions. Retrospective Yahoo adjustments and permanent issuer/share-class identities unverified.',
        'Two declared sample variants, six frozen signals and twelve primary tests per variant; Holm across 24 tests also reported. Six-month horizon exploratory.',
        'A partial 2007-2008 first chronological block cannot establish the full 2006-2008 gate. No certification or Stage2 release, regardless of numeric significance.'])
    family={name+':'+key:v['p'] for name,s in scenarios.items() for key,v in s['summary'].items() if not v['exploratory']}
    corrected=core.holm(family,family_size=24)
    for name,s in scenarios.items():
        for key,v in s['summary'].items(): v['holm_p_across_24_primary_tests']=corrected.get(name+':'+key)
    (OUT/'report.json').write_text(json.dumps(report,indent=2,allow_nan=False))
    writecsv(OUT/'price_issues.csv',core.price_issues(prices))
    print(json.dumps({k:report[k] for k in ('status','snapshots','universe_symbols','cached_stage1_symbols','evaluated_known_sector_symbols','first_known_sector_snapshot')}),flush=True)
    return report

if __name__=='__main__': run()
