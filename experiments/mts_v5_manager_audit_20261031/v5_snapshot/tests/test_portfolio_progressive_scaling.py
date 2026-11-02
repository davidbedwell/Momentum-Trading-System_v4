from engines.portfolio_replay.kernel import Bar,Signal,Replay
from discovery.competitive_ga.progressive_scaling import ScaleEvidence

def evidence(**changes):
    x=dict(matured_trades=120,forward_folds=4,positive_net_ev=True,historical_mdd=.10,
           current_signal_confirmed=True,position_profitable=True,independent_confirmation=True)
    x.update(changes)
    return ScaleEvidence(**x)

def test_scaling_at_next_open_with_earned_evidence():
    r=Replay()
    bars={'AAA':Bar(100,100)}
    r.day('d1',bars,[Signal('AAA','GA7','a',.10)])
    r.day('d2',bars,[Signal('AAA','GA7','a',.30,scaling_evidence=evidence(),stop_distance=.04,gap_risk=.05)])
    assert abs(r.shares['AAA']*100/(r.cash+r.shares['AAA']*100)-.10)<.001
    r.day('d3',bars)
    assert .29<r.shares['AAA']*100/(r.cash+r.shares['AAA']*100)<.301

def test_unearned_scaling_is_blocked():
    r=Replay()
    bars={'AAA':Bar(100,100)}
    r.day('d1',bars,[Signal('AAA','GA7','a',.10)])
    r.day('d2',bars,[Signal('AAA','GA7','a',.30)])
    r.day('d3',bars)
    assert r.shares['AAA']*100/(r.cash+r.shares['AAA']*100)<.11

def test_existing_large_position_not_cut_without_instruction():
    r=Replay(cash=70000,shares={'AAA':300})
    bars={'AAA':Bar(100,100)}
    r.day('d1',bars)
    assert r.shares['AAA']==300

def test_defense_liquidates_exceptional_position():
    r=Replay(cash=70000,shares={'AAA':300})
    r.day('d1',{'AAA':Bar(100,100)},defense=True)
    assert not r.shares

def test_scaling_requires_risk_evidence():
    import pytest
    r=Replay()
    b={'AAA':Bar(100,100)}
    r.day('d1',b,[Signal('AAA','GA7','a',.1,scaling_evidence=evidence())])
    with pytest.raises(ValueError,match='risk inputs'):
        r.day('d2',b)
