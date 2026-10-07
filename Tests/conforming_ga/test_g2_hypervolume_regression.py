import random
from Core.conforming_ga.ga_g2 import pareto,hypervolume

def row(i,c,m):
    return (i,{"cagr":c,"mdd":m})

def brute(scored):
    return [x for x in scored if not any(
        y is not x and y[1]["cagr"]>=x[1]["cagr"] and y[1]["mdd"]>=x[1]["mdd"] and
        (y[1]["cagr"]>x[1]["cagr"] or y[1]["mdd"]>x[1]["mdd"])
        for y in scored)]

def test_hypervolume_known_rectangle_union():
    pts=[row("a",.20,-.20),row("b",.10,-.10)]
    assert abs(hypervolume(pts)-1.10*0.90-0.10*0.80)<1e-12

def test_cumulative_archive_hypervolume_never_decreases():
    seq=[row("a",.10,-.20),row("b",.20,-.30),row("c",.15,-.10),row("d",.30,-.40)]
    vals=[hypervolume(seq[:i]) for i in range(1,len(seq)+1)]
    assert vals==sorted(vals),vals

def test_fast_pareto_matches_bruteforce_random_unique_metrics():
    rng=random.Random(20261006)
    for n in (1,2,10,100):
        scored=[row(i,rng.random(),-rng.random()) for i in range(n)]
        got={x[0] for x in pareto(scored)}
        exp={x[0] for x in brute(scored)}
        assert got==exp,(n,got,exp)

def test_plateau_gain_uses_excess_hv_not_reference_rectangle():
    # Same 0.001 absolute HV improvement: raw-HV gain is ~0.09%, while excess-HV
    # gain is 1%. H.4 therefore must not classify this as a <0.5% plateau.
    old_hv=1.100
    new_hv=1.101
    raw_gain=(new_hv-old_hv)/old_hv
    excess_gain=((new_hv-1.0)-(old_hv-1.0))/(old_hv-1.0)
    assert raw_gain < .005
    assert excess_gain > .005


def test_fast_pareto_retains_equal_metric_genomes_under_strict_dominance():
    scored=[
        row("equal_a",.20,-.20),
        row("equal_b",.20,-.20),
        row("dominated_same_cagr",.20,-.30),
        row("tradeoff",.10,-.10),
    ]
    got=[x[0] for x in pareto(scored)]
    exp=[x[0] for x in brute(scored)]
    assert got==exp
    assert "equal_a" in got and "equal_b" in got
    # Equal objective multiplicity has no geometric effect.
    assert hypervolume(scored)==hypervolume([scored[0],scored[3]])
