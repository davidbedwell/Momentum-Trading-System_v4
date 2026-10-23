"""Create isolated risk-aware evaluator from frozen GA6 baseline; never edit production."""
from pathlib import Path
source=Path('/opt/mts/ga6/guarded_evaluator_ga6.py').read_text()
source=source.replace('from exit_objectives import metrics as exit_metrics,calmar','from exit_objectives import metrics as exit_metrics,calmar\nfrom ga6.position_equity_risk_20261021 import PositionRisk')
source=source.replace(' pending=None;positions={};nav=[];last={};scale_fills=', ' pending=None;positions={};risk_positions={};risk_pending=set();risk_events=[];nav=[];last={};scale_fills=')
needle='  if pending:\n   decision,exits,entries,adjustments=pending'
replacement='''  # Execute previously triggered mandatory exits at first available open.
  # This is a next-open risk policy; gaps may exceed the 2% threshold.
  if risk_pending:
   for t in sorted(risk_pending):
    qty=ledger.holdings.get(t,0)
    if qty and t in opens:
     ledger.execute_open(Order(ds,t,"SELL",qty),ds,opens[t])
     positions.pop(t,None)
     risk_events.append({"date":ds,"ticker":t,"event":"MANDATORY_EXIT_FILLED"})
   risk_pending={t for t in risk_pending if ledger.holdings.get(t,0)}
  if pending:
   decision,exits,entries,adjustments=pending'''
assert source.count(needle)==1
source=source.replace(needle,replacement)
# Intercept actual fills, not shadow signals; preserve initial equity at entry.
needle='  replayed_fill_cursor=len(ledger.fills)'
replacement='''  # Track actual fills using immutable entry-time equity, never scale-in equity.
  if i==0:risk_fill_cursor=0
  for fill in ledger.fills[risk_fill_cursor:]:
   t=fill['security'];qty=fill['shares'];price=fill['price']
   fee_paid=fill['fee']
   if fill['side']=='BUY':
    if t not in risk_positions:
     # Opening NAV before fills is approximated from prior close NAV;
     # require independent verification before certification.
     e0=nav[-1][1] if nav else starting_cash
     risk_positions[t]=PositionRisk(e0)
    risk_positions[t].buy(qty,price,fee_paid/(qty*price))
   else:
    if t in risk_positions:
     risk_positions[t].sell(qty,price,fee_paid/(qty*price))
     if not risk_positions[t].remaining_shares:risk_positions.pop(t)
  risk_fill_cursor=len(ledger.fills)
  replayed_fill_cursor=len(ledger.fills)'''
assert source.count(needle)==1
source=source.replace(needle,replacement)
needle='  last.update(closes);nav.append((ds,ledger.nav(closes)))'
replacement='''  for t,state in risk_positions.items():
   if state.remaining_shares and t in closes:
    mark=state.mark(closes[t],fee)
    if mark['mandatory_exit'] and t not in risk_pending:
     risk_pending.add(t)
     risk_events.append({"date":ds,"ticker":t,"event":"MANDATORY_EXIT_TRIGGERED","loss_fraction":mark['loss_fraction_entry_equity']})
  last.update(closes);nav.append((ds,ledger.nav(closes)))'''
assert source.count(needle)==1
source=source.replace(needle,replacement)
needle='"ga6_portfolio_diagnostics":portfolio_diagnostics,'
replacement='"ga6_portfolio_diagnostics":portfolio_diagnostics,"ga6_position_risk_events":risk_events,"ga6_risk_pending_at_end":sorted(risk_pending),'
assert source.count(needle)==1
source=source.replace(needle,replacement)
path=Path('/opt/mts/ga6/guarded_evaluator_risk_experiment_20261021.py')
path.write_text(source)
compile(source,str(path),'exec')
print('EXPERIMENTAL EVALUATOR COMPILES',path)
