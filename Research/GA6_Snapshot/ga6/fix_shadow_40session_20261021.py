from pathlib import Path
root=Path('/opt/mts/ga6')
src=(Path('/opt/mts/ga5_redesign/shadow_niche_single_exit.py')).read_text()
old="    action,weight=decide(self.genome,f,PositionState(tr['shares'],tr['entry'],tr['peak'],tr['sessions']),price)"
new="""    if tr['sessions']>=40:
     self.pending[ticker]=('SELL',date,1.)
     continue
    action,weight=decide(self.genome,f,PositionState(tr['shares'],tr['entry'],tr['peak'],tr['sessions']),price)"""
assert old in src
src=src.replace(old,new,1)
p=root/'shadow_40session_20261021.py';p.write_text(src)
e=root/'guarded_evaluator_risk_40session_20261021.py'
x=e.read_text()
assert 'from shadow_niche_single_exit import ShadowBook' in x
x=x.replace('from shadow_niche_single_exit import ShadowBook','from ga6.shadow_40session_20261021 import ShadowBook',1)
e.write_text(x)
compile(src,str(p),'exec');compile(x,str(e),'exec')
print('40_SESSION_SHADOW_AND_PORTFOLIO_COMPILE')
