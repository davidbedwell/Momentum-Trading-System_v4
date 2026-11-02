"""Compare pinned free membership against dated IVV evidence without changing research inputs."""
import csv,json,hashlib,statistics as st
from pathlib import Path
import pandas as pd
from .expanded_stage1 import writecsv,sector_label
OUT=Path('reports/bounded-repair'); SRC=OUT/'sources'; BASE=Path('reports/expanded-stage1')
def run():
    seed=list(csv.DictReader((SRC/'sp500_seed.csv').open())); events=sorted(csv.DictReader((SRC/'sp500_changes.csv').open()),key=lambda r:r['date'])
    current={r['ticker']:r for r in csv.DictReader((SRC/'sp500_current.csv').open())}
    def roster(date):
        active={r['ticker'] for r in seed}
        for r in events:
            if r['date']>date: break
            if r['action']=='added':active.add(r['ticker'])
            elif r['action']=='removed':active.discard(r['ticker'])
            else:raise ValueError(r)
        return active
    members=list(csv.DictReader((BASE/'membership_used.csv').open())); prices=pd.read_parquet(BASE/'prices_used.parquet',columns=['symbol','date']); available=set(zip(prices.date,prices.symbol))
    rows=[]
    for date in sorted({r['start'] for r in members}):
        ivv={r['symbol']:r for r in members if r['start']==date}; pit=roster(date); common=pit&ivv.keys()
        comparable=[s for s in common if s in current and ivv[s]['sector']!='UNKNOWN' and sector_label(current[s]['gics_sector'])!='UNKNOWN']
        disagreements=[s for s in comparable if sector_label(current[s]['gics_sector'])!=ivv[s]['sector']]
        rows.append(dict(asof=date,ivv=len(ivv),pitindex=len(pit),common=len(common),jaccard=len(common)/len(pit|ivv.keys()),ivv_only=sorted(ivv.keys()-pit),pitindex_only=sorted(pit-ivv.keys()),pitindex_priced=sum((date,s) in available for s in pit),ivv_priced=sum((date,s) in available for s in ivv),pitindex_missing_prices=sum((date,s) not in available for s in pit),current_sector_available=sum(s in current for s in pit),current_vs_historical_sector_comparable=len(comparable),current_vs_historical_sector_disagreements=disagreements))
    writecsv(OUT/'membership_comparison.csv',rows)
    early=[]
    for date in pd.date_range('2006-01-31','2006-09-30',freq='ME').strftime('%Y-%m-%d'):
        p=roster(date);early.append(dict(asof=date,membership=len(p),current_sector_available=sum(s in current for s in p),historical_sector_verified=0))
    report=json.loads((BASE/'report.json').read_text()); cov=report['coverage']; protected=report['protected_hashes_after']
    hashes={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in protected}
    result=dict(decision='NO-GO; STOP',rerun_primary=False,reason='Zero recovered price rows and zero newly verified PIT sector labels; no meaningful usable-coverage improvement.',meaningful_coverage_rule='At least +5 percentage points in priced, historically sector-verified stock-month coverage, or 12 additional complete sector-month benchmarks. A membership-only addition does not qualify.',pitindex_commit=json.loads((SRC/'tree.json').read_text())['sha'],snapshot_comparison=dict(months=len(rows),jaccard_mean=st.mean(r['jaccard'] for r in rows),jaccard_min=min(r['jaccard'] for r in rows),common_mean=st.mean(r['common'] for r in rows),ivv_only_total=sum(len(r['ivv_only']) for r in rows),pitindex_only_total=sum(len(r['pitindex_only']) for r in rows),ivv_priced_total=sum(r['ivv_priced'] for r in rows),pitindex_priced_total=sum(r['pitindex_priced'] for r in rows),pitindex_missing_price_stock_months=sum(r['pitindex_missing_prices'] for r in rows),sector_comparable_total=sum(r['current_vs_historical_sector_comparable'] for r in rows),sector_disagreements_total=sum(len(r['current_vs_historical_sector_disagreements']) for r in rows)),early_membership_candidates=early,baseline=dict(price_rows=report['price_rows'],priced_symbols=report['cached_stage1_symbols'],universe_symbols=report['universe_symbols'],missing_price_symbols=len(report['missing_cache_or_stage1_price_symbols']),stock_months=sum(c['expected_holdings'] for c in cov),missing_price_stock_months=sum(len(c['missing_symbols']) for c in cov),priced_known_sector_stock_months=sum(c['priced_known_sector'] for c in cov),known_sector_stock_month_coverage=sum(c['priced_known_sector'] for c in cov)/sum(c['expected_holdings'] for c in cov),strict_benchmark_rows=report['scenarios']['dated_holdings_available']['strict_full_holdings_benchmark_rows']),repair=dict(recovered_price_rows=0,new_verified_historical_sector_labels=0,usable_coverage_gain_percentage_points=0,additional_complete_benchmark_rows=0),sourcing=dict(max_minutes=10,local_targets=10,free_price_requests=6,full_universe_price_download=False),protected_hashes=hashes,protected_unchanged_from_expanded=hashes==protected,limitations=['Exact ticker comparison; differences include fund aliases, historical renames, share classes, and source errors; neither roster is treated as ground truth.','pitindex current sector enrichment is retrospective, not PIT GICS. Its historical roster can extend membership evidence but supplies no prices.','Current roster/metadata were read only for source assessment; no Stage2 prices or returns were loaded.','Six failed Yahoo probes and a bounded local search do not prove global nonexistence of free delisted prices.','No H3/H4/H6 historical analysis, no primary rerun, no new placebos or Holm family, no Stage2 release.'])
    assert result['protected_unchanged_from_expanded']
    (OUT/'comparison.json').write_text(json.dumps(result,indent=2)); print(json.dumps(result,indent=2))
if __name__=='__main__':run()
