"""Full manager chronology: matured evidence -> buy fill -> owner exit -> sell fill."""
from engines.portfolio_replay.kernel import Bar
from discovery.competitive_ga.causal_calibration import TradeOutcome
from discovery.competitive_ga.native_signal_contract import NativeProposal
from discovery.competitive_ga.chronological_manager_replay import run


def test_postfill_native_ga7_exit_executes_next_open():
    seen=[]
    def producer(date,session,bars,holdings,owners,defense):
        seen.append((session,dict(holdings),dict(owners)))
        if session>=4:return []
        held=owners.get('AAA')==('GA7','g7')
        action='EXIT' if held else 'ENTER'
        return [NativeProposal(date,'AAA','GA7','g7',action,0. if held else .07,
            0.,'net_return_fraction','source','features','2020-01-01')]
    days=[]
    for i in range(6):
        outcomes=[TradeOutcome('g7',('GA7_ENTRY',),0,i,.1,'shadow')] if i==1 else []
        days.append((f'2020-01-{i+2:02d}',{'AAA':Bar(100,100)},producer,outcomes,False))
    result=run(days,min_samples=1,stops_by_owner={('GA7','g7'):.02})
    assert [(row[0],row[2]) for row in result['ledger']]==[
        ('2020-01-05','BUY'),('2020-01-06','SELL')]
    assert seen[3][2]=={'AAA':('GA7','g7')}
    assert seen[4][1]=={}
    assert result['nav'][-1][3]=={}
