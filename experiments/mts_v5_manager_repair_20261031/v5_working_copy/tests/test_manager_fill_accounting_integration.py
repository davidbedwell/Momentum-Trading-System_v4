from engines.portfolio_replay.kernel import Bar
from discovery.competitive_ga.causal_calibration import TradeOutcome
from discovery.competitive_ga.native_signal_contract import NativeProposal
from discovery.competitive_ga.chronological_manager_replay import run
import pytest

def test_manager_buy_sell_fee_reconciliation():
    def producer(date,session,bars,holdings,owners,defense):
        if session>=4:return []
        action='EXIT' if owners.get('AAA')==('GA7','g7') else 'ENTER'
        return [NativeProposal(date,'AAA','GA7','g7',action,0. if action=='EXIT' else .07,0.,'net_return_fraction','source','features','2020-01-01')]
    days=[]
    for i in range(6):
        outcomes=[TradeOutcome('g7',('GA7_ENTRY',),0,i,.1,'shadow')] if i==1 else []
        days.append((f'2020-01-{i+2:02d}',{'AAA':Bar(100,110 if i>=4 else 100)},producer,outcomes,False))
    result=run(days,min_samples=1,stops_by_owner={('GA7','g7'):.02})
    assert [row[2] for row in result['ledger']]==['BUY','SELL']
    buy,sell=result['ledger']
    quantity=buy[3]
    expected=quantity*(sell[4]-buy[4])-buy[5]-sell[5]
    assert sum(row['pnl'] for row in result['realized'])==pytest.approx(expected)
    assert result['position_basis']=={}
    assert result['nav'][-1][3]=={}
