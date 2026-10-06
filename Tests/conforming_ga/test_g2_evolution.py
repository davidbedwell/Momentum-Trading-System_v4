import numpy as np
from Core.conforming_ga.g2evolution import *
from Core.conforming_ga.g2schema import *

def test_g2_initial_population_family_coverage_and_complexity():
    p=initial_population_g2("G2",0,0,250)
    n=len(FAMILIES);minimum=250//(2*n)
    for f in FAMILIES:
        assert sum(any(m.family_tag==f for m in g.modules) for g in p)>=minimum
    assert all(8<=active_concept_count(g)<=12 for g in p)
    assert all(validate_genome(g)==[] for g in p)

def test_every_g2_mutation_operator_is_reachable_and_valid():
    g=seed_g2(41,"momentum")
    changed=set()
    for j,name in enumerate(G2_MUTATION_OPS):
        rng=np.random.Generator(np.random.PCG64(1000+j))
        for _ in range(12):
            h=mutate_g2(g,rng,force=name)
            assert validate_genome(h)==[]
            if canonical(h)!=canonical(g):changed.add(name);break
    # Delete cannot alter a one-module seed; simplification can also be a no-op.
    assert set(G2_MUTATION_OPS)-{"module_delete","simplify"} <= changed

def test_g2_module_growth_and_shrink_are_reachable():
    rng=np.random.default_rng(7);g=seed_g2(7,"trend")
    h=mutate_g2(g,rng,force="module_add");assert len(h.modules)==2
    q=mutate_g2(h,rng,force="module_delete");assert len(q.modules)==1
    assert validate_genome(q)==[]

def test_g2_homologous_crossover_and_species_distance():
    a=seed_g2(1,"momentum");b=seed_g2(2,"reversal")
    c=crossover_g2(a,b,np.random.default_rng(3))
    assert validate_genome(c)==[]
    assert compatibility_distance(a,a)==0
    assert compatibility_distance(a,b)>0
    groups=assign_species([a,a,b],threshold=.01)
    assert sorted(map(len,groups))==[1,2]
