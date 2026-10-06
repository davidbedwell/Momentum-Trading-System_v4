import numpy as np
from dataclasses import replace
from Core.conforming_ga.g2schema import validate_genome,ctxref
from Core.conforming_ga.g2evolution import seed_g2,mutate_g2,crossover_g2

def test_validator_rejects_dangling_context_reference():
    g=seed_g2(1)
    m=g.modules[0]
    bad=replace(g,modules=(replace(m,applicability=ctxref("gate",987654321)),))
    assert any(x.startswith("dangling_ctxref_") for x in validate_genome(bad))

def test_mutation_and_crossover_never_emit_dangling_references():
    rng=np.random.Generator(np.random.PCG64(20261006))
    pop=[seed_g2(i) for i in range(24)]
    for _ in range(1000):
        a=pop[int(rng.integers(0,len(pop)))];b=pop[int(rng.integers(0,len(pop)))]
        child=crossover_g2(a,b,rng)
        child=mutate_g2(child,rng)
        assert not validate_genome(child)
        pop[int(rng.integers(0,len(pop)))]=child
