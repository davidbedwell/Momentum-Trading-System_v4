import random
from dataclasses import asdict
from pathlib import Path
import numpy as np
import pytest
from Core.g3.production import *

def data(seed=1,n=400,p=17,h=60):
    r=np.random.default_rng(seed);X=r.normal(size=(n,p));Y=r.normal(0,.006,size=(n,h));return {'A':(X,Y),'B':(X.copy(),Y.copy())}

def test_genome_has_no_identity_or_portfolio_genes():
    g=random_genome(1,17); s=str(asdict(g)).lower()
    assert all(k not in s for k in FORBIDDEN_GENES)

def test_broad_grammar_and_lifecycle_executes():
    g=random_genome(2,17);validate_genome(g,17);e=evaluate_genome(g,data(),10)
    assert e.n>=0
    if e.events: assert all(x.actions[0]=='enter' and x.actions[-1]=='exit' for x in e.events)

def test_cost_monotonicity_same_events():
    g=random_genome(3,17);d=data();a=evaluate_genome(g,d,0);b=evaluate_genome(g,d,20)
    assert a.n==b.n
    if a.n: assert a.mean>=b.mean

def test_pareto_direction():
    assert dominates((.02,.01,5),(.01,.02,7))
    assert not dominates((.01,.03,4),(.02,.02,7))

def test_promotion_requires_floor():
    g=random_genome(4,17);e=evaluate_genome(g,data(n=100),10);axes=bootstrap_axes(e,1,20)
    if e.n<50 or e.clusters<25: assert promotion(e,e,axes,1.0) is False

def test_checkpoint_identity(tmp_path):
    g=random_genome(5,17);s={'generation':7,'population':[g],'rng':random.Random(9).getstate()};p=tmp_path/'c.pkl';h=save_checkpoint(p,s);z=load_checkpoint(p)
    assert z==s and len(h)==64

def test_mutation_stays_in_grammar():
    g=random_genome(6,17)
    for i in range(200): g=mutate(g,i,17);validate_genome(g,17)

def test_crossover_stays_in_grammar():
    a=random_genome(7,17);b=random_genome(8,17)
    for i in range(50): validate_genome(crossover(a,b,i),17)
