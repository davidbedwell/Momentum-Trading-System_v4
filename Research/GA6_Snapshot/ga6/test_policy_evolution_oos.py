import sys,random
sys.path.insert(0,'/opt/mts')
from ga6.policy_evolution_oos import train_validate
paths=[]
for k in range(120):
 y='2020' if k<60 else '2021'
 vals=[100,99,95,90,92,98,103,107]
 paths.append([(f'{y}-01-{i+1:02d}',v,v) for i,v in enumerate(vals)])
r=train_validate(paths,random.Random(6106),'2021-01-01',8,2)
assert r['eligible'] and r['train']['count']==60 and r['validation']['count']==60,r
print('PASS train-only policy selection and untouched validation',r['genes'])
