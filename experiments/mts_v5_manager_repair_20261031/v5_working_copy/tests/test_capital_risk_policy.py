from discovery.competitive_ga.capital_risk_policy import AllocationPolicy,position_risk,allowable_additional_shares

def test_policy_defaults():
    p=AllocationPolicy()
    assert (p.favorable_exposure_target,p.preferred_initial_min,p.preferred_initial_max)==(.70,.07,.10)
    assert p.max_position_capital_loss==.02

def test_profit_giveback_is_not_principal_loss():
    r=position_risk(shares=100,average_cost=100,current_price=130,protective_exit=115,portfolio_equity=100000,peak_price=140)
    assert r['capital_loss_fraction']==0
    assert abs(r['profit_giveback_fraction']-.025)<1e-10
    assert abs(r['mark_to_exit_fraction']-.015)<1e-10

def test_scale_uses_entire_cost_basis():
    # 100 shares bought at 100, $90 stop => $1K principal at risk;
    # adding at 120 risks $30 per added share, leaving $1K risk budget.
    n=allowable_additional_shares(existing_shares=100,average_cost=100,add_price=120,protective_exit=90,portfolio_equity=100000)
    assert abs(n-1000/30)<1e-10

def test_gap_stress_counts_as_capital_risk():
    r=position_risk(shares=200,average_cost=100,current_price=140,protective_exit=120,gap_exit=85,portfolio_equity=100000)
    assert abs(r['capital_loss_fraction']-.03)<1e-10
    assert not r['within_two_percent']
