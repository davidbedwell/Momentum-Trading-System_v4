#!/usr/bin/env python3
"""Cheap destination-machine throughput preflight; never launches production GA."""
from pathlib import Path
import sys,time,json,os
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from Core.conforming_ga.compute_plan import plan
from Core.conforming_ga.realdata import FoldLoader
from Core.conforming_ga.h7_g2 import build_null_tape,_seed
from Core.conforming_ga.g2fitness import make_g2_evaluator
from Core.conforming_ga.g2evolution import initial_population_g2
def main():
 p=plan();loader=FoldLoader(ROOT,Path('/home/ubuntu/mts-clean-folds-20261006'),0,'train')
 raw=loader.load_prices();tape=build_null_tape(ROOT,raw,loader.tickers,_seed('compute-benchmark'))
 ev=make_g2_evaluator(tape);gs=initial_population_g2('compute-benchmark',0,0,12)
 t=time.time()
 for g in gs:ev(g)
 elapsed=time.time()-t;sec=elapsed/len(gs);evals=9*250*500*4
 est=evals*sec/max(1,p['usable_workers'])
 out={"compute_plan":p,"sample_genomes":len(gs),"elapsed_seconds":elapsed,"seconds_per_genome_single_process":sec,
      "estimated_four_fold_base_hours_if_parallel_scaling":est/3600,
      "note":"ETA is a conservative first-order benchmark; production launch still requires all conformance gates."}
 q=ROOT/'Research/Benchmarks/MTS_G2_DESTINATION_COMPUTE_BENCHMARK_20261006.json';q.parent.mkdir(parents=True,exist_ok=True);q.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
