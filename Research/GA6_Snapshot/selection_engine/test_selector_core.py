from selector_core import Proposal,compete
p=lambda id,s,action,ev,cutoff='2024-06-01':Proposal(id,s,'2024-06-05',action,'NICHE-0001',ev,.8,.001,.1,cutoff)
a=compete([p(1,'AAA','ENTER',.04),p(2,'BBB','ENTER',.02)],asof='2024-06-05',cash=10000,nav=100000)
assert a['orders'][0]['symbol']=='AAA' and a['orders'][0]['incremental_weight']<.1
assert len(a['orders'])==1
b=compete([p(3,'AAA','EXIT',0),p(4,'BBB','ENTER',.04)],asof='2024-06-05',cash=10000,nav=100000,existing_weights={'AAA':.2})
assert b['orders'][0]['action']=='REDUCE_OR_EXIT'
try:compete([p(5,'AAA','ENTER',.04,'2024-06-06')],asof='2024-06-05',cash=100000,nav=100000);raise RuntimeError('leakage not blocked')
except AssertionError:pass
print('PASS: cash limit, competition, exit precedence, future evidence rejected')
