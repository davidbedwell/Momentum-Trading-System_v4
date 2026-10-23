import sys
sys.path.insert(0,'/opt/mts')
from ga6.prospective_replay import simulate
p=[(f'd{i}',x,x) for i,x in enumerate([100,100,90,88,85,95,100,105])]
r=simulate(p)
assert r['actions'][0][1]=='SELL' and r['actions'][0][0]=='d3',r
assert r['actions'][1][1]=='BUY' and r['actions'][1][0]=='d6',r
assert r['incremental_net']!=0,r
print('PASS prospective replay',r)
