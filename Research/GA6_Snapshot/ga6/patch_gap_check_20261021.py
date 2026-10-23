from pathlib import Path
p=Path('/opt/mts/ga6/guarded_evaluator_risk_experiment_20261021.py')
x=p.read_text()
x=x.replace('  mandatory_exited=set()','''  mandatory_exited=set()
  # Gap check before discretionary orders: the open is the first executable price.
  for t,state in risk_positions.items():
   if state.remaining_shares and t in opens and state.mark(opens[t],fee)['mandatory_exit']:
    risk_pending.add(t)''')
x=x.replace('   decision,exits,entries,adjustments=pending','''   decision,exits,entries,adjustments=pending
   exits=[t for t in exits if t not in mandatory_exited]
   adjustments=[a for a in adjustments if a[0] not in mandatory_exited]''')
x=x.replace('  if i==0:risk_fill_cursor=0','  if i==0:risk_fill_cursor=0')
x=x.replace('  for fill in ledger.fills[risk_fill_cursor:]:','''  for fill in ledger.fills[risk_fill_cursor:]:''')
# Avoid reopening a forced exited ticker from pending and preserve true initial equity.
x=x.replace('  for t,state in risk_positions.items():\n   if state.remaining_shares and t in closes:', '  for t,state in risk_positions.items():\n   if state.remaining_shares and t in closes:')
p.write_text(x)
compile(x,str(p),'exec')
print('PATCH_COMPILES')
