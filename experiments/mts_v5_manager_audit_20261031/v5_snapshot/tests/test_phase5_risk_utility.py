import pytest
from engines.portfolio_replay.kernel import Replay, Bar, Signal
from engines.portfolio_replay.risk import RiskSnapshot
from discovery.competitive_ga.action_utility import paired
from discovery.competitive_ga.causal_calibration import Calibrator


def test_incumbent_and_correlated_risk():
    r=Replay(cash=80000,shares={'A':200},pending=[Signal('B','GA6','b',.1)])
    r.risk_snapshot=RiskSnapshot('1',{'A':(.05,.08,'g'),'B':(.05,.08,'g')},max_group_weight=.25,reference_close={'B':100})
    r.day('2',{'A':Bar(100,100),'B':Bar(100,100)})
    assert r.shares['B']==pytest.approx(50)
    assert r.risk_audit[0][1]==[('B','aggregate risk')]


def test_gap_blocks_buy_but_not_exit_and_close_is_unused():
    r=Replay(cash=90000,shares={'A':100},pending=[Signal('A','GA6','a',0),Signal('B','GA7','b',.1)])
    r.risk_snapshot=RiskSnapshot('1',{'A':(.1,.2,'g'),'B':(.1,.2,'h')},reference_close={'B':100})
    r.day('2',{'A':Bar(100,1),'B':Bar(120,999)})
    assert not r.shares
    assert r.risk_audit[0][1]==[('B','open gap')]


def test_missing_incumbent_and_same_day_risk_fail():
    for date,exposures in [('1',{}),('2',{'A':(.1,.1,'g')})]:
        r=Replay(shares={'A':1},risk_snapshot=RiskSnapshot(date,exposures))
        with pytest.raises(ValueError):r.day('2',{'A':Bar(100,100)})


@pytest.mark.parametrize('action,target,price,sign',[('ADD',.2,120,1),('ADD',.2,80,-1),('REDUCE',.05,120,-1),('EXIT',0,80,1)])
def test_paired_utility_and_maturity(action,target,price,sign):
    o=paired(chromosome='x',family='GA7',action=action,decision=0,maturity=2,training_end=2,cash=900,shares=1,target=target,execution_open=100,terminal_close=price)
    assert o.net_r*sign>0
    c=Calibrator(min_samples=1);c.record(o)
    assert c.estimate('x',('GA7_ENTRY',),3) is None
    assert c.estimate('x',o.context,2) is None
    assert c.estimate('x',o.context,3)['edge']==o.net_r
    with pytest.raises(ValueError):paired(chromosome='x',family='GA7',action=action,decision=0,maturity=3,training_end=2,cash=900,shares=1,target=target,execution_open=100,terminal_close=price)


def test_entry_evidence_cannot_authorize_add():
    from discovery.competitive_ga.native_signal_contract import NativeProposal
    from discovery.competitive_ga.causal_manager_proposals import calibrated_proposals
    from discovery.competitive_ga.causal_calibration import TradeOutcome
    c=Calibrator(min_samples=1)
    c.record(TradeOutcome('c',('GA7_ENTRY',),0,1,.9,'shadow'))
    p=NativeProposal('2020-01-05','A','GA7','c','ADD',.09,0.,'net_return_fraction','src','features','2020-01-01')
    assert calibrated_proposals([p],p.decision_date,3,c)==[]


def test_gap_causal_close_parity_split_and_cash():
    results=[]
    for close in (1,1000):
        r=Replay(cash=100,cap=.1,pending=[Signal('A','GA6','a',.1)])
        r.risk_snapshot=RiskSnapshot('1',{'A':(.02,.03,'g')},reference_close={'A':100})
        r.day('2',{'A':Bar(50,close,split=2)})
        results.append(r.ledger)
        assert r.cash>=0
    assert results[0]==results[1]


@pytest.mark.parametrize('bad',[float('nan'),float('inf'),-1,2])
def test_invalid_orders_fail_before_mutation(bad):
    r=Replay(pending=[Signal('A','GA6','c',bad)])
    with pytest.raises(ValueError):r.day('2',{'A':Bar(100,100)})
    assert not r.ledger and r.session==-1


def test_independent_cashflow_oracle():
    # ADD buys one share for 100.10; its next-close value is 120.
    o=paired(chromosome='c',family='GA7',action='ADD',decision=0,maturity=1,training_end=1,cash=900,shares=1,target=.2,execution_open=100,terminal_close=120)
    assert o.net_r==pytest.approx(19.9/1000)
    # EXIT pays .10 sale fee and misses the 20 gain on the original share.
    o=paired(chromosome='c',family='GA7',action='EXIT',decision=0,maturity=1,training_end=1,cash=900,shares=1,target=0,execution_open=100,terminal_close=120)
    assert o.net_r==pytest.approx(-20.1/1000)


@pytest.mark.parametrize('incumbent',[250,300])
def test_unrelated_full_group_does_not_block_other_group_capacity(incumbent):
    # g is full or appreciated over cap; h still has 25% available. The old
    # max-group interpolation either rejected B entirely or let B exceed cap.
    r=Replay(cash=100000-100*incumbent,shares={'A':incumbent},cap=.30,
             pending=[Signal('B','GA6','b',.30)])
    r.risk_snapshot=RiskSnapshot('1',{'A':(.01,.01,'g'),'B':(.01,.01,'h')},
        max_group_weight=.25,reference_close={'B':100})
    r.day('2',{'A':Bar(100,100),'B':Bar(100,100)})
    assert r.shares['B']==pytest.approx(250)
    assert r.shares['A']==incumbent
