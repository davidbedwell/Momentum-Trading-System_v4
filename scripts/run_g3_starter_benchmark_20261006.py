import argparse,time,random,json,hashlib
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from Core.g3.starter import *
def job(args):
    seed,n=args; x,y,_=planted_dataset(seed=seed,n=n); rng=random.Random(seed)
    vals=[]
    for _ in range(16):
        g=random_specialist(rng,x.shape[1]); vals.append(quality(evaluate_one(g,x,y,10)))
    return vals
if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--workers",type=int,default=8);ap.add_argument("--jobs",type=int,default=32);ap.add_argument("--rows",type=int,default=2500);a=ap.parse_args()
    t=time.perf_counter()
    with ProcessPoolExecutor(max_workers=a.workers) as ex: z=list(ex.map(job,[(1000+i,a.rows) for i in range(a.jobs)]))
    sec=time.perf_counter()-t; evals=a.jobs*16
    out={"format":"MTS_G3_STARTER_BENCHMARK_V1","workers":a.workers,"jobs":a.jobs,"rows":a.rows,"specialist_evaluations":evals,"seconds":sec,"eval_per_sec":evals/sec}
    p=Path("Research/G3/MTS_G3_STARTER_BENCHMARK_20261006.json");p.write_text(json.dumps(out,indent=2)+"\n");print(json.dumps(out,indent=2))
