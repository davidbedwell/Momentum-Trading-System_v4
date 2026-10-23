"""GA5 guarded research runner. Does not launch a GA unless explicitly invoked.
Uses one feature file, one niche per worker, and a shared SQLite evaluation cache.
No scientific promotion or production use.
"""
import argparse,concurrent.futures,json,os,sys,time,base64,pickle
from dataclasses import replace,asdict
from pathlib import Path
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from niche_seeds import initial
from ga5_chromosome_contract import mutate,crossover,Genome
from optimizer_v3 import NICHES,fitness
from canonical_engine import ResultCache,digest_file
from guarded_evaluator import evaluate as guarded_evaluate,PreparedSessions
import hashlib
# Fingerprint the complete research execution path, not just inputs.
ENGINE_FILES=("ga5_redesign/runner_v4.py","ga5_redesign/guarded_evaluator.py",
 "ga5_redesign/niche_seeds.py","ga5_redesign/ga4_registry.py","ga5_redesign/shadow_signals.py","ga5_redesign/fast_decision.py","ga5_redesign/settlement_ledger.py",
 "ga5_redesign/canonical_engine.py","ga5_chromosome_contract.py",
 "ga5_chromosome_decisions.py","ga5_feature_adapter.py",
 "ga5_earnings_entry_embargo.py","ga5_corporate_action_ledger.py",
 "mts_next_open_ledger_v1.py")
def engine_fingerprint():
 root=Path(__file__).resolve().parent.parent
 h=hashlib.sha256()
 for name in ENGINE_FILES:
  h.update(name.encode());h.update(digest_file(root/name).encode())
 return h.hexdigest()

