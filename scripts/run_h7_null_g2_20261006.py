#!/usr/bin/env python3
"""H.7 matched-null: same production controller; four Train80 freezes precede any Blind37 access."""
from pathlib import Path
import sys,json,time,hashlib,subprocess,os
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from Core.conforming_ga.realdata import FoldLoader
from Core.conforming_ga.h7_g2 import build_null_tape,_seed
from Core.conforming_ga.g2fitness import make_g2_evaluator
from Core.conforming_ga.ga_g2 import evolve_g2
from Core.conforming_ga.h7_runner import freeze_training_fold,enforce_four_fold_barrier,blind_replay
from Core.conforming_ga.compute_plan import plan
MIRROR=Path('/home/ubuntu/mts-clean-folds-20261006');OUT=ROOT/'Research/Conformance/MTS_H7_NULL_CALIBRATION_20261006.json';CKROOT=ROOT/'Research/State/H7_NULL_G2_20261006';FREEZE=ROOT/'Research/State/H7_NULL_FINALISTS_20261006'
MASTER='MTS_G2_H7_20261006';FOLDS=4;GENERATIONS=500;POPULATION=250
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def atomic_json(path,obj):
 path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n');tmp.replace(path)
def latest_checkpoint(d):
 xs=sorted(d.glob('g2_fold*_gen*.pkl')) if d.is_dir() else [];return xs[-1] if xs else None
def main():
 started=time.time();FREEZE.mkdir(parents=True,exist_ok=True);train_results=[];paths=[];hashes=[]
 # PHASE 1: all four Train80 evolutions + I.4 freezes. No blind loader exists above this barrier.
 cp=plan();parallel=cp["parallel_folds"];workers=cp["workers_per_fold"]
 if parallel>1:
  procs=[]
  for fold in range(FOLDS):
   log=ROOT/f"Research/Logs/MTS_H7_NULL_FOLD{fold}_20261006.log";log.parent.mkdir(parents=True,exist_ok=True)
   out=open(log,"ab",buffering=0);cmd=[str(ROOT/".venv/bin/python"),str(ROOT/"scripts/run_h7_null_fold_worker_20261006.py"),"--fold",str(fold),"--workers",str(workers)]
   procs.append((fold,subprocess.Popen(cmd,cwd=ROOT,stdout=out,stderr=subprocess.STDOUT),out))
  bad=[]
  for fold,p,out in procs:
   rc=p.wait();out.close()
   if rc:bad.append((fold,rc))
  if bad:raise RuntimeError("NULL_FOLD_WORKER_FAILURE:"+repr(bad))
  for fold in range(FOLDS):
   train_results.append(json.loads((FREEZE/f"fold{fold}_worker_result.json").read_text()))
 else:
  fold=0
  for fold in range(FOLDS):
   loader=FoldLoader(ROOT,MIRROR,fold,'train');raw=loader.load_prices();tickers=loader.tickers
   tape=build_null_tape(ROOT,raw,tickers,_seed(f'null|{MASTER}|train|{fold}'))
   ckdir=CKROOT/f'fold{fold}';resume=latest_checkpoint(ckdir);t=time.time()
   r=evolve_g2(evaluator=make_g2_evaluator(tape),master_seed=f'{MASTER}|NULL',fold=fold,generations=GENERATIONS,population_size=POPULATION,workers=workers,checkpoint_dir=ckdir,resume_path=resume)
   fp=FREEZE/f'fold{fold}_train_finalists.json';finalists,h=freeze_training_fold(fp,fold,tape,r['archives'])
   train_results.append({"fold":fold,"train_tickers":len(tickers),"completed_generations":r["completed_generations"],"final_budget":r["final_budget"],"elapsed_seconds":time.time()-t,"freeze_path":str(fp.relative_to(ROOT)),"freeze_sha256":h,"finalist_count":len(finalists),"events":r["events"]})
 paths=[ROOT/x["freeze_path"] for x in sorted(train_results,key=lambda z:z["fold"])]
 hashes=[x["freeze_sha256"] for x in sorted(train_results,key=lambda z:z["fold"])]
 atomic_json(OUT,{"format":"MTS_H7_G2_MATCHED_NULL_V2","status":"TRAINING_COMPLETE_AWAITING_BARRIER","passed":False,"compute_plan":cp,"train_results":train_results})
 # HARD BARRIER: hashes of all four frozen finalist sets must verify before first Blind37 access.
 enforce_four_fold_barrier(paths,hashes)
 # PHASE 2: independently construct null Blind37 tapes and replay frozen canonical genomes only.
 blind=[]
 for fold,(fp,h) in enumerate(zip(paths,hashes)):
  body=json.loads(fp.read_text());finalists=body["payload"]["finalists"]
  loader=FoldLoader(ROOT,MIRROR,fold,'blind');raw=loader.load_prices();tickers=loader.tickers
  tape=build_null_tape(ROOT,raw,tickers,_seed(f'null|{MASTER}|blind|{fold}'))
  blind.append({"fold":fold,"blind_tickers":len(tickers),"freeze_sha256":h,"frontier":blind_replay(tape,finalists)})
 report={"format":"MTS_H7_G2_MATCHED_NULL_V2","date":"2026-10-06","passed":True,"status":"PASS",
  "criterion":"matched-null calibration completion; null blind frontier is the measured chance bar, with no arbitrary bad-null threshold",
  "mechanics":{"islands":9,"population_per_island":250,"base_generations":500,"compute_plan":cp,"controller":"Core.conforming_ga.ga_g2.evolve_g2","bootstrap_replicates":2000,"freeze_barrier":"all four Train80 finalist files hash-verified before any Blind37 load","input_delta_only":"H.7 null stock path followed by production feature rebuild"},
  "train_results":train_results,"blind_results":blind,"elapsed_seconds":time.time()-started,
  "bindings":{x:sha(ROOT/x) for x in ["Core/conforming_ga/ga_g2.py","Core/conforming_ga/h7_g2.py","Core/conforming_ga/g2fitness.py","Core/conforming_ga/g2finalists.py","Core/conforming_ga/h7_runner.py","Core/conforming_ga/g2schema.py"]}}
 atomic_json(OUT,report);OUT.with_suffix(OUT.suffix+'.sha256').write_text(sha(OUT)+'\n');print(json.dumps({"status":"PASS","folds":4,"elapsed_seconds":report["elapsed_seconds"]},indent=2))
if __name__=='__main__':main()
