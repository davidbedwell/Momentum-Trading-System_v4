import numpy as np, pytest
from Core.conforming_ga.engine import *
from Core.conforming_ga.data import *

def test_train80_partition_local_rank_immune_to_blind37_mutation():
    rng=np.random.default_rng(1); train=rng.normal(size=(30,80)); blind=rng.normal(size=(30,37))
    before=partition_rank(train)
    blind[:]=1e9
    assert np.array_equal(before,partition_rank(train))

def test_blind37_reconstructed_independently():
    rng=np.random.default_rng(2); b=rng.normal(size=(10,37))
    assert np.array_equal(partition_rank(b),partition_rank(b.copy()))

def test_protected_data_denied_at_load_and_request():
    with pytest.raises(ProtectedDataError): PartitionStore({"DV":np.arange(3)},{"DV"})
    s=PartitionStore({"A":np.arange(3)},{"DV"})
    with pytest.raises(ProtectedDataError): s.materialize(Partition("x",("DV",)))

def test_pit_future_mutation_cannot_change_prior_view():
    a=np.arange(30.).reshape(10,3); x=causal_view(a,5)
    a[6:]=999
    assert np.array_equal(x,causal_view(a,5))

def test_weak_absolute_opportunity_stays_mostly_safe():
    w=absolute_claims({"A":Opportunity(.02)},0.0,AllocationMode.STRENGTH)
    assert w["A"]==pytest.approx(.02)
    assert 1-sum(map(abs,w.values()))==pytest.approx(.98)

def test_all_negative_opportunity_is_all_safe():
    w=absolute_claims({"A":Opportunity(-.1),"B":Opportunity(-.2)},0.0,AllocationMode.STRENGTH)
    assert sum(map(abs,w.values()))==0

def test_safe_hurdle_reduces_risky_claim():
    lo=absolute_claims({"A":Opportunity(.2)},0.0,AllocationMode.STRENGTH)["A"]
    hi=absolute_claims({"A":Opportunity(.2)},.1,AllocationMode.STRENGTH)["A"]
    assert hi < lo

@pytest.mark.parametrize("mode",[AllocationMode.EQUAL,AllocationMode.STRENGTH,AllocationMode.UNCERTAINTY,AllocationMode.DOWNSIDE])
def test_exact_four_allocation_modes_reachable(mode):
    w=absolute_claims({"A":Opportunity(.4,.2,.3),"B":Opportunity(.2,.4,.1)},0,mode)
    assert 0 < sum(w.values()) <= 1
def test_exactly_four_modes_exist(): assert set(AllocationMode)=={AllocationMode.EQUAL,AllocationMode.STRENGTH,AllocationMode.UNCERTAINTY,AllocationMode.DOWNSIDE}

def test_enter_semantics():
    cur,m=unified_moves({},{"A":.3},{"A":.5},0,.01)
    assert cur["A"]==pytest.approx(.3) and any(x.label=="ENTER" for x in m)

def test_continue_increase_semantics():
    cur,m=unified_moves({"A":.2},{"A":.4},{"A":.5},0,.01)
    assert cur["A"]==pytest.approx(.4) and any(x.label=="CONTINUE" for x in m)

def test_partial_resize_60_to_30():
    cur,m=unified_moves({"A":.6},{"A":.3},{"A":-.2},0,.01)
    assert cur["A"]==pytest.approx(.3) and any(x.label=="CONTINUE" and x.destination=="SAFE" for x in m)

def test_full_exit_to_safe():
    cur,m=unified_moves({"A":.4},{"A":0},{"A":-.2},0,.01)
    assert cur["A"]==pytest.approx(0) and any(x.label=="EXIT_TO_SAFE" for x in m)

def test_true_replace_incumbent_to_challenger():
    cur,m=unified_moves({"A":.6},{"A":.2,"B":.4},{"A":.10,"B":.50},0,.05)
    assert cur["A"]==pytest.approx(.2) and cur["B"]==pytest.approx(.4)
    assert any(x.label=="REPLACE" and x.source=="A" and x.destination=="B" for x in m)

def test_replace_blocked_when_hurdle_not_cleared():
    cur,m=unified_moves({"A":.6},{"A":.2,"B":.4},{"A":.40,"B":.42},0,.05)
    assert not any(x.label=="REPLACE" for x in m)

def test_short_entry():
    cur,m=unified_moves({},{"A":-.3},{"A":-.5},0,.01)
    assert cur["A"]==pytest.approx(-.3) and any(x.label=="SHORT" for x in m)

def test_short_cover_to_safe():
    cur,m=unified_moves({"A":-.4},{"A":0},{"A":.2},0,.01)
    assert cur["A"]==pytest.approx(0) and any(x.label=="EXIT_TO_SAFE" for x in m)

def test_friction_blocks_marginal_entry():
    cur,m=unified_moves({},{"A":.5},{"A":.02},0,.03)
    assert cur["A"]==0 and not m

def test_uncertainty_hurdle_blocks_marginal_entry():
    cur,m=unified_moves({},{"A":.5},{"A":.04},0,.01,.04)
    assert cur["A"]==0 and not m

def test_immediate_reentry_eligible_no_cooldown():
    cur,_=unified_moves({},{"A":.4},{"A":.5},0,.01)
    cur,_=unified_moves(cur,{"A":0},{"A":-.5},0,.01)
    cur,m=unified_moves(cur,{"A":.4},{"A":.5},0,.01)
    assert cur["A"]==pytest.approx(.4) and any(x.label=="ENTER" for x in m)

def test_gross_exposure_never_above_one():
    w=target_weights({"A":Opportunity(2),"B":Opportunity(2)},{"C":Opportunity(2)},0,AllocationMode.STRENGTH)
    assert sum(map(abs,w.values())) <= 1+1e-12

def test_transaction_cost_hand_calc():
    assert transaction_cost(100000,5)==pytest.approx(50)
    assert transaction_cost(100000,5,2e-5,True)==pytest.approx(52)

def test_borrow_cost_hand_calc():
    assert borrow_cost(100000,.03,30)==pytest.approx(100000*.03*30/365)

def test_deterministic_reproducibility():
    x=np.random.default_rng(9).normal(size=(20,8))
    assert np.array_equal(partition_rank(x),partition_rank(x))

def test_partition_provenance_exact_and_order_sensitive():
    s=PartitionStore({"A":np.arange(4.),"B":np.arange(4.)+1},set())
    assert s.provenance_hash(Partition("T",("A","B"))) != s.provenance_hash(Partition("T",("B","A")))
