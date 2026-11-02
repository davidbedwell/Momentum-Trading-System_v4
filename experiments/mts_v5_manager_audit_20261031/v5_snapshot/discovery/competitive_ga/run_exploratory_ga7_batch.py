import os,subprocess,time,json,concurrent.futures
from pathlib import Path
root=Path('/opt/mts/ga7-deploy/experiments/exploratory_ga7_500')
env=os.environ.copy();env['PYTHONPATH']='/opt/mts:/opt/mts/ga5_redesign:/opt/mts/ga7-deploy/ga7_unbounded:/opt/mts/ga6/claude_selective_20261023'
env['OPENBLAS_NUM_THREADS']='1';env['OMP_NUM_THREADS']='1'
started=None
force=False
def run(job):
 scenario,arm=job
 with (root/f'scenario_{scenario}_{arm}.log').open('w') as log:
  rc=subprocess.call(['/opt/mts/synthetic-market-lab/.venv/bin/python','-m','discovery.competitive_ga.exploratory_ga7_study','--scenario',str(scenario),'--arm',arm]+(['--force'] if force else []),env=env,stdout=log,stderr=subprocess.STDOUT)
 print(json.dumps({'scenario':scenario,'arm':arm,'exit':rc,'batch_elapsed':time.monotonic()-started}),flush=True)
 return {'scenario':scenario,'arm':arm,'exit':rc}
def main():
 global started,force
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--workers',type=int,default=4);p.add_argument('--force',action='store_true');a=p.parse_args()
 if not 1<=a.workers<=4:raise ValueError('workers must be 1..4')
 force=a.force;root.mkdir(parents=True,exist_ok=True)
 started=time.monotonic()
 with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:
  results=list(pool.map(run,[(s,a) for s in range(1,6) for a in ('evolved','frozen')]))
 (root/'batch_runtime.json').write_text(json.dumps({'wall_seconds':time.monotonic()-started,'jobs':results},indent=2))
 if any(job['exit']!=0 for job in results):raise SystemExit(1)

if __name__=='__main__': main()
