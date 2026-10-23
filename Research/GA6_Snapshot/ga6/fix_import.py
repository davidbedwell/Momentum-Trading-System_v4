from pathlib import Path
p=Path('/opt/mts/ga6/runner.py')
s=p.read_text().replace('from guarded_evaluator_niche_single_exit import PreparedSessions','from ga5_redesign.guarded_evaluator_niche_single_exit import PreparedSessions')
p.write_text(s)
print('canonical PreparedSessions import fixed')
