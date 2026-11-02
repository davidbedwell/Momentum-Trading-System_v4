"""Deterministic accounting fixtures, never strategy/performance evidence."""
import pytest
from discovery.competitive_ga.shadow_accounting_v2 import ShadowLedger
from discovery.competitive_ga.native_signal_contract import NativeProposal
from discovery.competitive_ga.chronological_manager_replay import run
from discovery.competitive_ga.causal_calibration import TradeOutcome
from engines.portfolio_replay.kernel import Bar


def proposal(action,target,cid='owner'):
    return NativeProposal('2026-01-02','A','GA6',cid,action,target,.1,
                          'entry_equity_fraction','fixture','fixture','2026-01-01')


def test_shadow_add_reduce_exit_fee_cashflow_identity():
    book=ShadowLedger()
    cashflows=[]
    for session,(action,target,price) in enumerate([
            ('ENTER',.1,100),('ADD',.2,120),('REDUCE',.1,130),('EXIT',0,140)],1):
        book.at_close([proposal(action,target)])
        outcomes=book.at_open(session,{'A':Bar(price,price)})
        cashflows.append((-1 if action in ('ENTER','ADD') else 1)*price*
                         (1.001 if action in ('ENTER','ADD') else .999))
        if action!='EXIT':assert outcomes==[]
    assert outcomes[0].net_r==pytest.approx(sum(cashflows)/(100*1.001+120*1.001))
    assert book.positions=={}


def test_foreign_calibrated_chromosome_cannot_exit_incumbent():
    def native(date,session,bars,holdings,owners,defense):
        p=proposal('EXIT' if holdings else 'ENTER',0 if holdings else .1,
                   'foreign' if holdings else 'owner')
        from dataclasses import replace
        return [replace(p,decision_date=date)]
    days=[]
    for i in range(6):
        outcomes=[TradeOutcome(c,('GA6_ENTRY',),0,1,.1,'shadow')
                  for c in ('owner','foreign')] if i==1 else []
        days.append((f'2026-01-{i+2:02d}',{'A':Bar(100,100)},native,outcomes,False))
    result=run(days,min_samples=1)
    assert [f[2] for f in result['ledger']]==['BUY']
    assert 'A' in result['position_basis']


def test_manager_split_reconciles_fill_basis_and_shares():
    from dataclasses import replace
    def native(date,session,bars,holdings,owners,defense):
        return [] if holdings else [replace(proposal('ENTER',.1),decision_date=date)]
    days=[]
    for i in range(6):
        outcomes=[TradeOutcome('owner',('GA6_ENTRY',),0,1,.1,'shadow')] if i==1 else []
        price=50 if i>=4 else 100
        days.append((f'2026-01-{i+2:02d}',{'A':Bar(price,price,split=2 if i==4 else 1)},native,outcomes,False))
    result=run(days,min_samples=1)
    assert result['position_basis']['A']==pytest.approx(50.05)
    assert result['nav'][-1][1]==pytest.approx(result['nav'][3][1])


@pytest.mark.parametrize('bad',[float('nan'),float('inf')])
def test_replay_rejects_nonfinite_market_prices(bad):
    from engines.portfolio_replay.kernel import Replay
    with pytest.raises(ValueError,match='invalid bar'):
        Replay().day('2026-01-02',{'A':Bar(bad,100)})
