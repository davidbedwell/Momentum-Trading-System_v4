import numpy as np, pytest
from Core.conforming_ga.evolution import *
from Core.conforming_ga.execution import *
from Core.conforming_ga.gates import *

def test_execution_timing_t1_open_to_t2_open():
    o=np.array([[100.],[101.],[103.],[106.]])
    assert next_open_return(o,0)[0]==pytest.approx(103/101-1)

def test_publication_lag_never_uses_future_publication():
    obs=np.array([1,2,3]); vals=np.array([10.,20.,30.]); pub=np.array([2,4,6])
    assert published_value(obs,vals,pub,3)==10
    assert published_value(obs,vals,pub,5)==20

def test_no_entry_age_dependence_engine_api():
    import inspect,Core.conforming_ga.engine as e
    src=inspect.getsource(e.unified_moves)
    for forbidden in ("held_days","min_hold","max_hold","cooldown","entry_price","entry_date","position_age"):
        assert forbidden not in src

def test_stage_boundaries_exact():
    assert [stage_for_generation(x) for x in (0,99,100,249,250,449,450,499)]==["A","A","B","B","C","C","D","D"]

def test_stage_b_upweights_context_applicability_sector():
    a=operator_weights("A");b=operator_weights("B")
    assert all(b[k]>a[k] for k in ("context","applicability","sector"))

def test_stage_c_upweights_lifecycle_allocation_short():
    a=operator_weights("A");c=operator_weights("C")
    assert all(c[k]>a[k] for k in ("lifecycle","allocation","short"))

def test_ring_migration_and_top5_count():
    assert [ring_destination(i) for i in range(9)]==[1,2,3,4,5,6,7,8,0]
    assert migration_count(250)==13

def test_map_descriptors_exact_seven():
    m={k:i for i,k in enumerate(MAP_DESCRIPTOR_NAMES)}
    assert len(map_descriptor(m))==7 and len(MAP_DESCRIPTOR_NAMES)==7

def test_behavioral_novelty_distance_not_identity():
    assert behavioral_distance(np.array([0,1]),np.array([0,2]))>0

def test_plateau_first_injects_second_freezes():
    assert plateau_action(1)=="IMMIGRANTS_20_STRUCTURAL_UPWEIGHT"
    assert plateau_action(2)=="FREEZE_REALLOCATE"

def test_seed_deterministic_and_dimensioned():
    a=deterministic_seed("x",0,0,0)
    assert a==deterministic_seed("x",0,0,0)
    assert len({deterministic_seed("x",f,i,g) for f in range(2) for i in range(2) for g in range(2)})==8

def test_fold_freeze_barrier(tmp_path):
    ps=[];hs=[]
    for f in range(4):
        p=tmp_path/f"f{f}.json"; h=freeze_finalists(p,f,{"x":f});ps.append(str(p));hs.append(h)
    assert require_all_fold_freezes(ps,hs)
    (tmp_path/"f2.json").write_text("mutated")
    with pytest.raises(CertificationError):require_all_fold_freezes(ps,hs)

def test_certification_gate_fail_closed():
    with pytest.raises(CertificationError):certification_gate({"A":True,"B":False},("A","B"))
    assert certification_gate({"A":True,"B":True},("A","B"))

def test_metric_fixture_hand_computed():
    m=portfolio_metrics(np.array([100.,110.,99.]),np.array([0.,.2,.4]),np.array([1.,.5,.25]))
    assert m["total_return"]==pytest.approx(-.01)
    assert m["mdd"]==pytest.approx(-.1)
    assert m["turnover"]==pytest.approx(.2)
    assert m["safe_fraction"]==pytest.approx(1.75/3)
