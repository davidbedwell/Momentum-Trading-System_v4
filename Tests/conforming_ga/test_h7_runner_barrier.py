import json
from pathlib import Path
from Core.conforming_ga.g2schema import canonical,genome_hash,genome_from_canonical_g2
from Core.conforming_ga.g2evolution import seed_g2
from Core.conforming_ga.h7_runner import enforce_four_fold_barrier
from Core.conforming_ga.gates import freeze_finalists
import pytest

def test_g2_canonical_roundtrip_hash_identical():
 g=seed_g2(9182);z=genome_from_canonical_g2(canonical(g))
 assert canonical(z)==canonical(g) and genome_hash(z)==genome_hash(g)

def test_four_fold_freeze_barrier_requires_all_exact_hashes(tmp_path):
 ps=[];hs=[]
 for f in range(4):
  p=tmp_path/f"f{f}.json";h=freeze_finalists(p,f,{"status":"FROZEN_TRAIN_ONLY","finalists":[]});ps.append(p);hs.append(h)
 assert enforce_four_fold_barrier(ps,hs)
 ps[3].write_text("{}")
 with pytest.raises(Exception):enforce_four_fold_barrier(ps,hs)

def test_runner_source_orders_all_train_freeze_barrier_before_blind_load():
 s=Path("scripts/run_h7_null_g2_20261006.py").read_text()
 train=s.index("for fold in range(FOLDS):")
 barrier=s.index("enforce_four_fold_barrier(paths,hashes)")
 blind=s.index("FoldLoader(ROOT,MIRROR,fold,'blind')")
 assert train < barrier < blind
 # Exactly one blind loader occurrence and it is textually impossible before barrier.
 assert s.count("fold,'blind'")==1
 assert "population_size=POPULATION" in s and "POPULATION=250" in s
 assert "evolve_g2(" in s and "bootstrap_replicates\":2000" in s
 assert "parallel_folds" in s and "workers_per_fold" in s
 assert s.index("p.wait()") < barrier
