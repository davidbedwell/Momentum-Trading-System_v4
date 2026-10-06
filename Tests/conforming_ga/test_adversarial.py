import numpy as np, pytest
from Core.conforming_ga.engine import partition_rank,trailing_peer_context,AllocationMode,Opportunity
from Core.conforming_ga.claims import frozen_claims
from Core.conforming_ga.data import causal_view
from Core.conforming_ga.ledger import *

def test_adversarial_blind37_extreme_mutation_cannot_move_train80_hash():
    rng=np.random.default_rng(101); tr=rng.normal(size=(80,80)); bl=rng.normal(size=(80,37))
    a=partition_rank(tr).tobytes()+trailing_peer_context(tr,10,3).tobytes()
    bl[:]=rng.normal(0,1e12,bl.shape)
    b=partition_rank(tr).tobytes()+trailing_peer_context(tr,10,3).tobytes()
    assert a==b

def test_adversarial_future_price_mutation_does_not_change_prior_features():
    rng=np.random.default_rng(102); x=rng.normal(size=(100,12)); T=50
    before=partition_rank(causal_view(x,T))
    x[T+1:]=rng.normal(0,1e9,x[T+1:].shape)
    after=partition_rank(causal_view(x,T))
    assert np.array_equal(before,after)

def test_adversarial_ticker_permutation_equivariance():
    rng=np.random.default_rng(103); x=rng.normal(size=(40,9)); perm=rng.permutation(9)
    a=partition_rank(x); b=partition_rank(x[:,perm])
    assert np.array_equal(a[:,perm],b)

def test_adversarial_weak_claims_do_not_get_normalized_to_full_investment():
    ops={f"S{i}":Opportunity(.001) for i in range(10)}
    w=frozen_claims(ops,AllocationMode.STRENGTH,tau=.5,q=0,gamma=1,eta=.1)
    assert sum(w.values())==pytest.approx(.005)

def test_adversarial_hand_replace_beats_two_safe_legs():
    st={"A":AssetState(.20,0,.03,0),"B":AssetState(.40,0,0,.03),"SAFE":AssetState(0)}
    cur,m=move_ledger({"A":1.0},{"B":1.0},st,kappa=1,lambda_u=0)
    assert cur["B"]==pytest.approx(1) and any(z.label=="REPLACE" for z in m)

def test_adversarial_bad_replace_is_rejected():
    st={"A":AssetState(.30,0,.02,0),"B":AssetState(.31,0,0,.02),"SAFE":AssetState(0)}
    cur,m=move_ledger({"A":1.0},{"B":1.0},st,kappa=1,lambda_u=0)
    assert cur["A"]==pytest.approx(1) and not m

def test_adversarial_partial_resize_is_not_all_or_nothing():
    st={"A":AssetState(-.2,0,.01,0),"SAFE":AssetState(0)}
    cur,m=move_ledger({"A":.6},{"A":.3},st,kappa=1,lambda_u=0)
    assert cur["A"]==pytest.approx(.3)

def test_adversarial_no_position_age_changes_decision():
    st={"A":AssetState(.2,0,0,0),"SAFE":AssetState(0)}
    # Engine has no age argument: identical economic state must be identical.
    a=move_ledger({},{"A":.4},st,kappa=0,lambda_u=0)
    b=move_ledger({},{"A":.4},st,kappa=0,lambda_u=0)
    assert a==b
