from dataclasses import dataclass
from Core.layered_ga.stage2_nsga2_engine_v3 import evolve,environmental_selection,Individual
@dataclass
class Gene:
    gene_id:str
    values:tuple
@dataclass
class Space:
    genes:tuple
@dataclass
class Curve:
    points:tuple

def evaluate(g):
    x=g['x'];return Curve(tuple({'horizon':h,'ev_net':float(x),'lcb95':float(5-x),'mae_mean':-0.1,'mae_tail5':-0.2} for h in range(1,64)))

def test_actual_reproduction_and_full_horizon():
    space=Space((Gene('x',(0,1,2,3,4,5)),))
    run=evolve(space,evaluate,seed=9,population_size=8,generations=3)
    assert len(run['generations'])==3
    assert len(run['generations'][0]['selection_lineage'])==8
    assert len(run['final_population'])==8
    assert all(len(p.curve.points)==63 for p in run['final_population'])
