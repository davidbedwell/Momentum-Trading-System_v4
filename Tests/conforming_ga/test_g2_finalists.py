import numpy as np
from Core.conforming_ga.g2finalists import candidate_bootstrap,paired_difference_se,BOOTSTRAP_REPLICATES
from Core.conforming_ga.g2evolution import initial_population_g2

def test_fixed_2000_and_deterministic_candidate_bootstrap():
 g=initial_population_g2("f",0,0,1)[0];r=np.sin(np.arange(300)/13)*.01
 a,ea=candidate_bootstrap(r,0,g);b,eb=candidate_bootstrap(r,0,g)
 assert BOOTSTRAP_REPLICATES==2000 and len(a)==2000
 assert np.array_equal(a,b) and ea==eb
 assert ea["replicate_count"]==2000 and ea["selected_block_length"]>=1

def test_paired_common_resamples_capture_covariance():
 gs=initial_population_g2("pair",0,0,2);t=np.arange(500)
 common=np.sin(t/17)*.02
 se,ev=paired_difference_se(common,common,0,gs[0],gs[1])
 # Identical histories have exactly zero comparison uncertainty under common resamples.
 assert se < 1e-14
 assert ev["paired_selected_block_length"]>=1
 assert "paired_seed_derivation" in ev

def test_pair_seed_is_order_invariant():
 gs=initial_population_g2("order",0,0,2);r=np.cos(np.arange(300)/11)*.01
 x,ex=paired_difference_se(r,r*.9,1,gs[0],gs[1])
 y,ey=paired_difference_se(r*.9,r,1,gs[1],gs[0])
 assert x==y and ex["paired_seed"]==ey["paired_seed"]
