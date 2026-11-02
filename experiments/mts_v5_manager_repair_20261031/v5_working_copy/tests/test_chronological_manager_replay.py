import pytest
from engines.portfolio_replay.kernel import Bar
from discovery.competitive_ga.causal_calibration import TradeOutcome
from discovery.competitive_ga.native_signal_contract import NativeProposal
from discovery.competitive_ga.chronological_manager_replay import run
from discovery.competitive_ga.manager_policy_v2 import Genes


def signal(date):
    return NativeProposal(date,'ABC','GA6','c1','ENTER',.08,.1,
        'entry_equity_fraction','source','features','2020-01-01')


def test_no_same_day_outcome_leak_and_next_open_fills():
    days=[]
    for i in range(6):
        date=f'2020-01-{i+2:02d}'
        outcomes=[TradeOutcome('c1',('GA6_ENTRY',),0,i,.10,'shadow')] if i in (1,2) else []
        days.append((date,{'ABC':Bar(100,100)},[signal(date)],outcomes,False))
    result=run(days,min_samples=2,genes=Genes(min_edge=.01))
    assert [d['eligible'] for d in result['decisions']]==[0,0,0,1,1,1]
    assert result['decisions'][3]['orders']==1
    assert result['ledger'][0][0]=='2020-01-06'
    assert result['ledger'][0][2]=='BUY'


def test_future_maturity_rejected():
    day=('2020-01-02',{'ABC':Bar(100,100)},[],
         [TradeOutcome('c1',('GA6_ENTRY',),0,2,.1,'shadow')],False)
    with pytest.raises(ValueError,match='maturity'):
        run([day])


def test_duplicate_date_rejected():
    day=('2020-01-02',{'ABC':Bar(100,100)},[],[],False)
    with pytest.raises(ValueError,match='strictly increasing'):
        run([day,day])
