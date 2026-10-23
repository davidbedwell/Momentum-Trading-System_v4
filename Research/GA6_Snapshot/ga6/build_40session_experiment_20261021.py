from pathlib import Path
p=Path('/opt/mts/ga6/guarded_evaluator_risk_experiment_20261021.py')
s=p.read_text()
s=s.replace('  if pending:\n   decision,exits,entries,adjustments=pending','  if pending:\n   decision,exits,entries,adjustments=pending',1)
s=s.replace('  # Execute previously triggered mandatory exits at first available open.','''  # Research-only maximum holding period: 40 completed sessions; exit on
  # next session open before any discretionary orders.
  for t,pos in positions.items():
   if pos.sessions_held>=40 and ledger.holdings.get(t,0):
    risk_pending.add(t)
    if not any(e.get('event')=='MAX_HOLD_40_TRIGGERED' and e.get('ticker')==t and e.get('date')==ds for e in risk_events):
     risk_events.append({'date':ds,'ticker':t,'event':'MAX_HOLD_40_TRIGGERED','sessions':pos.sessions_held})
  # Execute previously triggered mandatory exits at first available open.''',1)
s=s.replace('  # Gap check before discretionary orders: the open is the first executable price.','  # Gap check before discretionary orders: the open is the first executable price.',1)
s=s.replace('     risk_events.append({"date":ds,"ticker":t,"event":"MANDATORY_EXIT_FILLED"})','     risk_events.append({"date":ds,"ticker":t,"event":"FORCED_EXIT_FILLED"})',1)
s=s.replace('   exits=[t for t in exits if t not in mandatory_exited]','   exits=[t for t in exits if t not in mandatory_exited]\n   entries=[e for e in entries if e[0] not in mandatory_exited]',1)
s=s.replace('    risk_pending.add(t)\n  if risk_pending:', '''    if t not in risk_pending:
     risk_pending.add(t)
     risk_events.append({'date':ds,'ticker':t,'event':'GAP_2PCT_TRIGGERED'})
  if risk_pending:''',1)
out=Path('/opt/mts/ga6/guarded_evaluator_risk_40session_20261021.py')
out.write_text(s)
compile(s,str(out),'exec')
print('40_SESSION_EXPERIMENT_COMPILES')
