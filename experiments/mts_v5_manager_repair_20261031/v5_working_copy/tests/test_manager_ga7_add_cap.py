"""GA7 ADD within learning cap: executed fill and weighted cost basis."""
import pytest
from engines.portfolio_replay.kernel import Bar
from discovery.competitive_ga.causal_calibration import TradeOutcome
from discovery.competitive_ga.native_signal_contract import NativeProposal
from discovery.competitive_ga.chronological_manager_replay import run

def test_ga7_add_under_cap_updates_basis_and_shares():
    snapshots=[]
    def producer(date,session,bars,holdings,owners,defense,book):
        snapshots.append((session,{t:(p.shares,p.basis,p.stop) for t,p in book.positions.items()}))
        if session>=5:return []
        owned=owners.get('A')==('GA7','c7')
        action='ADD' if owned and session==3 else 'HOLD' if owned else 'ENTER'
        target=.09 if action=='ADD' else holdings['A'] if action=='HOLD' else .06
        return [NativeProposal(date,'A','GA7','c7',action,target,0.,'net_return_fraction','src','features','2020-01-01')]
    days=[]
    for i in range(7):
        outcomes=[TradeOutcome('c7',('GA7_ENTRY',),0,i,.1,'shadow'),TradeOutcome('c7',('GA7_UTILITY','ADD'),0,i,.05,'shadow')] if i==1 else []
        days.append((f'2020-01-{i+2:02d}',{'A':Bar(100 if i<4 else 110,100 if i<4 else 110)},producer,outcomes,False))
    result=run(days,min_samples=1,stops_by_owner={('GA7','c7'):.013})
    buys=[x for x in result['ledger'] if x[2]=='BUY']
    assert len(buys)==2
    assert buys[1][3]>0
    qty=sum(x[3] for x in buys)
    basis=sum(x[3]*x[4]+x[5] for x in buys)/qty
    assert result['position_basis']['A']==pytest.approx(basis)
    assert snapshots[4][1]['A'][2]==.013
    assert result['nav'][-1][3]['A']==pytest.approx(qty)
