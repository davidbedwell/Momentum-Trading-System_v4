import numpy as np
from Core.conforming_ga.peers import peer_indices

def test_zero_variance_does_not_create_arbitrary_peers():
    r=np.zeros((80,5),dtype=float)
    peers=peer_indices(r,79,60,3)
    assert len(peers)==5
    assert all(len(x)==0 for x in peers)

def test_finite_correlations_only_are_selected():
    x=np.linspace(-1,1,80)
    r=np.column_stack([x,x*2,np.zeros(80)])
    peers=peer_indices(r,79,60,2)
    assert 1 in peers[0]
    assert 0 in peers[1]
    assert len(peers[2])==0

def test_fast_peer_tape_matches_reference():
    from Core.conforming_ga.peers import peer_indices_tape
    rng=np.random.default_rng(19);r=rng.normal(size=(140,12))
    fast=peer_indices_tape(r,60,3)
    for t in (60,61,79,100,139):
        ref=peer_indices(r,t,60,3)
        for a,b in zip(fast[t],ref): assert np.array_equal(a,b)

def test_earnings_features_reachable_by_ga_factory():
    from Core.conforming_ga.evolution import random_genome
    seen=set()
    for seed in range(100):
        g=random_genome(seed)
        seen.update(t.feature for m in g.modules for t in m.stock_terms)
    assert "earnings_surprise_pct__v1" in seen
    assert "days_since_earnings__v1" in seen
    assert "earnings_event_session__v1" in seen

def test_ga_workers_execute_islands_in_parallel():
    import os,time
    from Core.conforming_ga.ga import evolve
    def ev(g):
        time.sleep(.002)
        return {"cagr":0.01,"mdd":-0.01,"gross":.1,"safe_fraction":.9,"short_share":0.,"turnover":0.,"holdings_hhi":1.,"gfc_return":0.,"recovery_capture":0.}
    r=evolve(evaluator=ev,master_seed="parallel-proof",fold=0,generations=1,population_size=2,workers=4)
    pids={m["_worker_pid"] for archive in r["archives"].values() for _,m in archive}
    assert len(pids)>=2
    assert os.getpid() not in pids
