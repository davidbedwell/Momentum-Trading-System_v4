from pathlib import Path
p=Path('/opt/mts/ga6/guarded_evaluator_risk_experiment_20261021.py')
s=p.read_text()
s=s.replace('pending=None;positions={};risk_positions={};risk_pending=set();risk_events=[];', 'pending=None;positions={};risk_positions={};risk_pending=set();risk_events=[];risk_entry_equity={};')
s=s.replace('  if pending:\n   decision,exits,entries,adjustments=pending','  if pending:\n   decision,exits,entries,adjustments=pending')
# Prevent mandatory exited position from being reentered in same open.
s=s.replace('  if risk_pending:\n   for t in sorted(risk_pending):','  mandatory_exited=set()\n  if risk_pending:\n   for t in sorted(risk_pending):')
s=s.replace('     positions.pop(t,None)\n     risk_events.append', '     positions.pop(t,None)\n     mandatory_exited.add(t)\n     risk_events.append')
s=s.replace('    if t not in opens or ledger.holdings.get(t,0)>0:continue','    if t not in opens or t in mandatory_exited or ledger.holdings.get(t,0)>0:continue')
# Capture true opening equity at first BUY; before any fill, never reset when scaling.
s=s.replace('    ledger.execute_open(Order(decision,t,"BUY",qty),ds,price)\n    active_positions+=1','    risk_entry_equity[t]=equity\n    ledger.execute_open(Order(decision,t,"BUY",qty),ds,price)\n    active_positions+=1')
s=s.replace('     # Opening NAV before fills is approximated from prior close NAV;\n     # require independent verification before certification.\n     e0=nav[-1][1] if nav else starting_cash','     e0=risk_entry_equity.pop(t,None)\n     if e0 is None:raise RuntimeError("Missing entry-time equity")')
# Reassessment state invokes normal exit signal, disallows scale-in when reassessing.
s=s.replace('    if mark[\'mandatory_exit\'] and t not in risk_pending:', '''    if mark['reassess'] and not any(e.get('ticker')==t and e.get('event')=='REASSESSMENT_ACTIVATED' for e in risk_events):
     risk_events.append({"date":ds,"ticker":t,"event":"REASSESSMENT_ACTIVATED"})
    if mark['mandatory_exit'] and t not in risk_pending:''')
s=s.replace('   elif p.shares and action in ("SCALE_IN","SCALE_OUT"):adjustments.append((t,action,weight))','''   elif p.shares and action in ("SCALE_IN","SCALE_OUT"):
    if action=="SCALE_IN" and (t in risk_pending or (t in risk_positions and risk_positions[t].reassessed)):continue
    adjustments.append((t,action,weight))''')
s=s.replace('  pending=(ds,exits,[(t,w) for t,w,_ in entries],adjustments)','''  # No forced-exit ticker may remain in a pending adjustment.
  adjustments=[a for a in adjustments if a[0] not in risk_pending]
  pending=(ds,exits,[(t,w) for t,w,_ in entries if t not in risk_pending],adjustments)''')
p.write_text(s)
compile(s,str(p),'exec')
print('RISK PATCH COMPILES')
