import pytest
from discovery.competitive_ga.funded_shadow import FundedShadow
from discovery.competitive_ga.native_signal_contract import NativeProposal
from engines.portfolio_replay.kernel import Bar

D=('2026-01-02','2026-01-05','2026-01-06','2026-01-07','2026-01-08')
O=('GA6','c')


def p(i,action,target,ticker='A',owner=O):
    return NativeProposal(D[i],ticker,*owner,action,target,0,'entry_equity_fraction','s','h','2025-12-31')


def test_owner_funding_is_independent_and_sale_cannot_fund_same_open():
    b=FundedShadow([O,('GA6','other')],sessions=D,capital=1000,fee=0)
    bars={t:Bar(10,10) for t in ('A','B','C','D','E')}
    b.open_session(0,bars)
    b.close_session(0,[p(0,'ENTER',.3,t) for t in 'ABCD']+[p(0,'ENTER',.3,'A',('GA6','other'))])
    b.open_session(1,bars)
    assert b.cash[O]==0 and b.cash[('GA6','other')]==700
    assert sum(v['shares'] for k,v in b.positions.items() if k[:2]==O)==100
    b.close_session(1,[p(1,'EXIT',0,'A'),p(1,'ENTER',.3,'E')])
    matured=b.open_session(2,bars)
    assert len(matured)==1 and (O+('E',)) not in b.positions
    assert b.unsettled[O]==[(3,300)] and b.cash[O]==0
    assert b.nav(O,bars)==1000
    b.close_session(2,[p(2,'ENTER',.3,'E')])
    b.open_session(3,bars)
    assert b.positions[O+('E',)]['shares']==30
    assert b.cash[O]==0


def test_fees_add_reduce_split_dividend_and_matured_pnl_reconcile():
    b=FundedShadow([O],sessions=D,capital=1000,fee=.001)
    bars={'A':Bar(100,100)}
    b.open_session(0,bars);b.close_session(0,[p(0,'ENTER',.1)])
    b.open_session(1,bars);b.close_session(1,[p(1,'ADD',.2)])
    b.open_session(2,bars)
    b.close_session(2,[p(2,'REDUCE',.1)])
    split={'A':Bar(50,50,dividend=1,split=2)}
    b.open_session(3,split)
    state=b.native_states(split)[O]['A']
    assert state['entry']==50 and state['weight']==pytest.approx(state['shares']*50/b.nav(O,split))
    b.close_session(3,[p(3,'EXIT',0)])
    matured=b.open_session(4,{'A':Bar(55,55)})
    assert len(matured)==1 and not b.positions
    pnl=b.nav(O,{'A':Bar(55,55)})-1000
    cost=sum(q*price+fee for _,_,side,q,price,fee in b.fills if side=='BUY')
    assert matured[0].net_r==pytest.approx(pnl/cost)


@pytest.mark.parametrize('lag',[0,1,2])
def test_settlement_obeys_explicit_sessions(lag):
    b=FundedShadow([O],sessions=D,fee=0,settlement_sessions=lag)
    bars={'A':Bar(100,100)}
    b.open_session(0,bars);b.close_session(0,[p(0,'ENTER',.1)])
    b.open_session(1,bars);b.close_session(1,[p(1,'EXIT',0)])
    b.open_session(2,bars)
    assert b.cash[O]==90000 and b.unsettled[O]
    b.close_session(2,[]);b.open_session(3,bars)
    assert b.cash[O]==(100000 if lag<2 else 90000)
    b.close_session(3,[]);b.open_session(4,bars)
    assert b.cash[O]==100000


def test_ga4_cannot_get_funded_exit_semantics_by_default():
    with pytest.raises(ValueError,match='GA4 blocked'):FundedShadow([('GA4','x')],sessions=D)


def test_chronology_hold_does_not_rebalance_and_filled_weights_drift():
    b=FundedShadow([O],sessions=D,fee=0)
    bars={'A':Bar(100,100)}
    with pytest.raises(ValueError):b.open_session(1,bars)
    b.open_session(0,bars);b.close_session(0,[p(0,'ENTER',.1)])
    b.open_session(1,bars)
    b.close_session(1,[p(1,'HOLD',.1)])
    b.open_session(2,{'A':Bar(200,200)})
    assert len(b.fills)==1
    assert b.native_states({'A':Bar(200,200)})[O]['A']['weight']==pytest.approx(2/11)
    with pytest.raises(ValueError,match='date'):b.close_session(2,[p(1,'EXIT',0)])


def test_funded_shadow_integrates_with_rejected_manager_native_callback():
    from discovery.competitive_ga.chronological_manager_replay import run
    b=FundedShadow([O],sessions=D[:3],fee=0)
    def native(date,session,bars,defense,ledger):
        held=ledger.native_states(bars).get(O,{})
        if session==0:return [p(session,'ENTER',.1)]
        if held:return [p(session,'EXIT',0)]
        return []
    result=run([(d,{'A':Bar(100,100)},[],[],False) for d in D[:3]],shadow_book=b,shadow_native=native)
    assert result['ledger']==[] and result['shadow_completed']==1
    assert b.cash[O]==90000 and b.unsettled[O]==[(3,10000)]
    assert b.completed[0].net_r==0
