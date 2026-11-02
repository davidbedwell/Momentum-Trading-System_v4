import pytest
from engines.portfolio_replay.kernel import Bar
from discovery.competitive_ga.causal_calibration import TradeOutcome
from discovery.competitive_ga.native_signal_contract import NativeProposal
from discovery.competitive_ga.chronological_manager_replay import run


def signal(date):
    return NativeProposal(date,'ABC','GA6','c1','ENTER',.08,.1,
        'entry_equity_fraction','source','features','2020-01-01')


def test_missing_held_bar_fails_before_nav_is_valued():
    days=[]
    for i in range(5):
        date=f'2020-01-{i+2:02d}'
        outcomes=[TradeOutcome('c1',('GA6_ENTRY',),0,i,.1,'shadow')] if i==1 else []
        bars={'ABC':Bar(100,100)} if i<4 else {'XYZ':Bar(100,100)}
        days.append((date,bars,[signal(date)] if i<4 else [],outcomes,False))
    with pytest.raises(ValueError,match='missing held-position bars'):
        run(days,min_samples=1)


def test_invalid_outcome_fails_before_any_execution():
    days=[('2020-01-02',{'ABC':Bar(100,100)},[],
           [TradeOutcome('c1',('GA6_ENTRY',),0,2,.1,'shadow')],False)]
    with pytest.raises(ValueError,match='maturity'):
        run(days)


def test_empty_session_bars_fail_closed():
    with pytest.raises(ValueError,match='empty session bars'):
        run([('2020-01-02',{},[],[],False)])
