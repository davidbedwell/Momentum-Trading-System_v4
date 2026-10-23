"""Small synthetic throughput benchmark; never starts the GA optimizer."""
import sys,time,json,concurrent.futures
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from test_ga5_evolution_pilot import EvolutionTests
from test_ga5_chromosome_contract import seed
from ga5_feature_families import compute
from guarded_evaluator import evaluate

def task(_):
 raw=EvolutionTests().bars()
 raw["dividends"]=0.;raw["stock_splits"]=0.
 frame=compute(raw,sector_map={"A":"TECH","B":"TECH"})
 days=sorted({str(d)[:10] for d in frame.date})
 membership={(d,t):True for d in days for t in ("A","B")}
 result=evaluate(frame,seed(),blocked={},membership=membership,
                 risk_veto={d:True for d in days},annual_cash_yield=.03)
 return result["final_nav"]
def main():
 results=[]
 for workers in (1,2,4,8):
  start=time.perf_counter()
  with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as pool:
   values=list(pool.map(task,range(16)))
  seconds=time.perf_counter()-start
  assert len(set(values))==1
  results.append({"workers":workers,"evaluations":16,"seconds":round(seconds,3),
                  "evaluations_per_second":round(16/seconds,3)})
 print(json.dumps(results,indent=2))
 Path("/opt/mts/ga5_redesign/guarded_throughput_benchmark.json").write_text(json.dumps(results,indent=2))
if __name__=="__main__":main()
