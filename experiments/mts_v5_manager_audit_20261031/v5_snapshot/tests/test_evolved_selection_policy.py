from discovery.competitive_ga.evolved_selection_policy import SelectionGenes,score
from discovery.competitive_ga.functional_niche_manager import Candidate

def test_evolvable_fit_vs_ev_and_abstain():
    near=Candidate('near','GA6','A',.02)
    far=Candidate('far','GA7',None,.02)
    m=(('A',.2),)
    fit=SelectionGenes(.2,1,0,0)
    ev=SelectionGenes(0,1,0,0)
    assert score(fit,near,'A',m,.03)>score(fit,far,'A',m,.15)
    assert score(ev,far,'A',m,.15)>score(ev,near,'A',m,.03)
    assert score(SelectionGenes(0,1,0,.2),far,'A',m,.15) is None

def test_matured_snapshot_changes_ranking_without_future_data():
    c=Candidate('near','GA6','A',.02)
    genes=SelectionGenes(0,1,1,0)
    key=('GA6','near',None,'A','MATCH','NEAR')
    snapshot={'estimates':{key:{'net_ev':.02,'uncertainty':.03}}}
    assert score(genes,c,'A',(('A',.2),),.5,snapshot) is None
    assert score(genes,c,'A',(('A',.2),),.5,None)==.5
