import numpy as np
from Core.g3.search_v3 import structural_screen
from Core.g3.starter import planted_dataset,evaluate_one,quality,aggregate_quality_summaries

def test_structural_screen_recovers_strong_planted_conjunction():
    data={}
    for i in range(4):
        x,y,_=planted_dataset(seed=900+i,n=1800,p=6,h=10,effect=.01)
        data[str(i)]=(x,y)
    seeds=structural_screen(data,24)
    best=-1
    for g in seeds:
        qs=[quality(evaluate_one(g,*data[t],10)) for t in data]
        best=max(best,aggregate_quality_summaries(qs)['mean'])
    assert best > .015

def test_structural_screen_is_deterministic():
    x,y,_=planted_dataset(seed=33,n=1000,p=4,h=10,effect=.01)
    d={'A':(x,y)}
    assert structural_screen(d,12)==structural_screen(d,12)
