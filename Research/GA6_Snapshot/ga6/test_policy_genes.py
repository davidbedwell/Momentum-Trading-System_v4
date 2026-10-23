import sys,random
sys.path.insert(0,'/opt/mts')
from ga6.policy_genes import fresh,mutate
r=random.Random(6106)
seen=set()
for _ in range(1000):
 g=fresh(r);assert g.valid();seen.add(g.identity())
 for j in range(20):
  g=mutate(g,r);assert g.valid();g.policy()
assert len(seen)>950
print('PASS fresh GA6 policy genetics and 20000 mutations')
