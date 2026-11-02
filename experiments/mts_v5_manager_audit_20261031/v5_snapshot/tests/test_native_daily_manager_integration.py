"""End-to-end research manager adapter smoke with genuine GA6 native contract.
No invented calibration: zero matured outcomes means no buys.
"""
from discovery.competitive_ga.native_daily_replay_adapter import daily_producer
from discovery.competitive_ga.chronological_manager_replay import run
from discovery.competitive_ga.native_signal_contract import NativeProposal
from engines.portfolio_replay.kernel import Bar

def test_native_daily_producer_runs_through_manager_without_future_calibration():
    dates=['2026-01-12','2026-01-13','2026-01-14']
    def ga6(date,held,defensive):
        return [NativeProposal(date,'AAA','GA6','c1','ENTER',.1,.1,
            'entry_equity_fraction','source','snapshot','2026-01-09')]
    inputs={d:dict(trained_through='2026-01-09',source_hash='source',
        snapshot_hash='snapshot',ga6_producer=ga6) for d in dates}
    native=daily_producer(inputs)
    days=[(d,{'AAA':Bar(100+i,101+i)},native,[],False)
          for i,d in enumerate(dates)]
    result=run(days)
    assert len(result['decisions'])==3
    assert all(day['native']==1 and day['eligible']==0 for day in result['decisions'])
    assert result['ledger']==[]
    assert len(result['nav'])==3
