import pytest
from discovery.competitive_ga.causal_market_state import state_from_closes
from discovery.competitive_ga.evolved_selection_policy import SelectionGenes,score
from discovery.competitive_ga.functional_niche_manager import Candidate

def test_market_state_no_future_and_state_sensitive_ranking():
    up=state_from_closes([100,102,104,106,108,110],5)
    down=state_from_closes([110,108,106,104,102,100],5)
    assert up.momentum>0 and down.momentum<0
    with pytest.raises(ValueError):state_from_closes([100,102,104,106,108,110,112],5)
    g=SelectionGenes(0,1,0,0,2,0)
    c=Candidate('a','GA6','A',.02)
    assert score(g,c,'A',(('A',.2),),.05,market_state=up)>score(g,c,'A',(('A',.2),),.05,market_state=down)
