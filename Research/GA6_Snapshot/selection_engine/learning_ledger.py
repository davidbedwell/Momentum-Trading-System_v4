"""Immutable decisions and delayed counterfactual labels for GA6 selector training.

This is a storage/training boundary, not a source of predicted returns or fills.
The evaluator must supply executable shadow outcomes with realistic costs.
"""
import json,sqlite3
from pathlib import Path

SCHEMA='''
CREATE TABLE IF NOT EXISTS decisions (
 decision_id TEXT PRIMARY KEY, asof TEXT NOT NULL, symbol TEXT NOT NULL,
 niche TEXT NOT NULL, chromosome INTEGER NOT NULL, action TEXT NOT NULL,
 feature_json TEXT NOT NULL, proposal_json TEXT NOT NULL,
 selected INTEGER NOT NULL CHECK(selected IN (0,1)),
 evidence_cutoff TEXT NOT NULL CHECK(evidence_cutoff <= asof)
);
CREATE TABLE IF NOT EXISTS outcomes (
 decision_id TEXT PRIMARY KEY REFERENCES decisions(decision_id),
 outcome_asof TEXT NOT NULL, net_return REAL NOT NULL,
 realized_pnl REAL, holding_sessions INTEGER NOT NULL,
 outcome_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS decisions_asof ON decisions(asof);
CREATE INDEX IF NOT EXISTS outcomes_maturity ON outcomes(outcome_asof);
'''
class LearningLedger:
 def __init__(self,path):
  Path(path).parent.mkdir(parents=True,exist_ok=True)
  self.db=sqlite3.connect(path)
  self.db.execute('PRAGMA foreign_keys=ON')
  self.db.executescript(SCHEMA)
 def close(self):self.db.close()
 def record_decision(self,*,decision_id,asof,symbol,niche,chromosome,action,features,proposal,selected,evidence_cutoff):
  if evidence_cutoff>asof:raise ValueError('future evidence')
  payload=(decision_id,asof,symbol,niche,chromosome,action,json.dumps(features,sort_keys=True,allow_nan=False),json.dumps(proposal,sort_keys=True,allow_nan=False),int(selected),evidence_cutoff)
  with self.db:self.db.execute('INSERT INTO decisions VALUES (?,?,?,?,?,?,?,?,?,?)',payload)
 def record_outcome(self,*,decision_id,outcome_asof,net_return,holding_sessions,details,realized_pnl=None):
  row=self.db.execute('SELECT asof FROM decisions WHERE decision_id=?',(decision_id,)).fetchone()
  if row is None:raise ValueError('missing original decision')
  if outcome_asof<=row[0]:raise ValueError('outcome not mature')
  if not 1<=holding_sessions<=40:raise ValueError('swing horizon invalid')
  with self.db:self.db.execute('INSERT INTO outcomes VALUES (?,?,?,?,?,?)',(decision_id,outcome_asof,net_return,realized_pnl,holding_sessions,json.dumps(details,sort_keys=True,allow_nan=False)))
 def training_rows(self,*,train_cutoff):
  """Only outcomes completed strictly BEFORE the selection decision date."""
  cur=self.db.execute('''SELECT d.decision_id,d.asof,d.symbol,d.niche,d.chromosome,d.action,d.feature_json,d.proposal_json,d.selected,o.outcome_asof,o.net_return,o.holding_sessions
  FROM decisions d JOIN outcomes o ON o.decision_id=d.decision_id
  WHERE o.outcome_asof < ? AND d.asof < ? ORDER BY d.asof,d.symbol,d.chromosome''',(train_cutoff,train_cutoff))
  return [dict(zip(('decision_id','asof','symbol','niche','chromosome','action','features','proposal','selected','outcome_asof','net_return','holding_sessions'),(json.loads(x) if i in (6,7) else x for i,x in enumerate(row)))) for row in cur]
 def compare_decisions(self,*,asof,symbol):
  """Retrospective audit only. Never use this query as a live selector feature."""
  cur=self.db.execute('''SELECT d.chromosome,d.selected,o.net_return,o.outcome_asof FROM decisions d JOIN outcomes o USING(decision_id) WHERE d.asof=? AND d.symbol=? ORDER BY o.net_return DESC''',(asof,symbol))
  return [dict(chromosome=c,selected=bool(s),net_return=r,outcome_asof=t) for c,s,r,t in cur]
