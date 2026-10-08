"""GA4 combination evolution with surviving NSGA-II environmental selection."""
import random
from .ga4_combination_genetics import propose, combine, chromosome_key
from .stage2_nsga2_engine_v3 import Individual, environmental_selection


def evolve_combinations(spaces, evaluate, *, seed, population_size=24, generations=5):
    if population_size < 2 or generations < 1:
        raise ValueError("Invalid evolutionary budget")
    rng = random.Random(seed)
    cache = {}
    ledger = []
    counter = 0

    def make(chromosomes):
        nonlocal counter
        key = tuple(sorted(chromosome_key(x) for x in chromosomes))
        if key not in cache:
            cache[key] = evaluate(chromosomes)
        counter += 1
        return Individual({"chromosomes": tuple(chromosomes)}, cache[key], f"c{counter:07d}")

    pool = [make(propose(spaces, rng)) for _ in range(population_size)]
    for generation in range(generations):
        selected, ranking = environmental_selection(pool, population_size)
        ledger.append({"generation": generation, "evaluated": len(pool),
                       "selected": [p.candidate_id for p in selected],
                       "unique_evaluations": len(cache)})
        offspring = []
        if generation < generations - 1:
            for _ in range(population_size):
                left, right = rng.sample(selected, 2)
                child = combine(left.genome["chromosomes"], right.genome["chromosomes"], rng)
                offspring.append(make(child))
        pool = selected + offspring
    return {"generations": ledger, "unique_evaluations": len(cache),
            "final_population": pool, "certified": False}
