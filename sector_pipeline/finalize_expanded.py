"""Create a concise reviewable report from completed Stage1 artifacts."""
import json
import csv
from collections import defaultdict
from pathlib import Path
import statistics as st
from .expanded_stage1 import OUT
from .validate_expanded import run as validate


def run():
    r=json.loads((OUT/'report.json').read_text())
    assert r['status'].startswith('COMPLETED')
    duplicates=[]
    for p in sorted((OUT/'sources').glob('ishares_*.csv')):
        grouped=defaultdict(list)
        for x in csv.DictReader(p.open()):
            if x['asset_class']=='Equity': grouped[x['symbol']].append(x)
        for symbol,g in grouped.items():
            if len(g)>1:
                assert len({x['sector'] for x in g})==1
                duplicates.append(dict(asof=g[0]['date'],symbol=symbol,names=sorted({x['name'] for x in g}),
                    cusips=sorted({x['CUSIP'] for x in g}),sectors=sorted({x['sector'] for x in g}),
                    permanent_identity='UNKNOWN',treatment='one ticker observation; labels agree; identity unresolved'))
    (OUT/'duplicate_identity_evidence.json').write_text(json.dumps(duplicates,indent=2))
    r['duplicate_identity_evidence']=duplicates
    r['limitations'].append('Retrospective holdings contain back-normalized/repeated ticker symbols: CB has ACE and Chubb names, MRK has two CUSIPs, and AGN has two names. Duplicate ticker entries are counted once, agreeing sector labels are retained, conflicting permanent identities remain UNKNOWN. This is a ticker-level dated-sector sensitivity, not reconstructed original ticker/share-class PIT history. Full-holdings benchmark counts refer only to deduplicated ticker proxies.')
    members=list(csv.DictReader((OUT/'membership_used.csv').open()))
    duplicate_lookup={(x['asof'],x['symbol']):x for x in duplicates}
    for m in members:
        d=duplicate_lookup.get((m['start'],m['symbol']))
        m['permanent_identity_status']='UNKNOWN; cache-to-historical-share-class mapping unverified'
        m['all_source_names']=json.dumps(d['names']) if d else m['source_name']
        m['all_source_cusips']=json.dumps(d['cusips']) if d else m['identity_cusip']
    with (OUT/'membership_used.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(members[0]));w.writeheader();w.writerows(members)
    observed={x['asof'][:7] for x in r['coverage']}
    r['months_without_membership_snapshots']=[f'{y}-{m:02d}' for y in range(2006,2016) for m in range(1,13) if f'{y}-{m:02d}' not in observed]
    r['limitations'].append('H3 issuer coverage derives from the earnings cache of the contaminated, outcome-selected 2019 pilot; Stage1 event dates do not remove this issuer-selection bias.')
    r['execution_note']='An earlier redundant-interval observation-building pass was interrupted before metrics; compacted intervals were asserted identical at every snapshot date. One completed expanded statistics run per registered sample.'
    c=[x for x in r['coverage'] if x['known_sector']]
    r['coverage_summary']=dict(labeled_months=len(c),priced_known_sector_min=min(x['priced_known_sector'] for x in c),
        priced_known_sector_max=max(x['priced_known_sector'] for x in c),priced_known_sector_mean=st.mean(x['priced_known_sector'] for x in c),
        expected_holdings_min=min(x['expected_holdings'] for x in c),expected_holdings_max=max(x['expected_holdings'] for x in c),
        unknown_sector_total=sum(x['unknown_sector'] for x in r['coverage']))
    r['limitations']=list(dict.fromkeys(r['limitations']))
    (OUT/'report.json').write_text(json.dumps(r,indent=2,allow_nan=False))
    v=validate()
    fmt=lambda x:'unavailable' if x is None else f'{x:.5f}'
    lines=['Expanded PROVISIONAL partial-period Stage1 — COMPLETED.', '',
        f"Loaded {r['price_rows']:,} pre-2016 price rows for {r['cached_stage1_symbols']} exact-matching historical holdings; {r['evaluated_known_sector_symbols']} symbols contribute known-sector outcomes.", '',
        'The earlier 433-stock overlap cache begins in 2016 and supplies zero Stage1 observations. The separate existing reconstructed raw_yfinance cache supplies this run. No external MTS files were modified.', '',
        f"All {r['snapshots']} dated IVV holdings snapshots from {r['holdings_snapshot_window'][0]} through {r['holdings_snapshot_window'][1]} were processed. Sector evidence begins {r['first_known_sector_snapshot']}; the preceding six snapshots have UNKNOWN sectors. January–September 2006 has no holdings snapshots. No current-sector backfill was used.", '',
        f"Labeled-month formation-price/sector coverage: {min(x['priced_known_sector'] for x in c)}–{max(x['priced_known_sector'] for x in c)} stocks per month (mean {st.mean(x['priced_known_sector'] for x in c):.2f}) against {min(x['expected_holdings'] for x in c)}–{max(x['expected_holdings'] for x in c)} equity holdings. See coverage.json for every missing ticker, unknown-sector count, horizon and signal count.", '',
        'Results below are raw equal-sector monthly mean Spearman ICs and frozen Newey–West t statistics. H5 expects a negative raw IC/t. Six signals and their definitions remain frozen; H4 and H6 are unavailable. H3 uses all eight prior surprises and remains sparse. Its issuer cache originated in the contaminated, outcome-selected 2019 pilot, so H3 also carries selection bias. No unavailable hypothesis receives invented observations or placebo results.', '']
    for name,s in r['scenarios'].items():
        lines += [f'Sample: {name}', '', '| Signal | 1m IC | NW t | 3m IC | NW t | 6m IC (exploratory) |', '|---|---:|---:|---:|---:|---:|']
        for sig in ('H1','H2','H3','H4','H5','H6'):
            a,b,d=[s['summary'][f'{sig}_{h}'] for h in (1,3,6)]
            lines += [f"| {sig} | {fmt(a['mean'])} | {fmt(a['t'])} | {fmt(b['mean'])} | {fmt(b['t'])} | {fmt(d['mean'])} |"]
        lines += ['', '| Signal/horizon | Months | Stocks | IC dates | Positive blocks | Positive-IC fraction (oriented) | Placebo real / 99th percentile | Beats placebo? |', '|---|---:|---:|---|---:|---:|---|---|']
        for key,a in s['summary'].items():
            if a['mean'] is None: continue
            n=s['sample_sizes'][key]; p=a['placebo']
            lines += [f"| {key} | {a['n']} | {n['symbols']} | {n['first_ic']}–{n['last_ic']} | {a['positive_blocks']}/4 | {fmt(a['fraction_positive_ic'])} | {fmt(p['real'])} / {fmt(p['percentile99'])} | {p['passed']} |"]
        lines += ['',f"Full-holdings benchmark rows: {s['strict_full_holdings_benchmark_rows']:,}; explicit available-stock benchmark rows: {s['available_stock_benchmark_rows']:,}. Neither establishes complete S&P500 benchmark coverage.", '']
    lines += ['Each defined statistic received exactly 1,000 within-sector-month permutations with fixed seed 0. H4/H6 have undefined ICs and zero shuffles. All means, HAC errors/t/p, twelve-test and twenty-four-test Holm p values, four-block counts, spreads, turnover, 15bp one-way net costs and lookahead diagnostics are in report.json; per-sector monthly observations and statistics are saved under each sample directory.', '',
        'The first chronological block is partial, membership is a dated tracking-fund proxy, publication/sector vintage is retrospective and unverified, and prices exclude many removed/delisted issuers. Retrospective holdings also contain normalized/repeated symbols: CB includes ACE/Chubb names and MRK two CUSIPs. One observation per ticker is retained because sector labels agree; permanent identity remains UNKNOWN. See duplicate_identity_evidence.json. This does not establish original historical ticker or share-class PIT history. Full-holdings counts refer to deduplicated ticker proxies. No certification, full-period pass or predictive claim is justified. Both variants are exploratory, and neither can release Stage2. Available-stock medians do not repair survivor bias.', '',
        'All price rows and exits end by 2015-12-31. Primary 1m/3m and exploratory 6m outcomes are right-censored accordingly. No 2016+ formations/outcome rows were loaded. Sealed manifest, protocols, core statistical engine, executor and gate hashes match before/after. 2019/2020 remain contaminated and are not evaluated by this run.', '',
        'Sources: [dated IVV snapshot repository](https://github.com/riazarbi/sp500-scraper), [annual membership cross-check](https://github.com/shardul0701/SP500-Survivorship-bias-data-2004-2026), [ticker ambiguity evidence](https://github.com/lawcal/sp500-components-history). URLs/blob IDs are in sources/acquisition.json; SHA256s are in report.json. Missing historical prices/identities, verified as-filed H4 inputs, complete historical membership/sector publication evidence and terminal delisting returns remain blockers to certification.', '',
        'Reproduce: `/opt/mts/.venv/bin/python -m sector_pipeline.expanded_stage1` then `/opt/mts/.venv/bin/python -m sector_pipeline.finalize_expanded`. The first command requires read access to the existing historical MTS cache and writes only here. Optional analysis dependencies: numpy, pandas, pyarrow; YAML source parsing uses system PyYAML. Tests: analysis environment 43 passed; default environment 39 passed, one optional module skipped. Artifact validation: PASS, including independent recomputation of saved sector ICs and verification of all downloaded source hashes.', '']
    (OUT/'README.md').write_text('\n'.join(lines))
    print(json.dumps(dict(status=r['status'],coverage=r['coverage_summary'],validation=v),indent=2))

if __name__=='__main__':run()
