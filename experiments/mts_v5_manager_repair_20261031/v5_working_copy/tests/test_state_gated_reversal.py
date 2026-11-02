import pytest
from discovery.competitive_ga.reversal_response_diagnostic import run
from discovery.competitive_ga.evolved_selection_policy import SelectionGenes,score
from discovery.competitive_ga.causal_market_state import MarketState
from discovery.competitive_ga.functional_niche_manager import Candidate

def test_state_gate_abstains_despite_positive_stale_edge():
    genes=SelectionGenes(0,1,0,0,min_market_momentum=0.)
    candidate=Candidate('long','GA7',None,.02)
    assert score(genes,candidate,'A',(('A',.2),),.10,market_state=MarketState(-.01,.01,35)) is None
    assert score(genes,candidate,'A',(('A',.2),),.10,market_state=MarketState(.01,.01,31)) is not None
    assert score(genes,candidate,'A',(('A',.2),),.10,market_state=None) is None
    with pytest.raises(ValueError):SelectionGenes(0,1,0,0,min_market_momentum=float('nan'))

def test_reversal_gating_reduces_exposure_and_drawdown_in_fixture():
    result=run()
    gated=result['state_gated'];ungated=result['learned']
    assert gated['entries_after']['NO_ENTRY']>0
    assert gated['entries_after']['GA7']<ungated['entries_after']['GA7']
    assert gated['max_drawdown']<ungated['max_drawdown']
    assert gated['post_boundary_return']>ungated['post_boundary_return']
