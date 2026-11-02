import pytest
from engines.portfolio_replay.kernel import Bar
from discovery.competitive_ga.causal_calibration import TradeOutcome
from discovery.competitive_ga.causal_scaling_evidence import FoldRecord
from discovery.competitive_ga.native_signal_contract import NativeProposal
from discovery.competitive_ga.chronological_manager_replay import run
from discovery.competitive_ga.progressive_scaling import ScaleEvidence

def test_fold_evidence_must_mature_before_manager_add():
    def native(date,session,bars,holdings,owners,defense):
        if session>=8:return []
        owned=owners.get('A')==('GA7','c7')
        return [NativeProposal(date,'A','GA7','c7','ADD' if owned else 'ENTER',.20 if owned else .07,0.,'net_return_fraction','src','features','2020-01-01')]
    days=[]
    for i in range(10):
        outcomes=[TradeOutcome('c7',('GA7_ENTRY',),0,i,.1,'shadow'),TradeOutcome('c7',('GA7_UTILITY','ADD'),0,i,.05,'shadow')] if i==1 else []
        days.append((f'2020-01-{i+2:02d}',{'A':Bar(100,110 if i>=3 else 100)},native,outcomes,False))
    folds={5:[FoldRecord('GA7','c7','fold1',0,5,.1,.10,120,'shadow',True,1,4,'ledger-f1')]}
    scale={('A','GA7','c7'):{'evidence':ScaleEvidence(999,9,True,.01,True,True,True),'stop_distance':.02,'gap_risk':.03}}
    # Fabricated caller evidence cannot bypass the absence of matured folds.
    no_folds=run(days,min_samples=1,stops_by_owner={('GA7','c7'):.02},scaling_by_owner=scale,folds_by_session={})
    assert len([f for f in no_folds['ledger'] if f[2]=='BUY'])==1
    result=run(days,min_samples=1,stops_by_owner={('GA7','c7'):.02},scaling_by_owner=scale,folds_by_session=folds)
    buys=[f for f in result['ledger'] if f[2]=='BUY']
    assert len(buys)==2
    assert buys[1][0]>days[5][0]
    assert result['nav'][-1][3]['A']>100
