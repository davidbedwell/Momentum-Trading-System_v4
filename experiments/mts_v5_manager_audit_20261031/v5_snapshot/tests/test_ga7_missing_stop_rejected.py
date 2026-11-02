import pytest
from engines.portfolio_replay.kernel import Bar
from discovery.competitive_ga.native_signal_contract import NativeProposal
from discovery.competitive_ga.causal_calibration import TradeOutcome
from discovery.competitive_ga.chronological_manager_replay import run

def test_ga7_missing_stop_fails_closed_at_fill():
    def native(date,session,bars,holdings,owners,defense):
        return [NativeProposal(date,'A','GA7','c7','ENTER',.07,0.,'net_return_fraction','source','features','2020-01-01')]
    days=[]
    for i in range(5):
        outcomes=[TradeOutcome('c7',('GA7_ENTRY',),0,i,.1,'shadow')] if i==1 else []
        days.append((f'2020-01-{i+2:02d}',{'A':Bar(100,100)},native,outcomes,False))
    with pytest.raises(ValueError,match='GA7 chromosome stop configuration required'):
        run(days,min_samples=1)
