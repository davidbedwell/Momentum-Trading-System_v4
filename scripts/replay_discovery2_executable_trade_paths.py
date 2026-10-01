#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,statistics
from collections import defaultdict
from pathlib import Path
from MTS_V4.derived_market_store import DerivedMarketQuery,ParquetDerivedMarketStore
from MTS_V4.derived_market_updater import YFinanceDailyMarketSource
from MTS_V4.search_candidate_analysis import _compile_signal
from MTS_V4.trade_path_analysis import TradePathError,simulate_long_path,summarize_paths

STOP_FRACTIONS=(0.02,0.05,0.10,0.15)
BOUNDARY="DISCOVERY2_FROZEN_STRUCTURE_EXECUTABLE_REPLAY_ONLY_NO_TARGET_SEARCH_INSPECTION_NOT_VALIDATION"

def key(r): return (r["trigger_family"],tuple(sorted(r["member_families"])),r["form"],int(r["size"]))

def eligible(predictors,signals,outcomes,col):
 dates={str(r["effective_date"]) for r in outcomes if r.get(col) is not None}
 return [bool(on) and str(row["effective_date"]) in dates for row,on in zip(predictors,signals)]

def accepted_indices(signals,h):
 out=[]; nxt=0
 for i,on in enumerate(signals):
  if on and i>=nxt: out.append(i);nxt=i+h
 return out

def paths_for(signals,predictors,outcomes,h,raw,bydate):
 sig=eligible(predictors,signals,outcomes,f"forward_return_{h}__v1")
 accepted=accepted_indices(sig,h); paths=[];excluded=[]
 for pi in accepted:
  dt=str(predictors[pi]["effective_date"]);ri=bydate.get(dt)
  if ri is None: excluded.append({"signal_date":dt,"reason":"SIGNAL_DATE_MISSING_FROM_REACQUIRED_OHLCV"});continue
  try: paths.append(simulate_long_path(bars=raw,signal_index=ri,horizon_sessions=h,stop_fractions=STOP_FRACTIONS))
  except TradePathError as e: excluded.append({"signal_date":dt,"reason":str(e)})
 return paths,excluded

def metric_delta(a,b):
 def d(path):
  x=a
  for p in path:x=x[p]
  y=b
  for p in path:y=y[p]
  return None if x is None or y is None else x-y
 return d

