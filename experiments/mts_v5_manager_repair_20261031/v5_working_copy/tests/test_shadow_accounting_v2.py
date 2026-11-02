from discovery.competitive_ga.shadow_accounting_v2 import ShadowLedger
from discovery.competitive_ga.native_signal_contract import NativeProposal
from engines.portfolio_replay.kernel import Bar

def p(action,target):
    return NativeProposal('2026-01-12','AAA','GA6','c',action,target,.1,
        'entry_equity_fraction','src','snap','2026-01-11')

def test_partial_reduction_then_exit_net_of_fees():
    s=ShadowLedger()
    s.at_close([p('ENTER',.1)])
    assert not s.at_open(1,{'AAA':Bar(100,100)})
    s.at_close([p('REDUCE',.05)])
    assert not s.at_open(2,{'AAA':Bar(110,110)})
    assert abs(s.positions[('GA6','c','AAA')]['shares']-.5)<1e-12
    s.at_close([p('EXIT',0)])
    out=s.at_open(3,{'AAA':Bar(120,120)})
    expected=(.5*(110*.999-100*1.001)+.5*(120*.999-100*1.001))/(100*1.001)
    assert abs(out[0].net_r-expected)<1e-12
    assert out[0].maturity_session==3
