"""Research integration: GA6 policy-gated independent chromosome replay and mature labels.
Explicitly NOT equivalent to the GA6 settled-ledger evaluator (scaling, dividend,
position-equity risk and settlement are still absent from shadow_replay).
"""
import hashlib
from ga5_earnings_entry_embargo import entry_allowed
from learning_ledger import LearningLedger
from shadow_replay import replay_symbol

def run_and_persist(rows,candidates,niches,*,membership,blocked,risk_veto,db_path,cohort,fee=.001):
 if not rows:raise ValueError('empty rows')
 symbol=rows[0]['ticker'];dates={str(r['date'])[:10] for r in rows}
 if any(r['ticker']!=symbol for r in rows):raise ValueError('single symbol required')
 if not all((d,symbol) in membership and d in risk_veto for d in dates):raise ValueError('incomplete PIT policy')
 # Ineligible entry days are passed explicitly to the simulator, not inferred
 # from future price behavior.
 allowed={d:bool(membership[(d,symbol)] and risk_veto[d] is True and entry_allowed(symbol,d,blocked)) for d in dates}
 result=replay_symbol(rows,candidates,niches,fee=fee,entry_allowed_by_date=allowed,risk_veto_by_date=risk_veto)
 ledger=LearningLedger(db_path)
 try:
  for d in result['decisions']:
   decision_id=hashlib.sha256(f"{cohort}|{d['decision_id']}".encode()).hexdigest()
   ledger.record_decision(decision_id=decision_id,asof=d['asof'],symbol=symbol,niche=d['niche'],chromosome=d['chromosome'],action=d['action'],features=d['features'],proposal={'raw_weight':d['weight'],'research_only':True},selected=False,evidence_cutoff=d['asof'])
  for trade in result['trades']:
   if not trade['entry_decision_id']:continue
   decision_id=hashlib.sha256(f"{cohort}|{trade['entry_decision_id']}".encode()).hexdigest()
   ledger.record_outcome(decision_id=decision_id,outcome_asof=trade['exit_date'],net_return=trade['net_return'],realized_pnl=trade['realized_pnl'],holding_sessions=trade['holding_sessions'],details={'entry_date':trade['entry_date'],'exit_date':trade['exit_date'],'exit_reason':trade['exit_reason'],'research_only':True})
 finally:ledger.close()
 return result
