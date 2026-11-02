from discovery.competitive_ga.capital_competition import Opportunity, compare

def test_only_superior_eligible_challenger_can_displace():
    old=Opportunity(('HORIZONS','h1'),'AAA',.08,.02,.01)
    weak=Opportunity(('GA7','g1'),'BBB',.07,.02,.01)
    strong=Opportunity(('GA6','g2'),'CCC',.15,.02,.02)
    assert compare(old,[weak],held_weight=.1,free_weight=0) is None
    assert compare(old,[strong],held_weight=.1,free_weight=.2) is None
    result=compare(old,[strong],held_weight=.1,free_weight=0,margin=.01)
    assert result.challenger==('GA6','g2')
    assert result.incumbent==('HORIZONS','h1')
    assert result.net_advantage>.01

def test_ineligible_challenger_never_displaces():
    old=Opportunity(('GA7','old'),'AAA',.03,.01,0)
    other=Opportunity(('GA6','new'),'BBB',.5,.01,.01,False)
    assert compare(old,[other],held_weight=.1,free_weight=0) is None
