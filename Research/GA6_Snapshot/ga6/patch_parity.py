from pathlib import Path
p=Path('/opt/mts/ga6/guarded_evaluator_ga6.py')
s=p.read_text()
a=s.index('class PreparedSessions:')
b=s.index('\ndef evaluate(',a)
s=s[:a]+'from ga5_redesign.guarded_evaluator_niche_single_exit import PreparedSessions\n'+s[b:]
p.write_text(s)
print('shared prepared session class installed')
