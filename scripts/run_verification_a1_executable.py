#!/usr/bin/env python3
from __future__ import annotations
import argparse,gzip,hashlib,json,os,statistics
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path
from MTS_V4.derived_market_store import DerivedMarketQuery,ParquetDerivedMarketStore
from MTS_V4.derived_market_updater import YFinanceDailyMarketSource
from MTS_V4.search_candidate_analysis import _compile_signal
from MTS_V4.trade_path_analysis import TradePathError,simulate_long_path,summarize_paths

EXPECTED_PROTOCOL_SHA="d70d6cf94a76aeccb1c53a11048ca3c46fee1cd59cf3de1cc61073993af15fa1"
EXPECTED_SELECTION_SHA="7b2e52076175d28c01350a7caa0d7e334df2f2bd7045ffc73b092d42a29a76a5"
EXPECTED_STRUCTURAL_SHA="8d3043019f3196a33b3992d536635dfa706c45ffe523aa963bd4f23edd56b0ce"
STOP_FRACTIONS=(0.02,0.05,0.10,0.15)
G={}

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def key(r): return (r["trigger_family"],tuple(sorted(r["member_families"])),r["form"],int(r["size"]))
def eligible(predictors,signals,outcomes,col):
 dates={str(r["effective_date"]) for r in outcomes if r.get(col) is not None}
 return [bool(on) and str(row["effective_date"]) in dates for row,on in zip(predictors,signals)]
def accepted_indices(signals,h):
 out=[];nxt=0
 for i,on in enumerate(signals):
  if on and i>=nxt:out.append(i);nxt=i+h
 return out
def paths_for(signals,predictors,outcomes,h,raw,bydate):
 sig=eligible(predictors,signals,outcomes,f"forward_return_{h}__v1");accepted=accepted_indices(sig,h);paths=[];excluded=[]
 for pi in accepted:
  dt=str(predictors[pi]["effective_date"]);ri=bydate.get(dt)
  if ri is None:excluded.append({"signal_date":dt,"reason":"SIGNAL_DATE_MISSING_FROM_REACQUIRED_OHLCV"});continue
  try:paths.append(simulate_long_path(bars=raw,signal_index=ri,horizon_sessions=h,stop_fractions=STOP_FRACTIONS))
  except TradePathError as e:excluded.append({"signal_date":dt,"reason":str(e)})
 return paths,excluded
def md(a,b,path):
 x=a;y=b
 for p in path:x=x[p];y=y[p]
 return None if x is None or y is None else x-y
def cp_path(t):return Path(G["checkpoint_dir"])/f"{t}.json.gz"

def process_target(target):
 t=target["ticker"];sid=target["security_id"];cp=cp_path(t)
 if cp.exists():
  try:
   with gzip.open(cp,"rt") as f:r=json.load(f)
   if r.get("format")=="MTS_V4_VERIFICATION_A1_EXECUTABLE_TARGET_V1" and r.get("ticker")==t:return t,True,r
  except Exception:pass
 store=ParquetDerivedMarketStore(G["derived_root"])
 apps=G["apps_by_ticker"][t]
 template=G["templates"][t]
 predictors=list(store.query(DerivedMarketQuery(universe_id=template["universe_id"],feature_set_id="mts_market_predictors",feature_set_version=template["predictor_feature_set_version"],security_ids=(sid,))))
 predictors.sort(key=lambda r:str(r["effective_date"]))
 outcomes=list(store.query(DerivedMarketQuery(universe_id=template["universe_id"],feature_set_id="mts_historical_outcomes",feature_set_version=template["outcome_feature_set_version"],security_ids=(sid,))))
 raw=list(YFinanceDailyMarketSource().fetch(ticker=t,start_date=str(predictors[0]["effective_date"]),end_date=str(predictors[-1]["effective_date"])))
 raw.sort(key=lambda r:str(r["date"]));bydate={str(r["date"]):i for i,r in enumerate(raw)}
 rows=[]
 for r in apps:
  members=[G["candidates"][(r["source_ticker"],cid)] for cid in r["member_candidate_ids"]]
  ids=r["member_candidate_ids"];tidx=ids.index(r["trigger_candidate_id"]);sigs=[_compile_signal(predictors,c) for c in members]
  if r["form"]=="ALL":combo=[all(s[i] for s in sigs) for i in range(len(predictors))]
  elif r["form"]=="2_OF_3":combo=[sum(bool(s[i]) for s in sigs)>=2 for i in range(len(predictors))]
  elif r["form"]=="3_OF_4":combo=[sum(bool(s[i]) for s in sigs)>=3 for i in range(len(predictors))]
  else:raise RuntimeError("unknown form")
  gated=[bool(sigs[tidx][i]) and bool(combo[i]) for i in range(len(combo))]
  h=int(members[tidx]["genome"]["forward_horizon"])
  cpv,ce=paths_for(gated,predictors,outcomes,h,raw,bydate);bpv,be=paths_for(sigs[tidx],predictors,outcomes,h,raw,bydate)
  cs=summarize_paths(cpv);bs=summarize_paths(bpv)
  sd={}
  for sk in cs["stop_scenarios"]:
   sd[sk]={"stop_fraction":cs["stop_scenarios"][sk]["stop_fraction"],
    "delta_mean_realized_return":md(cs,bs,["stop_scenarios",sk,"realized_return","mean"]),
    "delta_median_realized_return":md(cs,bs,["stop_scenarios",sk,"realized_return","median"]),
    "delta_gross_ev_r":md(cs,bs,["stop_scenarios",sk,"gross_ev_r"])}
  rows.append({k:r[k] for k in ("ticker","security_id","sector","size_band","source_ticker","trigger_family","member_families","form","size","trigger_candidate_id","member_candidate_ids")} | {
   "horizon_sessions":h,"composite":cs,"trigger_baseline":bs,
   "delta_fixed_mean":md(cs,bs,["fixed_horizon_return","mean"]),
   "delta_fixed_median":md(cs,bs,["fixed_horizon_return","median"]),
   "stop_deltas":sd,"composite_excluded":ce,"trigger_excluded":be})
 result={"format":"MTS_V4_VERIFICATION_A1_EXECUTABLE_TARGET_V1","ticker":t,"security_id":sid,"applications":rows,
  "execution_policy":G["execution_policy"],"search_run":False,"refit":False,"winner_selection":False,
  "verification_a_remaining_accessed":False,"verification_b_accessed":False,"sol_calls":0}
 cp.parent.mkdir(parents=True,exist_ok=True);tmp=cp.with_suffix(cp.suffix+".tmp")
 with gzip.open(tmp,"wt",compresslevel=6) as f:json.dump(result,f,separators=(",",":"))
 os.replace(tmp,cp);return t,False,result

