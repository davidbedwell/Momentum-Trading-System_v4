from discovery.competitive_ga.liquidity_policy import LiquidityGenes,targets

def test_three_buckets_and_sgov_not_cash():
    g=LiquidityGenes()
    r=targets(g,near_term_opportunity=0,uncertainty=0,active_target=.5)
    assert abs(sum(r.values())-1)<1e-10
    assert r['sgov']>0 and r['cash']>=g.base_cash
    assert targets(g,near_term_opportunity=.2,uncertainty=.5,active_target=.5)['cash']>r['cash']

def test_sgov_unavailable_stays_cash():
    r=targets(LiquidityGenes(),near_term_opportunity=0,uncertainty=0,active_target=.5,sgov_eligible=False)
    assert r['sgov']==0 and abs(r['cash']-.5)<1e-10
