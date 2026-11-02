"""Manager executes owner GA7 partial reduction and reconciles fees/basis."""
import pytest
from engines.portfolio_replay.kernel import Bar
from discovery.competitive_ga.causal_calibration import TradeOutcome
from discovery.competitive_ga.native_signal_contract import NativeProposal
from discovery.competitive_ga.chronological_manager_replay import run

def test_ga7_partial_reduce_then_exit():
    seen=[]
    def producer(date,session,bars,holdings,owners,defense,fillbook):
        seen.append((session,{t:(p.shares,p.basis,p.stop) for t,p in fillbook.positions.items()}))
        if session>=5:return []
        owned=owners.get('AAA')==('GA7','c7')
        action='ENTER' if not owned else ('REDUCE' if session==3 else 'EXIT' if session==4 else 'HOLD')
        weight=.08 if action=='ENTER' else holdings['AAA']/2 if action=='REDUCE' else holdings.get('AAA',0.) if action=='HOLD' else 0.
        return [NativeProposal(date,'AAA','GA7','c7',action,weight,0.,'net_return_fraction','source','features','2020-01-01')]
    days=[]
    for i in range(7):
        outcomes=[TradeOutcome('c7',('GA7_ENTRY',),0,i,.1,'shadow')] if i==1 else []
        days.append((f'2020-01-{i+2:02d}',{'AAA':Bar(100,100)},producer,outcomes,False))
    result=run(days,min_samples=1,stops_by_owner={('GA7','c7'):.015})
    assert [f[2] for f in result['ledger']]==['BUY','SELL','SELL']
    buy,partial,final=result['ledger']
    assert partial[3]==pytest.approx(buy[3]/2)
    assert final[3]==pytest.approx(buy[3]/2)
    assert seen[4][1]['AAA'][2]==.015
    assert seen[4][1]['AAA'][1]==pytest.approx(buy[4]+buy[5]/buy[3])
    assert result['position_basis']=={}
    assert sum(x['pnl'] for x in result['realized'])==pytest.approx(-sum(f[5] for f in result['ledger']))
