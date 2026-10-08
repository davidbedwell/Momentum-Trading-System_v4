from types import SimpleNamespace
from Core.layered_ga.stage2_multiobjective_v3 import (
    Observation,dominates,nondominated_sort,crowding_distance,rank_candidates
)
def p(name,ev,lcb,mae,h=5):
    return Observation(name,h,ev,lcb,mae,-abs(mae)*2)
def test_mae_not_objective_or_arbitrary_cap():
    better=p("higher-return",.09,.04,-3.5)
    worse=p("lower-return",.04,.02,-.2)
    assert dominates(better,worse)
    assert not dominates(worse,better)
    assert nondominated_sort([worse,better])[0]==(better,)
def test_economic_tradeoff_preserved():
    a=p("a",.09,.01,-.8)
    b=p("b",.05,.04,-.1)
    assert set(nondominated_sort([a,b])[0])=={a,b}
def test_horizon_not_cross_compared():
    a=p("a",.09,.08,-1,5)
    b=p("b",.01,.001,-.1,25)
    assert not dominates(a,b)
    assert len(nondominated_sort([a,b])[0])==2
def test_crowding_diversity():
    a=p("a",.01,.01,-1)
    b=p("b",.02,.02,-1)
    c=p("c",.03,.03,-1)
    d=crowding_distance((a,b,c))
    assert d[("a",5)]==float("inf")
    assert d[("c",5)]==float("inf")
def test_curve_rank_preserves_both_sides_of_tradeoff():
    def curve(ev,lcb,mae):
        return SimpleNamespace(points=({"horizon":5,"ev_net":ev,"lcb95":lcb,
                                        "mae_mean":mae,"mae_tail5":mae*2},))
    ranks,fronts=rank_candidates([("a",curve(.09,.01,-4)),
                                  ("b",curve(.05,.04,-.1))])
    assert ranks["a"][0]==ranks["b"][0]==0
    assert len(fronts[0])==2
