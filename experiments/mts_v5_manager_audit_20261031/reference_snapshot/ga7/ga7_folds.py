"""GA7-only deterministic stock-fold assignment and causal walk-forward schedule."""
from collections import defaultdict
from datetime import date
import hashlib
import json


def sector_balanced_folds(ticker_sector, count=3):
    """Deterministic, disjoint sector-stratified allocation; never inspect returns."""
    if count<2 or len(ticker_sector)<count: raise ValueError('Insufficient stocks for folds')
    sectors=defaultdict(list)
    for ticker,sector in ticker_sector.items():
        sectors[str(sector)].append(str(ticker))
    groups={f'S{i+1}':[] for i in range(count)}
    for sector,tickers in sorted(sectors.items()):
        tickers.sort(key=lambda t:hashlib.sha256(t.encode()).hexdigest())
        for ticker in tickers:
            target=min(groups,key=lambda k:(sum(ticker_sector[t]==sector for t in groups[k]),len(groups[k]),k))
            groups[target].append(ticker)
    if set(sum(groups.values(),[]))!=set(ticker_sector): raise AssertionError('Fold loss')
    return {k:sorted(v) for k,v in groups.items()}


def expanding_walk_forward(first_year=2009,last_year=2024,train_years=5,test_years=1):
    """Train through preceding December 31, evaluate only following calendar year."""
    if train_years<1 or test_years<1 or last_year-first_year+1<train_years+test_years:
        raise ValueError('Insufficient history')
    result=[]
    for start in range(first_year+train_years,last_year-test_years+2,test_years):
        result.append(dict(train_start=f'{first_year}-01-01',train_end_exclusive=f'{start}-01-01',
                           test_start=f'{start}-01-01',test_end_exclusive=f'{start+test_years}-01-01'))
    return result


def freeze_plan(ticker_sector):
    folds=sector_balanced_folds(ticker_sector)
    schedule=expanding_walk_forward()
    return dict(schema='ga7-fold-plan-v1',stock_folds=folds,chronological_folds=schedule,
                methodology='Sector-stratified stock folds; 5-year expanding history then 1-year forward test; no validation data in breeding',
                status='PLAN_ONLY_NOT_WIRED_TO_EVALUATOR')
