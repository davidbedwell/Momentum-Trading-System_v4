"""Fixed real-data 500-candidate benchmark; never evolves or opens holdout."""
import os
for name in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[name]='1'
import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
import hashlib
import json
import multiprocessing as mp
from pathlib import Path
import random
import resource
import time
from threadpoolctl import threadpool_limits
from . import long_run as lr
from .engine import FAMILIES, Manager, replay
from .run import seed_genes
from .resources import Monitor

def main():
    parser=argparse.ArgumentParser(__doc__)
    parser.add_argument('--output',required=True)
    parser.add_argument('--end',default='2023-01-01')
    parser.add_argument('--workers',type=int,nargs='+',default=[1,4,8])
    args=parser.parse_args()
    out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    threadpool_limits(1);lr.worker_init()
    rng=random.Random(80079)
    tasks=[]
    for i in range(500):
        genes=list(seed_genes())
        genes[i%3]=replace(genes[i%3],family=FAMILIES[i%len(FAMILIES)],niche=i%4-1,threshold=rng.uniform(-.1,.7))
        tasks.append((genes,Manager(slots=rng.choice([5,7,10]),reserve=rng.choice([.1,.2,.35])),args.end))
    # Exact baseline parity includes metrics, audit and every marginal ablation.
    for genes,manager,end in tasks[:3]:
        result=lr.evaluate((genes,manager,end))
        baseline_full=replay(lr.PANEL,genes,manager,'2022-01-01',end,True)
        assert result['metrics']==baseline_full['metrics']
        assert result['audit']==baseline_full['audit']
        for k,entry in enumerate(result['marginal']):
            baseline=replay(lr.PANEL,genes[:k]+genes[k+1:],manager,'2022-01-01',end)['metrics']
            assert entry['incremental_nav']==result['metrics']['final_nav']-baseline['final_nav']
            assert entry['delta_cagr']==result['metrics']['cagr']-baseline['cagr']
            assert entry['delta_mdd']==result['metrics']['max_drawdown']-baseline['max_drawdown']
    lr.cached_replay.cache_clear()
    lr.cached_signal.cache_clear()
    reference=None
    for workers in args.workers:
        before=resource.getrusage(resource.RUSAGE_CHILDREN)
        monitor=Monitor();monitor.start();start=time.monotonic()
        with ProcessPoolExecutor(workers,initializer=lr.worker_init,mp_context=mp.get_context('fork')) as pool:
            rows=[]
            for row in pool.map(lr.evaluate,tasks,chunksize=4):
                rows.append(row)
                if len(rows)%100==0:
                    print(json.dumps(dict(workers=workers,completed=len(rows),seconds=time.monotonic()-start,resources=monitor.snapshot())),flush=True)
                if monitor.exceeded:
                    raise RuntimeError('RAM gate exceeded')
        seconds=time.monotonic()-start;monitor.closed=True
        digest=hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest()
        if reference is None:reference=digest
        assert digest==reference,'Worker-count semantic mismatch'
        after=resource.getrusage(resource.RUSAGE_CHILDREN)
        cpu_seconds=after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime
        report=dict(source_sha256=hashlib.sha256(lr.RAW.read_bytes()).hexdigest(),code_sha256=hashlib.sha256(Path(lr.__file__).read_bytes()+Path(lr.__file__).with_name('engine.py').read_bytes()+Path(lr.__file__).with_name('resources.py').read_bytes()).hexdigest(),train_end=args.end,aggregate_worker_cpu_percent=cpu_seconds/seconds*100,workers=workers,candidates=500,replays=2000,seconds=seconds,candidates_per_second=500/seconds,replays_per_second=2000/seconds,eta_1000_generations_seconds=seconds*1000,**monitor.snapshot(),sha256=digest,holdout_accessed=False)
        (out/f'workers_{workers}.json').write_text(json.dumps(report,indent=2))
        print(json.dumps(report),flush=True)
if __name__=='__main__':main()
