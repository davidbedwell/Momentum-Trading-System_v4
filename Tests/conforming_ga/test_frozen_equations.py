import pytest
from Core.conforming_ga.engine import AllocationMode,Opportunity
from Core.conforming_ga.claims import frozen_claims
from Core.conforming_ga.ledger import *

def test_f2_strength_exact():
    w=frozen_claims({"A":Opportunity(.2),"B":Opportunity(.1)},AllocationMode.STRENGTH,tau=.5,q=.05,gamma=1,eta=.2)
    assert w==pytest.approx({"A":.075,"B":.025})

def test_f2_equal_is_not_normalized_upward():
    w=frozen_claims({"A":Opportunity(.2),"B":Opportunity(.1)},AllocationMode.EQUAL,tau=.2,q=.05,gamma=1,eta=.3)
    assert w==pytest.approx({"A":.06,"B":.06})
    assert 1-sum(w.values())==pytest.approx(.88)

def test_f2_only_scales_when_G_above_one():
    w=frozen_claims({"A":Opportunity(2),"B":Opportunity(2)},AllocationMode.STRENGTH,tau=1,q=0,gamma=1,eta=1)
    assert w==pytest.approx({"A":.5,"B":.5})

def test_e4_replace_uses_source_destination_inequality():
    states={"A":AssetState(.10,0,.01,0),"B":AssetState(.50,0,0,.01),"SAFE":AssetState(0)}
    cur,m=move_ledger({"A":.6},{"A":.2,"B":.4},states,kappa=1,lambda_u=0)
    assert cur==pytest.approx({"A":.2,"B":.4})
    assert any(x.source=="A" and x.destination=="B" and x.label=="REPLACE" for x in m)

def test_e4_partial_exit_to_safe_only_if_hurdle_clears():
    states={"A":AssetState(-.10,0,.01,0),"SAFE":AssetState(0)}
    cur,m=move_ledger({"A":.6},{"A":.3},states,kappa=1,lambda_u=0)
    assert cur["A"]==pytest.approx(.3)
    assert any(x.destination=="SAFE" for x in m)

def test_e4_uncertainty_can_block_move():
    states={"A":AssetState(0),"B":AssetState(.1,.2,0,0),"SAFE":AssetState(0)}
    cur,m=move_ledger({},{"B":.5},states,kappa=0,lambda_u=1)
    assert cur["B"]==0 and not m