def main():
 p=argparse.ArgumentParser();p.add_argument("--replication",required=True);p.add_argument("--source-manifest",required=True)
 p.add_argument("--derived-market-root",required=True);p.add_argument("--output",required=True);a=p.parse_args()
 rep=json.loads(Path(a.replication).read_text());man=json.loads(Path(a.source_manifest).read_text())
 if rep.get("verification_accessed") is not False or rep.get("methodology",{}).get("target_search_results_read") is not False:
  raise RuntimeError("scientific boundary violated")
 mrows={(r["ticker"],r["candidate_id"]):r for r in man["retained_candidates"]}; ccache={}
 def cand(st,cid):
  k=(st,cid)
  if k in ccache:return ccache[k]
  mr=mrows[k];trade=json.loads(Path(mr["source_report"]).read_text());search=json.loads(Path(trade["source_search_report"]).read_text())
  for opt in mr["optimizers"]:
   for c in trade["results"][mr["family"]][opt]:
    if c.get("candidate_id")==cid: ccache[k]=(search,{"candidate_id":c["candidate_id"],"family_id":c["family_id"],"genome":c["genome"]});return ccache[k]
  raise RuntimeError("candidate not found")
 store=ParquetDerivedMarketStore(a.derived_market_root);bytarget=defaultdict(list)
 for r in rep["applications"]:bytarget[(r["ticker"],r["security_id"])].append(r)
 results=[]
 for ti,((ticker,sid),apps) in enumerate(sorted(bytarget.items()),1):
  s0,_=cand(apps[0]["source_ticker"],apps[0]["member_candidate_ids"][0])
  predictors=list(store.query(DerivedMarketQuery(universe_id=s0["universe_id"],feature_set_id="mts_market_predictors",feature_set_version=s0["predictor_feature_set_version"],security_ids=(sid,))))
  predictors.sort(key=lambda r:str(r["effective_date"]))
  outcomes=list(store.query(DerivedMarketQuery(universe_id=s0["universe_id"],feature_set_id="mts_historical_outcomes",feature_set_version=s0["outcome_feature_set_version"],security_ids=(sid,))))
  raw=list(YFinanceDailyMarketSource().fetch(ticker=ticker,start_date=str(predictors[0]["effective_date"]),end_date=str(predictors[-1]["effective_date"])))
  raw.sort(key=lambda r:str(r["date"]));bydate={str(r["date"]):i for i,r in enumerate(raw)}
  for r in apps:
   members=[cand(r["source_ticker"],cid)[1] for cid in r["member_candidate_ids"]]
   ids=r["member_candidate_ids"];tidx=ids.index(r["trigger_candidate_id"]);sigs=[_compile_signal(predictors,c) for c in members]
   if r["form"]=="ALL":combo=[all(s[i] for s in sigs) for i in range(len(predictors))]
   elif r["form"]=="2_OF_3":combo=[sum(bool(s[i]) for s in sigs)>=2 for i in range(len(predictors))]
   elif r["form"]=="3_OF_4":combo=[sum(bool(s[i]) for s in sigs)>=3 for i in range(len(predictors))]
   else:raise RuntimeError("unknown form")
   gated=[bool(sigs[tidx][i]) and bool(combo[i]) for i in range(len(combo))]
   h=int(members[tidx]["genome"]["forward_horizon"])
   cp,ce=paths_for(gated,predictors,outcomes,h,raw,bydate);bp,be=paths_for(sigs[tidx],predictors,outcomes,h,raw,bydate)
   cs=summarize_paths(cp);bs=summarize_paths(bp)
   stop_delta={}
   for sk in cs["stop_scenarios"]:
    stop_delta[sk]={"stop_fraction":cs["stop_scenarios"][sk]["stop_fraction"],
      "delta_mean_realized_return":metric_delta(cs,bs)(["stop_scenarios",sk,"realized_return","mean"]),
      "delta_median_realized_return":metric_delta(cs,bs)(["stop_scenarios",sk,"realized_return","median"]),
      "delta_gross_ev_r":metric_delta(cs,bs)(["stop_scenarios",sk,"gross_ev_r"])}
   results.append({**{k:r[k] for k in ("ticker","security_id","sector","size_band","source_ticker","trigger_family","member_families","form","size","trigger_candidate_id","member_candidate_ids")},
    "horizon_sessions":h,"composite":cs,"trigger_baseline":bs,
    "delta_fixed_mean":metric_delta(cs,bs)(["fixed_horizon_return","mean"]),
    "delta_fixed_median":metric_delta(cs,bs)(["fixed_horizon_return","median"]),
    "stop_deltas":stop_delta,"composite_excluded":ce,"trigger_excluded":be})
  print(f"[{ti}/{len(bytarget)}] EXECUTABLE={ticker}",flush=True)
 groups=defaultdict(list)
 for r in results:groups[key(r)].append(r)
 structures=[]
 for k,rs in sorted(groups.items()):
  usable=[r for r in rs if r["composite"]["trade_count"]>=10 and r["trigger_baseline"]["trade_count"]>=10]
  improved=[r for r in usable if r["delta_fixed_mean"] is not None and r["delta_fixed_median"] is not None and r["delta_fixed_mean"]>0 and r["delta_fixed_median"]>0]
  stop_summary={}
  for sk in [f"{x:.6f}" for x in STOP_FRACTIONS]:
   sr=[r for r in usable if sk in r["stop_deltas"]]
   both=[r for r in sr if r["stop_deltas"][sk]["delta_mean_realized_return"]>0 and r["stop_deltas"][sk]["delta_median_realized_return"]>0]
   stop_summary[sk]={"usable_instances":len(sr),"improved_mean_and_median_instances":len(both)}
  structures.append({"trigger_family":k[0],"member_families":list(k[1]),"form":k[2],"size":k[3],
   "applications":len(rs),"usable_instances_n_ge_10_both":len(usable),"fixed_horizon_improved_instances":len(improved),
   "usable_tickers":len({r["ticker"] for r in usable}),"improved_tickers":len({r["ticker"] for r in improved}),
   "stop_summary":stop_summary})
 out={"format":"MTS_V4_DISCOVERY2_FROZEN_STRUCTURE_EXECUTABLE_REPLAY_V1","scientific_boundary":BOUNDARY,
  "source_replication":a.replication,"source_manifest":a.source_manifest,
  "execution_policy":{"raw_market_source":"YFINANCE_DAILY_AUTO_ADJUSTED_REACQUIRED_NOT_PERSISTED","signal_information_cutoff":"COMPLETED_SIGNAL_DAY_BAR",
   "entry":"NEXT_TRADING_SESSION_OPEN","exit":"CLOSE_ON_SIGNAL_DATE_PLUS_FORWARD_HORIZON_TRADING_SESSIONS",
   "overlapping_positions":"PROHIBITED_WITHIN_EACH_SIGNAL_STREAM","exploratory_stop_fractions":list(STOP_FRACTIONS),
   "gap_through_stop":"FILL_AT_OBSERVED_OPEN","intraday_stop_touch":"FILL_AT_STOP","profit_target":"NONE","transaction_costs":"NOT_APPLIED"},
  "methodology":{"target_search_results_read":False,"new_search":False,"new_genomes":False,"winner_selection":False,"refit":False,
   "all_transported_applications_preserved":True,"net_ev":"UNAVAILABLE_REQUIRES_FROZEN_ALL_IN_COST_INPUT"},
  "applications":results,"structures":structures,"candidate_selection_mutated":False,"verification_accessed":False,"sol_calls":0}
 Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print(f"REPORT={a.output}");print(f"TARGET_TICKERS={len(bytarget)}");print(f"APPLICATIONS={len(results)}")
 for s in structures:print(f"{s['trigger_family']}|{'+'.join(s['member_families'])}|{s['form']} usable={s['usable_instances_n_ge_10_both']} improved={s['fixed_horizon_improved_instances']} tickers={s['improved_tickers']}/{s['usable_tickers']}")
 print("TARGET_SEARCH_RESULTS_READ=False");print("VERIFICATION_ACCESSED=False");print("SOL_CALLS=0")
if __name__=="__main__":main()
