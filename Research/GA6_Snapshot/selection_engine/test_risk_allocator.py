from risk_allocator import allocate,RiskPolicy
import numpy as np
D=[f'2024-01-{i:02d}' for i in range(1,32)]+[f'2024-02-{i:02d}' for i in range(1,30)]+[f'2024-03-{i:02d}' for i in range(1,16)]
rng=np.random.default_rng(9)
base=rng.normal(0,.02,len(D))
ret={s:dict(zip(D,(base+rng.normal(0,.001,len(D))) if s.startswith('T') else rng.normal(0,.02,len(D)))) for s in ['T1','T2','T3','T4','H1','H2','H3','H4']}
sectors={s:('Tech' if s.startswith('T') else 'Health') for s in ret}
p=lambda s,i,score,w=.1:dict(symbol=s,chromosome=i,niche='N1',score=score,target_weight=w,evidence_cutoff='2024-03-15')
a=allocate([p('T1',400,2),p('T1',1,1),p('T2',2,1.8),p('T3',3,1.7),p('T4',4,1.6),p('H1',5,1.5)],asof='2024-03-15',cash=100000,nav=100000,holdings={},sector_by_symbol=sectors,trailing_returns=ret)
assert next(x for x in a['orders'] if x['symbol']=='T1')['chromosome']==400
assert 'T4' not in a['proposed_weights']
assert sum(v for s,v in a['proposed_weights'].items() if s.startswith('T'))<=.30000001
assert len(a['shadow_decisions'])==6
assert a['correlated_pairs']
b=allocate([p('T1',400,2,.05),p('H2',7,1.9)],asof='2024-03-15',cash=0,nav=100000,holdings={'T1':.1},sector_by_symbol=sectors,trailing_returns=ret)
assert b['orders'][0]['action']=='REDUCE' and 'H2' not in b['proposed_weights']
try:
 allocate([dict(p('T1',1,1),evidence_cutoff='2024-03-16')],asof='2024-03-15',cash=100000,nav=100000,holdings={},sector_by_symbol=sectors,trailing_returns=ret)
 raise AssertionError('leakage permitted')
except ValueError:pass
print('PASS: context winner #400, sector cap, cluster cap, shadow ledger, no unsettled buying, PIT cutoff')
