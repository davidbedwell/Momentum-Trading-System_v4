"""Past-only learned ranking and chronological allocator harness.
PROPOSALS ONLY: no portfolio fills, NAV, realized CAGR or drawdown.
"""
from collections import defaultdict
from learning_ledger import LearningLedger
from risk_allocator import allocate,RiskPolicy

def past_only_scores(ledger,asof,*,min_samples=5,prior_strength=20):
 rows=ledger.training_rows(train_cutoff=asof)
 stats=defaultdict(list)
 for r in rows:
  if r['outcome_asof']>=asof:raise AssertionError('future label')
  stats[(r['niche'],r['chromosome'])].append(float(r['net_return']))
 return {k:sum(v)/(len(v)+prior_strength) for k,v in stats.items() if len(v)>=min_samples}

def select_day(ledger,*,asof,candidates,cash,nav,holdings,sector_by_symbol,trailing_returns,policy=RiskPolicy(),min_samples=5):
 scores=past_only_scores(ledger,asof,min_samples=min_samples)
 scored=[];unknown=0
 for p in candidates:
  k=(p['niche'],p['chromosome'])
  if k not in scores:unknown+=1;continue
  scored.append({**p,'score':scores[k]})
 result=allocate(scored,asof=asof,cash=cash,nav=nav,holdings=holdings,sector_by_symbol=sector_by_symbol,trailing_returns=trailing_returns,policy=policy)
 return {**result,'unknown_without_mature_labels':unknown,'training_cutoff_exclusive':asof,'status':'PAST_ONLY_PROPOSALS_NOT_EXECUTED'}
