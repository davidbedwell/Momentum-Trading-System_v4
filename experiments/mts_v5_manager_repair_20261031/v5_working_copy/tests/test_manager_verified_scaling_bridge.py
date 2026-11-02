"""Calibrated GA7 manager ADD carries evidence into replay kernel."""
import pytest
from engines.portfolio_replay.kernel import Bar
from discovery.competitive_ga.causal_calibration import TradeOutcome
from discovery.competitive_ga.native_signal_contract import NativeProposal
from discovery.competitive_ga.chronological_manager_replay import run
from discovery.competitive_ga.causal_scaling_evidence import FoldRecord

def test_manager_verified_scale_to_twenty_percent():
    def producer(date,session,bars,holdings,owners,defense):
        if session>=5:return []
        owned=owners.get('A')==('GA7','c7')
        action='ADD' if owned else 'ENTER'
        return [NativeProposal(date,'A','GA7','c7',action,.20 if owned else .07,0.,'net_return_fraction','src','features','2020-01-01')]
    days=[]
    for i in range(7):
        outcomes=[TradeOutcome('c7',('GA7_ENTRY',),0,i,.1,'shadow'),TradeOutcome('c7',('GA7_UTILITY','ADD'),0,i,.05,'shadow')] if i==1 else []
        days.append((f'2020-01-{i+2:02d}',{'A':Bar(100,101 if i>=4 else 100)},producer,outcomes,False))
    folds={2:[FoldRecord('GA7','c7','f1',0,2,.10,.10,120,'shadow',True,0,1,'ledger-f1')]}
    result=run(days,min_samples=1,stops_by_owner={('GA7','c7'):.02},
        scaling_by_owner={('A','GA7','c7'):{'stop_distance':.02,'gap_risk':.03}},folds_by_session=folds)
    assert len([x for x in result['ledger'] if x[2]=='BUY'])>=3
    assert result['nav'][-1][3]['A']>140  # scaling occurs after the position becomes profitable
