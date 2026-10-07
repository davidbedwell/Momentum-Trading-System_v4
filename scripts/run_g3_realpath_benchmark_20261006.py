import json,time,random,argparse
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from Core.g3.realdata import acquire,derive,evidence_arrays,ROOT
from Core.g3.starter import random_specialist,evaluate_one,quality,assert_independent_path
TICKERS=["AAPL","MSFT","XOM","JPM","JNJ","CAT","WMT","NVDA"]
def one(args):
 t,seed,n=args;X,Y,_=evidence_arrays(t);X=X[-n:];Y=Y[-n:];rng=random.Random(seed)
 return [quality(evaluate_one(random_specialist(rng,X.shape[1]),X,Y,10)) for _ in range(32)]
if __name__=="__main__":
 ap=argparse.ArgumentParser();ap.add_argument("--workers",type=int,default=32);ap.add_argument("--jobs",type=int,default=64);ap.add_argument("--rows",type=int,default=2500);a=ap.parse_args()
 assert_independent_path(ROOT)
 t=time.perf_counter();m=acquire(TICKERS,"2006-01-01","2026-09-16");download=time.perf_counter()-t
 t=time.perf_counter();derive(TICKERS);deriv=time.perf_counter()-t
 tasks=[(TICKERS[i%len(TICKERS)],1000+i,a.rows) for i in range(a.jobs)]
 t=time.perf_counter()
 with ProcessPoolExecutor(max_workers=a.workers) as ex:z=list(ex.map(one,tasks))
 evsec=a.jobs*32/(time.perf_counter()-t)
 out={"format":"MTS_G3_REALPATH_BENCHMARK_V1","tickers":TICKERS,"period":["2006-01-01","2026-09-16"],"workers":a.workers,"jobs":a.jobs,"rows_per_job":a.rows,"evaluations":a.jobs*32,"download_seconds":download,"derive_seconds":deriv,"eval_per_sec":evsec,"lineage_root":str(ROOT)}
 p=Path("Research/G3/MTS_G3_REALPATH_BENCHMARK_20261006.json");p.write_text(json.dumps(out,indent=2)+"\n");print(json.dumps(out,indent=2))
