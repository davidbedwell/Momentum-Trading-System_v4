import hashlib
from pathlib import Path
from Core.conforming_ga.ga import evolve
from Core.conforming_ga.evolution import canonical_genome

def ev(g):
    h=int(hashlib.sha256(canonical_genome(g).encode()).hexdigest()[:12],16)
    return {'cagr':(h%10000)/100000.0,'mdd':-((h//10000)%4000)/10000.0,
      'gross':.5,'safe_fraction':.5,'short_share':0.,'turnover':.1,'holdings_hhi':.2,'gfc_return':0.,'recovery_capture':0.}

def signature(r):
    return {k:[hashlib.sha256(canonical_genome(g).encode()).hexdigest() for g in v] for k,v in r['populations'].items()}

def test_pf25_checkpoint_resume_bit_identical(tmp_path):
    full=evolve(evaluator=ev,master_seed='RESUME',fold=0,generations=12,population_size=16,checkpoint_dir=tmp_path/'full')
    part=evolve(evaluator=ev,master_seed='RESUME',fold=0,generations=10,population_size=16,checkpoint_dir=tmp_path/'part')
    cp=tmp_path/'part'/'fold0_gen0010.json'
    assert cp.is_file()
    resumed=evolve(evaluator=ev,master_seed='RESUME',fold=0,generations=12,population_size=16,resume_path=cp)
    assert signature(full)==signature(resumed)
    assert full['history']==resumed['history']

def test_deterministic_repeat_independent_of_evaluation_order():
    a=evolve(evaluator=ev,master_seed='DET',fold=1,generations=3,population_size=12,workers=1)
    b=evolve(evaluator=ev,master_seed='DET',fold=1,generations=3,population_size=12,workers=4)
    assert signature(a)==signature(b)
