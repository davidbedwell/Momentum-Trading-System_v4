from learning_ledger import LearningLedger
from tempfile import TemporaryDirectory
from pathlib import Path
with TemporaryDirectory() as tmp:
 l=LearningLedger(Path(tmp)/'test.sqlite')
 for i,ret,end in [(400,.12,'2024-06-20'),(1,.04,'2024-06-10')]:
  l.record_decision(decision_id=str(i),asof='2024-06-01',symbol='XYZ',niche='N1',chromosome=i,action='ENTER',features={'momentum':.7},proposal={'score':.2},selected=i==1,evidence_cutoff='2024-06-01')
  l.record_outcome(decision_id=str(i),outcome_asof=end,net_return=ret,holding_sessions=8,details={'shadow':i==400})
 assert not l.training_rows(train_cutoff='2024-06-10')
 assert [r['chromosome'] for r in l.training_rows(train_cutoff='2024-06-15')]==[1]
 assert len(l.training_rows(train_cutoff='2024-06-21'))==2
 assert l.compare_decisions(asof='2024-06-01',symbol='XYZ')[0]['chromosome']==400
 try:
  l.record_decision(decision_id='bad',asof='2024-06-01',symbol='XYZ',niche='N1',chromosome=2,action='ENTER',features={},proposal={},selected=False,evidence_cutoff='2024-06-02')
  raise AssertionError('future leakage')
 except ValueError:pass
 l.close()
print('PASS: immutable decisions, delayed outcomes, matured-only training, retrospective regret')
