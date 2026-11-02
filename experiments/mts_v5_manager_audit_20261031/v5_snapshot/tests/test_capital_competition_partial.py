from discovery.competitive_ga.capital_competition import Opportunity, compare

def test_partial_free_cash_only_releases_shortfall():
    incumbent=Opportunity(('HORIZONS','h'),'AAA',.05,.01,.01)
    challenger=Opportunity(('GA7','g'),'BBB',.14,.01,.01)
    result=compare(incumbent,[challenger],held_weight=.10,free_weight=.04,required_weight=.10)
    assert abs(result.released_weight-.06)<1e-10
    assert compare(incumbent,[challenger],held_weight=.10,free_weight=.10,required_weight=.10) is None
