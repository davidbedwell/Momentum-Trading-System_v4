from pathlib import Path
r=Path('/opt/mts/ga6')
p=r/'guarded_evaluator_risk_40session_20261021.py'
s=p.read_text()
s=s.replace('risk_entry_equity={};nav=[]','risk_entry_equity={};last_exit_session={};nav=[]',1)
s=s.replace('     mandatory_exited.add(t)','     mandatory_exited.add(t)\n     last_exit_session[t]=i',1)
s=s.replace('     positions.pop(t,None)\n   # Process reductions','     positions.pop(t,None)\n     last_exit_session[t]=i\n   # Process reductions',1)
s=s.replace('     if qty==held:positions.pop(t,None)','     if qty==held:\n      positions.pop(t,None)\n      last_exit_session[t]=i',1)
s=s.replace('    if t not in opens or t in mandatory_exited or ledger.holdings.get(t,0)>0:continue','    if t not in opens or t in mandatory_exited or ledger.holdings.get(t,0)>0 or i-last_exit_session.get(t,-100)>=0 and i-last_exit_session.get(t,-100)<2:continue',1)
p.write_text(s)
q=r/'shadow_40session_20261021.py'
x=q.read_text()
x=x.replace('self.closed=[];self.events=[];self.signals=0;self.missing_open=0','self.closed=[];self.events=[];self.signals=0;self.missing_open=0;self.session_index=-1;self.last_exit_session={}',1)
x=x.replace('  actions=actions or {}','  self.session_index+=1\n  actions=actions or {}',1)
x=x.replace("    if ticker in self.open or not membership.get((date,ticker),False)","    if ticker in self.open or self.session_index-self.last_exit_session.get(ticker,-100)<2 or not membership.get((date,ticker),False)",1)
x=x.replace('      self.open.pop(ticker)\n      total=', '      self.open.pop(ticker)\n      self.last_exit_session[ticker]=self.session_index\n      total=',1)
x=x.replace("   elif ticker not in self.pending:\n    action,_=decide","   elif ticker not in self.pending and self.session_index-self.last_exit_session.get(ticker,-100)>=1:\n    action,_=decide",1)
# Exit on day D: signal may be generated on D+1 close for D+2 open.
for f,t in ((p,s),(q,x)):
 f.write_text(t);compile(t,str(f),'exec')
print('40_SESSION_CAP_AND_2_SESSION_REENTRY_COMPILE')
