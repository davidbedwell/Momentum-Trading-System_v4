#!/usr/bin/env python3
"""Fail-closed sequential 13-window controller. No job until server authorization."""
import argparse,json,pathlib,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.thirteen_window_evolution_engine_20261011 import WINDOWS
from scripts.thirteen_window_launch_guard_20261011 import require_launch_authorization

def plan(base, generations=200, workers=28, batch=120, seed_size=1200, seed=20261011):
    return [{'window':[lo,hi],'output':str(pathlib.Path(base)/f'window_{lo:02d}_{hi:02d}'),
             'seed':seed+i,'generations':generations,'workers':workers,'batch':batch,'seed_size':seed_size}
            for i,(lo,hi) in enumerate(WINDOWS)]

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--output',type=pathlib.Path,default=ROOT/'Research/Runs/thirteen-window-serial-20261011')
    p.add_argument('--generations',type=int,default=200);p.add_argument('--workers',type=int,default=28)
    p.add_argument('--batch',type=int,default=120);p.add_argument('--seed-size',type=int,default=1200)
    p.add_argument('--seed',type=int,default=20261011);p.add_argument('--authorization-file',type=pathlib.Path)
    p.add_argument('--plan',action='store_true');a=p.parse_args()
    if not (a.generations>=1 and 1<=a.workers<=64 and a.batch>=20 and a.seed_size>=a.batch):raise ValueError('invalid settings')
    jobs=plan(a.output,a.generations,a.workers,a.batch,a.seed_size,a.seed)
    if a.plan:
        print(json.dumps({'status':'PLAN_ONLY_NO_COMPUTE','jobs':jobs},indent=2));return
    require_launch_authorization(authorization_path=a.authorization_file)
    for job in jobs:
        cmd=[sys.executable,str(ROOT/'scripts/run_thirteen_window_normal_20261011.py'),
             '--window',str(job['window'][0]),str(job['window'][1]),
             '--output',job['output'],'--generations',str(job['generations']),
             '--workers',str(job['workers']),'--batch',str(job['batch']),
             '--seed-size',str(job['seed_size']),'--seed',str(job['seed']),
             '--authorization-file',str(a.authorization_file)]
        print('START_WINDOW',job['window'],flush=True)
        subprocess.run(cmd,cwd=ROOT,check=True)
        print('COMPLETE_WINDOW',job['window'],flush=True)
if __name__=='__main__':main()
