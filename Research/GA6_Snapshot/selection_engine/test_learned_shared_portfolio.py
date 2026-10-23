"""Historical next-open shared-capital selector integration, two DEV79 stocks.
Pre-seeded past-only synthetic outcomes test wiring, NOT predictive efficacy.
"""
import tempfile
from pathlib import Path
import pandas as pd
from learning_ledger import LearningLedger
from chronological_selector import select_day
from risk_allocator import RiskPolicy
from shared_capital_execution import SharedCapitalExecution
ROOT=Path('/opt/mts')
f=pd.read_parquet(ROOT/'ga5_redesign/exploratory79_ga4_enriched.parquet')
names=sorted(f.ticker.unique())[:2]
f=f[f.ticker.isin(names)].sort_values(['date','ticker'])
f=f[(f.date>='2024-01-02')&(f.date<'2024-02-15')]
assert len(names)==2
with tempfile.TemporaryDirectory() as tmp:
 ledger=LearningLedger(str(Path(tmp)/'learning.sqlite'))
 # Earlier matured labels are synthetic: isolate execution integration, not alpha.
 for i,t in enumerate(names):
  ledger.record_decision(decision_id=t,asof='2023-10-02',symbol=t,niche='NICHE-0001',chromosome=i,action='ENTER',features={},proposal={},selected=False,evidence_cutoff='2023-10-02')
  ledger.record_outcome(decision_id=t,outcome_asof='2023-10-20',net_return=.10-i*.01,holding_sessions=10,details={'synthetic':True})
 x=SharedCapitalExecution(cash=100000,annual_cash_yield=0)
 dates=sorted(f.date.unique());prev={};ret={t:{} for t in names}
 for ds in dates:
  day=f[f.date==ds];date=str(ds)[:10]
  rows={r.ticker:r._asdict() for r in day.itertuples(index=False)}
  if set(rows)!=set(names):continue
  opens={t:float(r['open'])*float(r['adj_close'])/float(r['close']) for t,r in rows.items()}
  closes={t:float(r['adj_close']) for t,r in rows.items()}
  for t,p in closes.items():
   if t in prev:ret[t][date]=p/prev[t]-1
   prev[t]=p
  membership={(date,t):True for t in names}
  x.start(date,opens,closes,rows,risk_veto={date:True},membership=membership,blocked={})
  nav=x.nav[-1][1];holdings={t:q*closes[t]/nav for t,q in x.ledger.holdings.items() if q}
  candidates=[dict(symbol=t,chromosome=i,niche='NICHE-0001',target_weight=.03,evidence_cutoff=date) for i,t in enumerate(names) if not x.ledger.holdings.get(t)]
  proposal=select_day(ledger,asof=date,candidates=candidates,cash=x.ledger.available_cash(),nav=nav,holdings=holdings,sector_by_symbol={t:'SyntheticSector' for t in names},trailing_returns=ret,policy=RiskPolicy(min_observations=2),min_samples=1)
  x.schedule(date,[dict(symbol=o['symbol'],action=o['action'],weight=o['incremental_weight'],max_weight=.10) for o in proposal['orders'] if o['action'] in ('ENTER','ADD')])
 assert len(x.ledger.fills)>0 and all(z['execution_date']>z['decision_date'] for z in x.ledger.fills)
 assert sum(q*closes[t] for t,q in x.ledger.holdings.items())<=x.nav[-1][1]+1e-6
 print('PASS: historical 2-stock shared-capital next-open selector integration',len(x.nav),'sessions',len(x.ledger.fills),'fills','final_NAV',round(x.nav[-1][1],2),'SYNTHETIC_TRAINING_LABELS_NOT_PERFORMANCE')
 ledger.close()
