"""Engineering throughput only: deliberately unverified research policies."""
import sys,time,json,concurrent.futures
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import pandas as pd
from ga5_feature_families import compute
from test_ga5_chromosome_contract import seed
from ga5_chromosome_contract import mutate
from guarded_evaluator import evaluate,PreparedSessions
import random

def worker(job):
 count,worker_id=job
 raw=pd.read_parquet("/opt/mts/portfolio_evolution_dev80/dev80_raw_no_smci.parquet")
 features=compute(raw,sector_map={t:"PLACEHOLDER" for t in raw.ticker.unique()})
 prepared=PreparedSessions(features)
 membership={(d,t):True for d,rows,_,_ in prepared.sessions for t in rows}
 veto={d:True for d in prepared.dates}
 rng=random.Random(1234+worker_id)
 g=seed()
 start=time.perf_counter()
 results=[]
 for _ in range(count):
  g=mutate(g,rng)
  r=evaluate(prepared,g,blocked={},membership=membership,risk_veto=veto,annual_cash_yield=.03)
  results.append(r["final_nav"])
 return {"worker":worker_id,"evaluations":count,"seconds":time.perf_counter()-start,"result_count":len(results)}

def main():
 output=[]
 for workers in (1,2,4,8):
  start=time.perf_counter()
  with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as pool:
   result=list(pool.map(worker,[(2,i) for i in range(workers)]))
  elapsed=time.perf_counter()-start
  item={"workers":workers,"evaluations":workers*2,"wall_seconds":round(elapsed,3),"evals_per_second":round(workers*2/elapsed,3),"worker_details":result}
  output.append(item)
  print(json.dumps(item),flush=True)
 Path("/opt/mts/ga5_redesign/fullhistory_parallel_preflight.json").write_text(json.dumps(output,indent=2))
if __name__=="__main__":main()
