import sys,random
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'discovery'/'competitive_ga'))
from evolution import *

def test_population_reproducible_and_unique():
 a=initial_population(400,42);b=initial_population(400,42)
 assert [x.identity for x in a]==[x.identity for x in b]
 assert len({x.identity for x in a})==400

def test_mutation_crossover_valid():
 a,b=initial_population(2)
 assert mutate(a,random.Random(1)).identity!=a.identity
 assert len(crossover(a,b,random.Random(2)).weights)==len(FEATURES)

def test_pareto_non_dominated():
 g=initial_population(3)
 f=pareto_front([(g[0],(10,-.1,1)),(g[1],(9,-.2,.9)),(g[2],(11,-.3,1))])
 assert {x.identity for x,_ in f}=={g[0].identity,g[2].identity}

def test_requires_actual_fitness_and_breeds():
 try:next_generation([])
 except ValueError:pass
 else:raise AssertionError('must reject missing fitness')
 p=initial_population(4)
 out=next_generation([(g,(i,-i,.1)) for i,g in enumerate(p)],n=40)
 assert len(out)==40 and len({g.identity for g in out})==40
