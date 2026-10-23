from pathlib import Path
p=Path('/opt/mts/ga6/fast_portfolio_evaluator_20261021.py')
s=p.read_text()
assert 'MAX_SWING_SESSIONS' not in s
s=s.replace('from math import isfinite','from math import isfinite\nMAX_SWING_SESSIONS=40',1)
needle='''  # Gap check before discretionary orders: the open is the first executable price.
  for t,state in risk_positions.items():'''
replace='''  # Swing exit: a position may be held for at most 40 completed
  # trading sessions; liquidate at session-40 open (no lookahead).
  # Re-entry is not permitted on that same session.
  for t,state in risk_positions.items():
   if state.remaining_shares and i-position_entry_session[t]>=MAX_SWING_SESSIONS:
    risk_pending.add(t)
  # Gap check before discretionary orders: the open is the first executable price.
  for t,state in risk_positions.items():'''
assert needle in s;s=s.replace(needle,replace,1)
needle='''      completed_positions.append((closed.cumulative_realized_pnl,closed.entry_equity,i-entry_session))'''
replace='''      held=i-entry_session
      if held>MAX_SWING_SESSIONS:raise RuntimeError('Swing holding cap violated')
      completed_positions.append((closed.cumulative_realized_pnl,closed.entry_equity,held))'''
assert needle in s;s=s.replace(needle,replace,1)
s=s.replace("'open_positions_excluded':len(risk_positions),","'open_positions_excluded':len(risk_positions),'max_swing_sessions':MAX_SWING_SESSIONS,",1)
compile(s,str(p),'exec');p.write_text(s)
print('SWING_CAP_INSTALLED_COMPILED')
