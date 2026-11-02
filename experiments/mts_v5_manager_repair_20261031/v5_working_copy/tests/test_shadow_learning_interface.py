from discovery.competitive_ga.shadow_learning_interface import ShadowLearningView
from discovery.competitive_ga.causal_calibration import TradeOutcome

def test_causal_niche_fit_learning_and_uncertainty():
    view=ShadowLearningView(min_samples=2,prior_strength=0)
    for i,r in enumerate((.04,.02,-.01)):
        view.ingest(TradeOutcome('specialist',('A','A',.2),i,i+2,r,'shadow'))
    for i,r in enumerate((.08,-.03)):
        view.ingest(TradeOutcome('generic',('A',None,None),i,i+2,r,'shadow'))
    assert view.snapshot(2)['matured_count']==0
    early=view.snapshot(4)
    assert early['matured_count']==4
    assert (None,'specialist',None,'A','MATCH','NEAR') in early['estimates']
    assert early['estimates'][(None,'generic',None,'A','OTHER','FAR_OR_UNKNOWN')]['samples']==2
    full=view.snapshot(6)
    assert full['matured_count']==5
    assert full['estimates'][(None,'generic',None,'A','OTHER','FAR_OR_UNKNOWN')]['samples']==2
    assert full['estimates'][(None,'specialist',None,'A','MATCH','NEAR')]['samples']==3
