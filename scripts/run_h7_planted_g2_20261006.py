#!/usr/bin/env python3
from pathlib import Path
import json,time,hashlib,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from Core.conforming_ga.h7_g2 import run_planted_g2
OUT=ROOT/'Research/Conformance/MTS_H7_PLANTED_CALIBRATION_20261006.json'
CK=ROOT/'Research/Checkpoints/H7_G2_PLANTED_20261006'
MASTER='MTS-G2-H7-20261006'; MAX_GENERATIONS=500; CHECK_INTERVAL=1; POPULATION=64; WORKERS=6; SEEDS=(0,1,2,3)
t=time.time()
print(f'H7 planted calibration: seeds={SEEDS} max_generations={MAX_GENERATIONS} check_interval={CHECK_INTERVAL} population/island={POPULATION} workers={WORKERS}',flush=True)
r=run_planted_g2(master_seed=MASTER,seeds=SEEDS,generations=MAX_GENERATIONS,population_size=POPULATION,workers=WORKERS,checkpoint_root=CK,check_interval=CHECK_INTERVAL)
report={'format':'MTS_H7_G2_PLANTED_V3','date':'2026-10-06','schema':'MTS-GA-G2',
'mechanics':{'islands':9,'population_per_island':POPULATION,'maximum_generations_per_seed':MAX_GENERATIONS,'recovery_observation_interval':CHECK_INTERVAL,'disk_checkpoint_interval':10,'workers':WORKERS,'same_evolution':'Core.conforming_ga.ga_g2.evolve_g2','same_fitness':'Core.conforming_ga.g2fitness.make_g2_evaluator','seeds':list(SEEDS)},
'criterion':'same module signal references planted stock ret20 and applicability references planted market breadth_positive20, with positive CAGR; recover in >=3/4 seeds within 500-generation base budget',
'results':r['results'],'recovered':r['recovered'],'decision':r['decision'],'passed':bool(r['passed']),'elapsed_seconds':time.time()-t}
OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
(OUT.with_suffix(OUT.suffix+'.sha256')).write_text(hashlib.sha256(OUT.read_bytes()).hexdigest()+'  '+OUT.name+'\n')
print(json.dumps(report,indent=2),flush=True)
