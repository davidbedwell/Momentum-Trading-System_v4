import sys
sys.path.insert(0,'/opt/mts')
from ga6.episode_uncertainty import assess
trades=[{'entry_date':f'{2020+i//12}-{i%12+1:02d}-05','net_return':.03} for i in range(24)]
a=assess(trades);b=assess(trades)
assert a==b and a['robust_positive'] and a['independent_months']==24
assert not assess(trades[:5])['eligible']
print('PASS reproducible episode-aware uncertainty and insufficient-episode guard')