def main():
 p=argparse.ArgumentParser()
 for x in ("protocol","selection","structural-report","source-manifest","derived-market-root","checkpoint-dir","output"):p.add_argument("--"+x,required=True)
 p.add_argument("--workers",type=int,default=8);a=p.parse_args()
 if sha(a.protocol)!=EXPECTED_PROTOCOL_SHA:raise RuntimeError("protocol hash mismatch")
 if sha(a.selection)!=EXPECTED_SELECTION_SHA:raise RuntimeError("selection hash mismatch")
 if sha(a.structural_report)!=EXPECTED_STRUCTURAL_SHA:raise RuntimeError("frozen structural report hash mismatch")
 sel=json.loads(Path(a.selection).read_text());sr=json.loads(Path(a.structural_report).read_text());man=json.loads(Path(a.source_manifest).read_text())
 if sr.get("format")!="MTS_V4_VERIFICATION_A1_STRUCTURAL_REPLAY_V1":raise RuntimeError("wrong structural report format")
 if sr.get("a1_count")!=20 or sr.get("remaining_a_count")!=80 or sr.get("verification_b_accessed") is not False:raise RuntimeError("structural boundary mismatch")
 if sr.get("protocol_sha256")!=EXPECTED_PROTOCOL_SHA or sr.get("selection_sha256")!=EXPECTED_SELECTION_SHA:raise RuntimeError("structural lineage mismatch")
 targets={r["ticker"]:r for r in sel["a1"]}
 if set(targets)!={r["ticker"] for r in sr["targets"]}:raise RuntimeError("A1 target set mismatch")
 mrows={(r["ticker"],r["candidate_id"]):r for r in man["retained_candidates"]};candidates={};templates={}
 def cand(st,cid):
  k=(st,cid)
  if k in candidates:return candidates[k]
  mr=mrows[k];trade=json.loads(Path(mr["source_report"]).read_text());search=json.loads(Path(trade["source_search_report"]).read_text())
  templates.setdefault(st,search)
  for opt in mr["optimizers"]:
   for c in trade["results"][mr["family"]][opt]:
    if c.get("candidate_id")==cid:
     z={"candidate_id":c["candidate_id"],"family_id":c["family_id"],"genome":c["genome"]};candidates[k]=z;return z
  raise RuntimeError("candidate not found")
 apps_by=defaultdict(list);template_by={}
 for tr in sr["targets"]:
  t=tr["ticker"]
  for r in tr["composites"]:
   for cid in r["member_candidate_ids"]:cand(r["source_ticker"],cid)
   apps_by[t].append({"ticker":t,"security_id":tr["security_id"],"sector":tr["sector"],"size_band":tr["size_band"],
    "source_ticker":r["source_ticker"],"trigger_family":r["trigger_family"],"member_families":r["member_families"],"form":r["form"],"size":r["size"],
    "trigger_candidate_id":r["trigger_candidate_id"],"member_candidate_ids":r["member_candidate_ids"]})
   template_by[t]=templates[r["source_ticker"]]
 execution_policy={"raw_market_source":"YFINANCE_DAILY_AUTO_ADJUSTED_REACQUIRED_NOT_PERSISTED","signal_information_cutoff":"COMPLETED_SIGNAL_DAY_BAR",
  "entry":"NEXT_TRADING_SESSION_OPEN","exit":"CLOSE_ON_SIGNAL_DATE_PLUS_FORWARD_HORIZON_TRADING_SESSIONS",
  "overlapping_positions":"PROHIBITED_WITHIN_EACH_SIGNAL_STREAM","exploratory_stop_fractions":list(STOP_FRACTIONS),
  "gap_through_stop":"FILL_AT_OBSERVED_OPEN","intraday_stop_touch":"FILL_AT_STOP","profit_target":"NONE","transaction_costs":"NOT_APPLIED"}
 global G
 G={"derived_root":a.derived_market_root,"checkpoint_dir":a.checkpoint_dir,"apps_by_ticker":dict(apps_by),"templates":template_by,"candidates":candidates,"execution_policy":execution_policy}
 completed=[]
 with ProcessPoolExecutor(max_workers=a.workers) as ex:
  fut={ex.submit(process_target,targets[t]):t for t in sorted(targets)}
  n=0
  for f in as_completed(fut):
   t,reused,r=f.result();completed.append(r);n+=1;print(f"[{n}/20] {'RESUMED' if reused else 'EXECUTABLE'}={t}",flush=True)
 groups=defaultdict(list)
 for tr in completed:
  for r in tr["applications"]:groups[key(r)].append(r)
 structures=[]
 for k,rs in sorted(groups.items()):
  usable=[r for r in rs if r["composite"]["trade_count"]>=10 and r["trigger_baseline"]["trade_count"]>=10]
  improved=[r for r in usable if r["delta_fixed_mean"] is not None and r["delta_fixed_median"] is not None and r["delta_fixed_mean"]>0 and r["delta_fixed_median"]>0]
  ss={}
  for sk in [f"{x:.6f}" for x in STOP_FRACTIONS]:
   q=[r for r in usable if sk in r["stop_deltas"]]
   both=[r for r in q if r["stop_deltas"][sk]["delta_mean_realized_return"] is not None and r["stop_deltas"][sk]["delta_median_realized_return"] is not None and r["stop_deltas"][sk]["delta_mean_realized_return"]>0 and r["stop_deltas"][sk]["delta_median_realized_return"]>0]
   ss[sk]={"usable_instances":len(q),"improved_mean_and_median_instances":len(both),
    "median_delta_mean_realized_return":statistics.median([r["stop_deltas"][sk]["delta_mean_realized_return"] for r in q]) if q else None,
    "median_delta_median_realized_return":statistics.median([r["stop_deltas"][sk]["delta_median_realized_return"] for r in q]) if q else None}
  structures.append({"trigger_family":k[0],"member_families":list(k[1]),"form":k[2],"size":k[3],"applications":len(rs),
   "usable_instances_n_ge_10_both":len(usable),"fixed_horizon_improved_instances":len(improved),
   "usable_tickers":len({r["ticker"] for r in usable}),"improved_tickers":len({r["ticker"] for r in improved}),
   "median_delta_fixed_mean":statistics.median([r["delta_fixed_mean"] for r in usable]) if usable else None,
   "median_delta_fixed_median":statistics.median([r["delta_fixed_median"] for r in usable]) if usable else None,"stop_summary":ss})
 out={"format":"MTS_V4_VERIFICATION_A1_EXECUTABLE_REPLAY_V1","scientific_boundary":"FROZEN_A1_EXECUTABLE_PATH_ONLY",
  "protocol_sha256":EXPECTED_PROTOCOL_SHA,"selection_sha256":EXPECTED_SELECTION_SHA,"structural_report_sha256":EXPECTED_STRUCTURAL_SHA,
  "a1_count":20,"remaining_a_count":80,"execution_policy":execution_policy,
  "methodology":{"new_search":False,"new_genomes":False,"refit":False,"winner_selection":False,"all_frozen_composite_instances_preserved":True,
   "net_ev":"UNAVAILABLE_REQUIRES_FROZEN_ALL_IN_COST_INPUT"},
  "targets":completed,"structures":structures,"verification_a_remaining_accessed":False,"verification_b_accessed":False,"sol_calls":0}
 Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("REPORT="+a.output)
 for s in structures:print(f"COMP {s['trigger_family']}|{'+'.join(s['member_families'])}|{s['form']} usable={s['usable_instances_n_ge_10_both']} improved={s['fixed_horizon_improved_instances']} tickers={s['improved_tickers']}/{s['usable_tickers']} medDM={(s['median_delta_fixed_mean'] or 0):.6f} medDMed={(s['median_delta_fixed_median'] or 0):.6f}")
 print("SEARCH_RUN=False");print("REFIT=False");print("WINNER_SELECTION=False");print("VERIFICATION_A_REMAINING_ACCESSED=False");print("VERIFICATION_B_ACCESSED=False");print("SOL_CALLS=0")
if __name__=="__main__":main()
