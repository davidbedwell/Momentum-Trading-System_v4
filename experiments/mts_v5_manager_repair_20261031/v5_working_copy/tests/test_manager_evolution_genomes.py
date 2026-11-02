"""Manager GA genome operators; no proxy fitness permitted."""
import random
from dataclasses import asdict
from discovery.competitive_ga.manager_evolution_v1 import BOUNDS,population,mutate,crossover,identity,offspring


def valid(g):
    d=asdict(g)
    assert all(BOUNDS[k][0]<=v<=BOUNDS[k][1] for k,v in d.items())
    assert g.max_total>=g.max_initial


def test_population_reproducible_and_bounded():
    a=population(300,seed=13)
    assert len(a)==300
    assert [identity(g) for g in a]==[identity(g) for g in population(300,seed=13)]
    for g in a:valid(g)


def test_mutation_and_crossover_respect_constraints():
    a,b=population(2,seed=2)
    rng=random.Random(9)
    for _ in range(100):
        a=mutate(a,rng)
        b=crossover(a,b,rng)
        valid(a);valid(b)


def test_offspring_uses_supplied_replay_fitness():
    parents=population(3,seed=7)
    scored=[(parents[0],(1.,-.1,1.,.02)),
            (parents[1],(.5,-.2,.5,.01)),
            (parents[2],(.7,-.15,.6,.015))]
    result=offspring(scored,n=40,seed=8)
    assert len(result)==40
    assert identity(result[0])==identity(parents[0])
    for g in result:valid(g)
