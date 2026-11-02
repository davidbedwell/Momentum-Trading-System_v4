from engines.portfolio_replay.kernel import Replay,Bar,Signal
from engines.portfolio_replay.defense_router import DefenseDecision,DefenseRouter
import pytest

def test_defense_liquidates_and_blocks_pending_and_new_signals():
    router=DefenseRouter()
    r=Replay()
    bars={'AAA':Bar(100,100)}
    r.day('2026-01-01',bars,[Signal('AAA','GA7','a',.10)])
    r.day('2026-01-02',bars,[Signal('AAA','GA7','a',.30)])
    assert r.shares
    decision=DefenseDecision('2026-01-02','2026-01-03',True,('A_v2',))
    r.day('2026-01-03',bars,[Signal('AAA','GA7','a',.30)],defense=router.apply('2026-01-03',decision))
    assert not r.shares and not r.pending
    r.day('2026-01-04',bars,[Signal('AAA','GA7','a',.10)],defense=router.apply('2026-01-04'))
    assert not r.shares and not r.pending

def test_recovery_restarts_at_normal_entry():
    router=DefenseRouter()
    router.apply('2026-01-03',DefenseDecision('2026-01-02','2026-01-03',True,('B1',)))
    recovery=DefenseDecision('2026-01-04','2026-01-05',False,(),True)
    assert not router.apply('2026-01-05',recovery)
    r=Replay()
    bars={'AAA':Bar(100,100)}
    r.day('2026-01-05',bars,[Signal('AAA','GA7','a',.30)])
    r.day('2026-01-06',bars)
    assert r.shares['AAA']*100/(r.cash+r.shares['AAA']*100)<.11

def test_no_future_defense_or_same_day_execution():
    router=DefenseRouter()
    with pytest.raises(ValueError,match='next session'):
        DefenseDecision('2026-01-03','2026-01-03',True,('C',))
    decision=DefenseDecision('2026-01-02','2026-01-03',True,('C',))
    with pytest.raises(ValueError,match='future defense'):
        router.apply('2026-01-02',decision)
