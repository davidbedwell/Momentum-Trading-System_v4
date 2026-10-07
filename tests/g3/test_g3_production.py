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

def test_plateau_only_at_40_generation_boundaries():
    from Core.g3.production import plateau_update
    assert plateau_update(39,1,1,0,0)==(0,False)
    assert plateau_update(40,1,1.004,0,0)==(1,False)
    assert plateau_update(80,1,1.004,0,1)==(2,True)
    assert plateau_update(80,1,1.006,0,1)==(0,False)
    assert plateau_update(80,1,1.0,1,1)==(0,False)

def test_perturbations_are_oat_and_bidirectional():
    from Core.g3.production import random_genome,perturb_genomes
    g=random_genome(7,4); q=perturb_genomes(g)
    assert len(q)==len(g.modules)*12+2

def test_qd_has_256_frozen_cells_and_is_deterministic():
    from Core.g3.production import qd_fit,qd_cell
    import numpy as np
    A=np.arange(12*300,dtype=float).reshape(300,12)%37
    a=qd_fit(A);b=qd_fit(A)
    assert a['centroids'].shape==(256,12)
    assert np.allclose(a['centroids'],b['centroids'])
    assert qd_cell(A[0],a)==qd_cell(A[0],b)

def test_behavioral_duplicate_merge_keeps_lower_uncertainty():
    from Core.g3.production import qd_fit,qd_duplicate_merge
    import numpy as np
    model=qd_fit(np.zeros((300,12)))
    old={'descriptor':[0.]*12,'fired_signature':[['A',1],['A',2]],'uncertainty_width':.2}
    new={'descriptor':[0.]*12,'fired_signature':[['A',1],['A',2]],'uncertainty_width':.1}
    cells={0:[('old',old)]};merged,other=qd_duplicate_merge(cells,'new',new,model)
    assert merged and other=='old' and cells[0][0][0]=='new'

def test_costs_are_monotone_for_identical_paths():
    from Core.g3.production import random_genome,evaluate_genome
    import numpy as np
    g=random_genome(91,4);X=np.ones((100,4));Y=np.full((100,60),.001);data={'T':(X,Y)}
    a=evaluate_genome(g,data,10);b=evaluate_genome(g,data,15);c=evaluate_genome(g,data,20)
    if a.events:
        assert a.mean>=b.mean>=c.mean
