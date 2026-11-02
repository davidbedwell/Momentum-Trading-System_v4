from discovery.competitive_ga.shadow_learning_interface import ShadowLearningView
from discovery.competitive_ga.causal_calibration import TradeOutcome
from discovery.competitive_ga.evolved_selection_policy import SelectionGenes,score
from discovery.competitive_ga.functional_niche_manager import Candidate

def test_matured_native_shadow_changes_selection_without_future_leak():
    view=ShadowLearningView(min_samples=2,prior_strength=0)
    specialist=Candidate('shared','GA6','A',.02)
    generalist=Candidate('shared','GA7',None,.02)
    genes=SelectionGenes(0,1,0,0)
    matches=(('A',.2),)
    def selected(snapshot):
        a=score(genes,specialist,'A',matches,.04,snapshot)
        b=score(genes,generalist,'A',matches,.03,snapshot)
        return 'GA6' if a is not None and (b is None or a>b) else 'GA7'
    assert selected(view.snapshot(3))=='GA6'
    for i in range(3):
        view.ingest(TradeOutcome('shared',('A','A',.2),i,i+4,-.02,'shadow',f'A{i}','GA6'))
        view.ingest(TradeOutcome('shared',('A',None,None),i,i+4,.05,'shadow',f'B{i}','GA7'))
    assert selected(view.snapshot(4))=='GA6'
    assert selected(view.snapshot(7))=='GA7'
    assert ('GA6','shared',None,'A','MATCH','NEAR') in view.snapshot(7)['estimates']
    assert ('GA7','shared',None,'A','OTHER','FAR_OR_UNKNOWN') in view.snapshot(7)['estimates']
