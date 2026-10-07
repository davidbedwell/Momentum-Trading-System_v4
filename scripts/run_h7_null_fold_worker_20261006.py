#!/usr/bin/env python3
from pathlib import Path
import sys,argparse,json,time,os
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from Core.conforming_ga.realdata import FoldLoader
from Core.conforming_ga.h7_g2 import build_null_tape,_seed
from Core.conforming_ga.g2fitness import make_g2_evaluator
from Core.conforming_ga.ga_g2 import evolve_g2
from Core.conforming_ga.h7_runner import freeze_training_fold
MIRROR=Path('/home/ubuntu/mts-clean-folds-20261006');CKROOT=ROOT/'Research/State/H7_NULL_G2_20261006';FREEZE=ROOT/'Research/State/H7_NULL_FINALISTS_20261006';PROGRESS=ROOT/'Research/Conformance/MTS_H7_NULL_PROGRESS_20261006';MASTER='MTS_G2_H7_20261006'
def latest(d):
 xs=sorted(d.glob('g2_fold*_gen*.pkl')) if d.is_dir() else [];return xs[-1] if xs else None
def main():
 a=argparse.ArgumentParser();a.add_argument('--fold',type=int,required=True);a.add_argument('--workers',type=int,required=True);x=a.parse_args();t=time.time()
 loader=FoldLoader(ROOT,MIRROR,x.fold,'train');raw=loader.load_prices();tape=build_null_tape(ROOT,raw,loader.tickers,_seed(f'null|{MASTER}|train|{x.fold}'))
 ck=CKROOT/f'fold{x.fold}';resume=latest(ck);PROGRESS.mkdir(parents=True,exist_ok=True);pp=PROGRESS/f'fold{x.fold}.json'
 def progress(generation,archives,history):
  tmp=pp.with_suffix('.json.tmp');tmp.write_text(json.dumps({"fold":x.fold,"pid":os.getpid(),"status":"RUNNING","generation":generation,"resumed_from":str(resume.relative_to(ROOT)) if resume else None,"timestamp":time.time()},indent=2,sort_keys=True)+'\n');tmp.replace(pp);return False
 progress(int(resume.stem[-4:]) if resume else 0,None,None)
 r=evolve_g2(evaluator=make_g2_evaluator(tape),master_seed=f'{MASTER}|NULL',fold=x.fold,generations=500,population_size=250,workers=x.workers,checkpoint_dir=ck,resume_path=resume,generation_stop=progress)
 tmp=pp.with_suffix('.json.tmp');tmp.write_text(json.dumps({"fold":x.fold,"pid":os.getpid(),"status":"TRAINING_COMPLETE","generation":r["completed_generations"],"timestamp":time.time()},indent=2,sort_keys=True)+'\n');tmp.replace(pp)
 fp=FREEZE/f'fold{x.fold}_train_finalists.json';finalists,h=freeze_training_fold(fp,x.fold,tape,r['archives'])
 q=FREEZE/f'fold{x.fold}_worker_result.json';q.write_text(json.dumps({"fold":x.fold,"train_tickers":len(loader.tickers),"completed_generations":r["completed_generations"],"final_budget":r["final_budget"],"elapsed_seconds":time.time()-t,"freeze_path":str(fp.relative_to(ROOT)),"freeze_sha256":h,"finalist_count":len(finalists),"events":r["events"]},indent=2,sort_keys=True)+'\n')
if __name__=='__main__':main()
