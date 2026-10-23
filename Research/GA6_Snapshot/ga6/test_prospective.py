import sys
sys.path.insert(0,'/opt/mts')
from ga6.prospective_policy import Policy,ExitReentry
p=ExitReentry(Policy(trigger=.05,recovery=.5,min_wait=1,max_wait=3))
assert p.close(100) is None
assert p.open(99) is None
assert p.close(90)=='SELL'
assert p.open(88)=='SELL'
assert p.out
assert p.close(87) is None
assert p.open(90) is None
assert p.close(95)=='BUY'
assert p.open(96)=='BUY'
assert not p.out
print('PASS no-lookahead next-open policy')
