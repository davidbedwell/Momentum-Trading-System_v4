"""Actual two-objective NSGA-II environmental selection and reproduction.

The engine never sees planted target labels, shapes or effects. Horizons are
compared only at equal horizon. All complete paths are retained for auditing.
"""
import random
from dataclasses import dataclass
from Core.layered_ga.stage2_multiobjective_v3 import rank_candidates

@dataclass
class Individual:
    genome: dict
    curve: object
    candidate_id: str

def environmental_selection(individuals, population_size):
    """NSGA-II selection using full curves, not scalar best-horizon LCB."""
    ranking,fronts=rank_candidates([(p.candidate_id,p.curve) for p in individuals])
    by_id={p.candidate_id:p for p in individuals}
    ordered=sorted(individuals,key=lambda p:(ranking.get(p.candidate_id,(10**9,0,0)),p.candidate_id))
    return ordered[:population_size],ranking

def evolve(space,evaluate,*,seed,population_size=24,generations=5):
    """Evaluate offspring, select by nondominated rank/crowding and reproduce.

    Genome operators preserve the discrete grammar and full search space.
    Returns a verifiable generation ledger with parent-child lineage.
    """
    from Core.layered_ga.stage2_compiler_v3 import random_genome
    rng=random.Random(seed);ledger=[];cache={};counter=0
    def make(genome):
        nonlocal counter
        key=tuple(sorted(genome.items()))
        if key not in cache:cache[key]=evaluate(genome)
        counter+=1
        return Individual(dict(genome),cache[key],f'c{counter:07d}')
    pool=[make(random_genome(space,rng)) for _ in range(population_size)]
    for gen in range(generations):
        selected,ranks=environmental_selection(pool,population_size)
        lineage=[];offspring=[]
        if gen<generations-1:
            for _ in range(population_size):
                a,b=rng.sample(selected,2)
                child={gene.gene_id:rng.choice((a.genome[gene.gene_id],b.genome[gene.gene_id])) for gene in space.genes}
                if rng.random()<.5:
                    gene=rng.choice(space.genes);child[gene.gene_id]=rng.choice(gene.values)
                born=make(child)
                offspring.append(born)
                lineage.append({'child':born.candidate_id,'parents':[a.candidate_id,b.candidate_id]})
        ledger.append({'generation':gen,'evaluated_count':len(pool),
                       'selected':[p.candidate_id for p in selected],
                       'selection_lineage':lineage,
                       'ranking':{p.candidate_id:list(ranks.get(p.candidate_id,(10**9,0,0))) for p in pool}})
        pool=selected+offspring
    return {'method':'NSGA_II_TWO_OBJECTIVE_V3','generations':ledger,
            'unique_evaluations':len(cache),'final_population':pool}
