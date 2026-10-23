import sys
sys.path.insert(0,'/opt/mts')
from ga6.path_replay import replay
p={'ABC':[(f'2026-01-{i:02}',v,v) for i,v in enumerate([100,99,90,87,85,91,100,110],1)]}
t=[{'ticker':'ABC','entry_date':'2026-01-01','exit_date':'2026-01-08'}]
r=replay(t,p,drawdown_trigger=.05,reentry_horizon=3)
assert r['candidate_count']==3,r
assert r['oracle_only'] and r['classes']['temporary_drawdown']['count']>=1,r
print('PASS chronological next-open replay',r)
