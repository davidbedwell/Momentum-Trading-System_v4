from chronological_selector import past_only_scores,select_day
from learning_ledger import LearningLedger
from pathlib import Path
import tempfile
with tempfile.TemporaryDirectory() as td:
 l=LearningLedger(str(Path(td)/'x.sqlite'))
 for i,ret,exit_date in [(0,.08,'2024-02-01'),(1,-.4,'2024-04-01')]:
  l.record_decision(decision_id=str(i),asof='2024-01-02',symbol='AAA',niche='NICHE-0001',chromosome=17,action='ENTER',features={},proposal={},selected=False,evidence_cutoff='2024-01-02')
  l.record_outcome(decision_id=str(i),outcome_asof=exit_date,net_return=ret,holding_sessions=20,details={})
 assert past_only_scores(l,'2024-03-01',min_samples=1)[('NICHE-0001',17)]>0
 assert past_only_scores(l,'2024-05-01',min_samples=1)[('NICHE-0001',17)]<0
 ret={'AAA':{f'2024-02-{i:02d}':.001*i for i in range(1,21)}}
 result=select_day(l,asof='2024-03-01',candidates=[dict(symbol='AAA',chromosome=17,niche='NICHE-0001',target_weight=.03,evidence_cutoff='2024-03-01')],cash=100000,nav=100000,holdings={},sector_by_symbol={'AAA':'Tech'},trailing_returns=ret,policy=__import__('risk_allocator').RiskPolicy(min_observations=2),min_samples=1)
 assert len(result['orders'])==1 and result['orders'][0]['action']=='ENTER'
 result2=select_day(l,asof='2024-05-01',candidates=[dict(symbol='AAA',chromosome=17,niche='NICHE-0001',target_weight=.03,evidence_cutoff='2024-05-01')],cash=100000,nav=100000,holdings={},sector_by_symbol={'AAA':'Tech'},trailing_returns=ret,policy=__import__('risk_allocator').RiskPolicy(min_observations=2),min_samples=1)
 assert not result2['orders']
 l.close()
 print('PASS: past-only matured outcomes alter chronological allocation; no future label leakage')
