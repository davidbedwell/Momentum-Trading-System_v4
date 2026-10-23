import sys
sys.path.insert(0,'/opt/mts')
from ga6.portfolio_counterfactuals import compare
common={'membership':True,'earnings_allowed':True,'risk_allowed':True,'weight':.6}
orders=[dict(common,decision_date='2020-01-01',ticker='A',action='ENTER',next_open=100),dict(common,decision_date='2020-01-01',ticker='B',action='ENTER',next_open=100),dict(common,decision_date='2020-01-02',ticker='A',action='EXIT',next_open=110),dict(common,decision_date='2020-01-03',ticker='B',action='ENTER',next_open=100)]
r=compare(orders,capital=1000,max_positions=1)
assert r['executed_entries']==2 and r['executed_exits']==1
assert any(x[2]=='capacity' for x in r['rejected'])
assert r['cash']>=0
print('PASS capital competition, exit frees capacity, next-open execution')
