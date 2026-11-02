import csv
from engines.portfolio_replay.historical_defense import HistoricalDefense,load_tape
from engines.portfolio_replay.kernel import Replay,Bar,Signal

def test_frozen_tape_loads_and_is_chronological():
    ds=load_tape()
    assert len(ds)>1000
    assert all(d.decided_at<d.effective_at for d in ds)
    assert any(d.defensive for d in ds)
    assert any(d.recovery_authorized for d in ds)

def test_actual_tape_liquidation_and_recovery():
    ds=load_tape()
    entry=next(d for d in ds if d.defensive and d.triggers)
    router=HistoricalDefense()
    before=router.state(entry.decided_at)
    assert router.state(entry.effective_at)
    r=Replay(cash=90000,shares={'AAA':100})
    r.day(entry.effective_at,{'AAA':Bar(100,100)},defense=True)
    assert not r.shares
    recovery=next(d for d in ds if d.recovery_authorized and d.decided_at>entry.decided_at)
    assert not router.state(recovery.effective_at)
    r.day(recovery.effective_at,{'AAA':Bar(100,100)},[Signal('AAA','GA6','x',.30)],defense=False)
    from datetime import date,timedelta
    r.day(str(date.fromisoformat(recovery.effective_at)+timedelta(days=1)),{'AAA':Bar(100,100)})
    assert r.shares['AAA']*100/(r.cash+r.shares['AAA']*100)<.11

def test_future_tape_row_does_not_affect_earlier_state():
    ds=load_tape()
    first=next(d for d in ds if d.defensive and d.triggers)
    router=HistoricalDefense()
    assert not router.state(first.decided_at)
    assert router.state(first.effective_at)
