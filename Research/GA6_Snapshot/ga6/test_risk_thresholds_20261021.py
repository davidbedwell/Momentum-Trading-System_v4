from ga6.position_equity_risk_20261021 import PositionRisk
def close(a,b):assert abs(a-b)<1e-8,(a,b)
r=PositionRisk(100000)
r.buy(100,100)
assert not r.mark(91)['reassess']
assert r.mark(90)['reassess'] and not r.forced_exit
r.buy(100,90)
close(r.entry_equity,100000)
assert r.mark(90)['reassess'] and not r.forced_exit
r.sell(100,90)
assert not r.mark(90)['mandatory_exit']
assert r.mark(70)['mandatory_exit']
try:r.buy(1,75);raise AssertionError('forced exit allowed scaling')
except ValueError:pass
s=PositionRisk(100000);s.buy(1000,100)
assert s.mark(99)['reassess']
assert s.mark(98)['mandatory_exit']
print('PASS: 1% reassess, scale-in allowed, partial sell realized+unrealized, 2% forced, no reset')
