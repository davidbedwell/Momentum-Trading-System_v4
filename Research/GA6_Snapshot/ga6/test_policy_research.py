import sys,random
sys.path.insert(0,'/opt/mts')
from ga6.policy_research import evolve
paths=[]
for k in range(60):
 values=[100,101,100,95,90,92,98,105,108,110]
 paths.append([(str(i),v*(1+k/10000),v*(1+k/10000)) for i,v in enumerate(values)])
r=evolve(paths,random.Random(6106),population=8,generations=2)
assert len(r)==2 and r[0]['best']['eligible'] and r[1]['best']['count']==60
print('PASS prospective GA6 policy evolution',r[-1])