def niche_worker(job):
 niche,feature_path,db_path,sha,generations,population,random_seed,output,policy_path,policy_sha=job
 code_sha=engine_fingerprint()
 import random
 rng=random.Random(random_seed)
 frame=pd.read_parquet(feature_path)
 frame=frame.sort_values(["date","ticker"]).reset_index(drop=True)
 frame=frame[(frame.date>="2005-09-14")&(frame.date<"2026-09-15")]
 policies=json.loads(Path(policy_path).read_text())
 membership={(date,ticker):value for date,ticker,value in policies["membership"]}
 risk_veto=policies["risk_veto"]
 blocked={ticker:frozenset(dates) for ticker,dates in policies["blocked"].items()}
 sessions={str(x)[:10] for x in frame.date}
 if not sessions.issubset(risk_veto):raise ValueError("Missing risk decisions for sessions")
 if not {(str(r.date)[:10],r.ticker) for r in frame[["date","ticker"]].itertuples(index=False)}.issubset(membership):raise ValueError("Incomplete membership")
 prepared=PreparedSessions(frame)
 cache=ResultCache(db_path)
 members=[initial(niche)]
 seen={members[0].identity()}
 while len(members)<population:
  child=mutate(rng.choice(members),rng)
  if child.identity() not in seen:members.append(child);seen.add(child.identity())
 best=None;hits=0;history=[];start=0
 checkpoint=Path(output)/("checkpoint_"+niche+".json")
 if checkpoint.exists():
  state=json.loads(checkpoint.read_text())
  expected={"niche":niche,"sha":sha,"policy_sha":policy_sha,"code_sha":code_sha,"population":population,"seed":random_seed}
  if any(state.get(k)!=v for k,v in expected.items()):raise ValueError("Checkpoint mismatch: "+niche)
  start=state["generation"]
  if start>generations:raise ValueError("Checkpoint exceeds budget")
  rng.setstate(pickle.loads(base64.b64decode(state["rng"])))
  members=[Genome(**g) for g in state["members"]]
  history=state["history"]
  if state.get("best"):
   b=state["best"];best=(b["score"],Genome(**b["genome"]),b["result"])
 for gen in range(start,generations):
  scored=[]
  for genome in members:
   key=cache.key(genome,sha,"DEV79_FULL","guarded-v2:"+policy_sha+":"+code_sha)
   result=cache.get(key);hit=result is not None
   if result is None:
    result=guarded_evaluate(prepared,genome,blocked=blocked,membership=membership,risk_veto=risk_veto,annual_cash_yield=policies["cash_proxy_annual_yield"])
    cache.put(key,result)
   hits+=int(hit)
   scored.append((fitness(result),genome,result))
  scored.sort(key=lambda x:(-x[0],x[1].identity()))
  if best is None or scored[0][0]>best[0]:best=scored[0]
  history.append({"generation":gen+1,"best_fitness":scored[0][0],"unique":len({g.identity() for _,g,_ in scored})})
  parents=[g for _,g,_ in scored[:max(2,population//4)]]
  next_members=parents.copy();seen={g.identity() for g in next_members};tries=0
  while len(next_members)<population:
   tries+=1
   if tries>10000:raise RuntimeError("Novelty exhausted")
   child=mutate(crossover(rng.choice(parents),rng.choice(parents),rng),rng)
   if child.identity() not in seen:next_members.append(child);seen.add(child.identity())
  members=next_members
  state={"niche":niche,"sha":sha,"policy_sha":policy_sha,"code_sha":code_sha,"population":population,"seed":random_seed,
         "generation":gen+1,"rng":base64.b64encode(pickle.dumps(rng.getstate())).decode(),
         "members":[asdict(g) for g in members],"history":history,
         "best":{"score":best[0],"genome":asdict(best[1]),"result":best[2]}}
  temp=checkpoint.with_suffix(".tmp");temp.write_text(json.dumps(state));temp.replace(checkpoint)
 cache.close()
 return {"niche":niche,"evaluations":generations*population,"cache_hits":hits,
         "best_fitness":best[0],"best_result":best[2],"history":history}
def main(argv=None):
 p=argparse.ArgumentParser()
 p.add_argument("--features",required=True)
 p.add_argument("--output",required=True)
 p.add_argument("--generations",type=int,default=1)
 p.add_argument("--population-per-niche",type=int,default=4)
 p.add_argument("--workers",type=int,default=1)
 p.add_argument("--diagnostic-only",action="store_true")
 p.add_argument("--policy-file",required=True)
 a=p.parse_args(argv)
 if not a.diagnostic_only:raise ValueError("Certification gate closed; specify --diagnostic-only for research")
 if a.generations<1 or a.population_per_niche<4 or not 1<=a.workers<=8:raise ValueError("Invalid budget")
 feature=Path(a.features);meta=feature.with_suffix(".manifest.json")
 if not feature.is_file() or not meta.is_file():raise ValueError("Verified prepared feature artifact required")
 config=json.loads(meta.read_text())
 if config.get("sector_map") is None:raise ValueError("PIT sector feature map missing")
 if config.get("engine")!="ga5-research-v4":raise ValueError("Feature engine version mismatch")
 if not config.get("source_sha256"):raise ValueError("Missing source fingerprint")
 if not config.get("sector_map"):raise ValueError("Empty sector mapping")
 policy_path=Path(a.policy_file)
 policies=json.loads(policy_path.read_text())
 if not isinstance(policies.get("membership"),list) or not isinstance(policies.get("risk_veto"),dict) or not isinstance(policies.get("blocked"),dict) or not isinstance(policies.get("cash_proxy_annual_yield"),(float,int)):raise ValueError("Complete guarded policy file required")
 if not {"dividends","stock_splits"}.issubset(pd.read_parquet(feature).columns):raise ValueError("Corporate action fields required")
 policy_sha=digest_file(policy_path)
 out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
 jobs=[(n,str(feature),str(out/"evaluations.sqlite"),digest_file(feature),
        a.generations,a.population_per_niche,1700+i,str(out),str(policy_path),policy_sha) for i,n in enumerate(NICHES)]
 started=time.monotonic()
 with concurrent.futures.ProcessPoolExecutor(max_workers=a.workers) as pool:
  results=list(pool.map(niche_worker,jobs))
 report={"status":"DIAGNOSTIC_ONLY","workers":a.workers,"elapsed_s":round(time.monotonic()-started,2),
         "total_evaluations":sum(x["evaluations"] for x in results),"evaluator":"guarded-v2", "code_sha256":engine_fingerprint(), "policy_sha256":policy_sha,
         "cache_hits":sum(x["cache_hits"] for x in results),"niches":results}
 tmp=out/"report.tmp";tmp.write_text(json.dumps(report,indent=2));tmp.replace(out/"report.json")
 return report
if __name__=="__main__":print(json.dumps(main(),indent=2))
