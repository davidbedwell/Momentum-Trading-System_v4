#!/usr/bin/env python3
from __future__ import annotations
import argparse,gzip,hashlib,json,math,os,statistics
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path
from MTS_V4.derived_market_store import DerivedMarketQuery,ParquetDerivedMarketStore
from MTS_V4.derived_market_updater import YFinanceDailyMarketSource
from MTS_V4.search_candidate_analysis import _compile_signal

FAMS=("MOMENTUM","BREAKOUT","TREND","MEAN_REVERSION","VOLATILITY","VOLUME_LIQUIDITY","RELATIVE_CROSS_SECTIONAL","MARKET_REGIME_STRUCTURE")
OFFSETS=(0.01,0.02,0.03,0.05,0.075,0.10)
G={}

def uniq(r,f):
 seen=set();out=[]
 for opt in ("random","ga"):
  for c in r["families"][f][opt]["top_candidates"]:
   if c["candidate_id"] not in seen:seen.add(c["candidate_id"]);out.append(c)
 return out
def pct(xs,p):
 if not xs:return None
 x=sorted(xs);q=(len(x)-1)*p;lo=int(math.floor(q));hi=int(math.ceil(q))
 return x[lo] if lo==hi else x[lo]+(x[hi]-x[lo])*(q-lo)
def stats(xs):
 x=[float(v) for v in xs if v is not None and math.isfinite(float(v))]
 return {"n":len(x),"mean":statistics.fmean(x) if x else None,"p25":pct(x,.25),"median":pct(x,.5),"p75":pct(x,.75),"p90":pct(x,.9)}
def accepted(sig,h):
 out=[];nxt=0
 for i,on in enumerate(sig):
  if on and i>=nxt:out.append(i);nxt=i+h
 return out
def init_worker(cfg,meta):G.update(cfg=cfg,meta=meta)
def checkpoint(t):return Path(G["cfg"]["checkpoint_dir"])/f"{t}.json.gz"

def process(t):
 cp=checkpoint(t)
 if cp.exists():
  try:
   with gzip.open(cp,"rt") as f:r=json.load(f)
   if r.get("format")=="MTS_V4_DISCOVERY_ADVERSE_EXCURSION_TARGET_V1" and r.get("ticker")==t:return t,True,r
  except Exception:pass
 m=G["meta"][t];r=json.loads(Path(m["report_path"]).read_text());store=ParquetDerivedMarketStore(G["cfg"]["derived_root"])
 pred=list(store.query(DerivedMarketQuery(universe_id=r["universe_id"],feature_set_id="mts_market_predictors",feature_set_version=r["predictor_feature_set_version"],security_ids=(r["security_id"],))))
 pred.sort(key=lambda x:str(x["effective_date"]));dates=[str(x["effective_date"])[:10] for x in pred]
 raw=list(YFinanceDailyMarketSource().fetch(ticker=t,start_date=dates[0],end_date=dates[-1]));raw.sort(key=lambda x:str(x["date"]))
 bydate={str(x["date"])[:10]:i for i,x in enumerate(raw)}
 trades=[]
 for fam in FAMS:
  for c in uniq(r,fam):
   h=int(c["genome"]["forward_horizon"]);sig=_compile_signal(pred,c)
   for pi in accepted(sig,h):
    sd=dates[pi];ri=bydate.get(sd)
    if ri is None or ri+1>=len(raw) or ri+h>=len(raw):continue
    entry_i=ri+1;exit_i=ri+h
    if exit_i<entry_i:continue
    entry=float(raw[entry_i]["open"]);exitp=float(raw[exit_i]["close"])
    if entry<=0:continue
    path=raw[entry_i:exit_i+1]
    lows=[float(b["low"]) for b in path];highs=[float(b["high"]) for b in path]
    maes=[lo/entry-1 for lo in lows];mfes=[hi/entry-1 for hi in highs]
    mi=min(range(len(maes)),key=lambda i:maes[i]);xi=max(range(len(mfes)),key=lambda i:mfes[i])
    base_ret=exitp/entry-1
    delayed={}
    for off in OFFSETS:
     limit=entry*(1-off);fill_i=None;fillp=None
     for j,b in enumerate(path):
      op=float(b["open"]);lo=float(b["low"])
      if op<=limit:fill_i=j;fillp=op;break
      if lo<=limit:fill_i=j;fillp=limit;break
     k=f"{off:.3f}"
     if fill_i is None:
      delayed[k]={"filled":False,"original_winner_missed":base_ret>0,"original_loser_avoided":base_ret<0}
     else:
      pp=path[fill_i:];fl=[float(b["low"])/fillp-1 for b in pp];fh=[float(b["high"])/fillp-1 for b in pp]
      delayed[k]={"filled":True,"fill_session_offset":fill_i,"fill_price":fillp,
       "terminal_return":exitp/fillp-1,"return_delta_vs_original":exitp/fillp-1-base_ret,
       "post_fill_mae":min(fl),"post_fill_mfe":max(fh)}
    trades.append({"ticker":t,"cohort":m["cohort"],"family":fam,"candidate_id":c["candidate_id"],"horizon":h,
     "signal_date":sd,"entry_date":str(raw[entry_i]["date"])[:10],"exit_date":str(raw[exit_i]["date"])[:10],
     "original_entry":entry,"original_terminal_return":base_ret,"mae":min(maes),"mfe":max(mfes),
     "mae_session_offset":mi,"mfe_session_offset":xi,"mae_before_mfe":mi<xi,"delayed":delayed})
 result={"format":"MTS_V4_DISCOVERY_ADVERSE_EXCURSION_TARGET_V1","ticker":t,"cohort":m["cohort"],"trades":trades,
  "search_run":False,"refit":False,"winner_selection":False,"verification_a_accessed":False,"verification_b_accessed":False,"sol_calls":0}
 cp.parent.mkdir(parents=True,exist_ok=True);tmp=cp.with_suffix(cp.suffix+".tmp")
 with gzip.open(tmp,"wt",compresslevel=6) as f:json.dump(result,f,separators=(",",":"))
 os.replace(tmp,cp);return t,False,result

def summarize(rows):
 base={"trades":len(rows),"mae":stats([r["mae"] for r in rows]),"mfe":stats([r["mfe"] for r in rows]),
  "mae_session_offset":stats([r["mae_session_offset"] for r in rows]),"mfe_session_offset":stats([r["mfe_session_offset"] for r in rows]),
  "mae_before_mfe_fraction":sum(r["mae_before_mfe"] for r in rows)/len(rows) if rows else None,
  "original_terminal_return":stats([r["original_terminal_return"] for r in rows])}
 ds={}
 for off in OFFSETS:
  k=f"{off:.3f}";z=[r["delayed"][k] for r in rows];filled=[x for x in z if x["filled"]]
  ds[k]={"eligible":len(z),"filled":len(filled),"fill_rate":len(filled)/len(z) if z else None,
   "unfilled":len(z)-len(filled),"missed_original_winners":sum(bool(x.get("original_winner_missed")) for x in z),
   "avoided_original_losers":sum(bool(x.get("original_loser_avoided")) for x in z),
   "sessions_to_fill":stats([x["fill_session_offset"] for x in filled]),"terminal_return":stats([x["terminal_return"] for x in filled]),
   "return_delta_vs_same_filled_originals":stats([x["return_delta_vs_original"] for x in filled]),
   "post_fill_mae":stats([x["post_fill_mae"] for x in filled]),"post_fill_mfe":stats([x["post_fill_mfe"] for x in filled])}
 base["delayed_entries"]=ds;return base

def main():
 p=argparse.ArgumentParser()
 for x in ("protocol","d2-dir","d2b-dir","d2-classification","d2b-manifest","derived-market-root","checkpoint-dir","output"):p.add_argument("--"+x,required=True)
 p.add_argument("--workers",type=int,default=8);a=p.parse_args()
 protocol_sha=hashlib.sha256(Path(a.protocol).read_bytes()).hexdigest()
 meta={}
 for x in json.loads(Path(a.d2_classification).read_text())["tickers"]:
  t=x["ticker"];meta[t]={"cohort":"D2_50","report_path":str(Path(a.d2_dir)/f"{t}_COMPUTATIONAL_SEARCH_20260930.json")}
 for x in json.loads(Path(a.d2b_manifest).read_text())["tickers"]:
  t=x["ticker"];meta[t]={"cohort":"D2B_SUPPLEMENT","report_path":str(Path(a.d2b_dir)/f"{t}_COMPUTATIONAL_SEARCH_20260930.json")}
 if len(meta)!=67:raise RuntimeError(f"expected exactly 67 Discovery tickers, got {len(meta)}")
 cfg={"derived_root":a.derived_market_root,"checkpoint_dir":a.checkpoint_dir};done=[]
 with ProcessPoolExecutor(max_workers=a.workers,initializer=init_worker,initargs=(cfg,meta)) as ex:
  fut={ex.submit(process,t):t for t in sorted(meta)}
  n=0
  for f in as_completed(fut):
   t,reused,r=f.result();done.append(r);n+=1;print(f"[{n}/67] {'RESUMED' if reused else 'COMPLETE'}={t}",flush=True)
 rows=[r for tr in done for r in tr["trades"]]
 groups={"overall":{"ALL":rows},"ticker":defaultdict(list),"family":defaultdict(list),"horizon":defaultdict(list),"cohort":defaultdict(list),"outcome_sign":defaultdict(list)}
 for r in rows:
  groups["ticker"][r["ticker"]].append(r);groups["family"][r["family"]].append(r);groups["horizon"][str(r["horizon"])].append(r);groups["cohort"][r["cohort"]].append(r)
  groups["outcome_sign"]["WIN" if r["original_terminal_return"]>0 else "LOSS_OR_FLAT"].append(r)
 summary={g:{k:summarize(v) for k,v in sorted(x.items())} for g,x in groups.items()}
 out={"format":"MTS_V4_DISCOVERY_ADVERSE_EXCURSION_DELAYED_ENTRY_V1","protocol_sha256":protocol_sha,
  "scientific_boundary":"DISCOVERY_ONLY_HYPOTHESIS_GENERATION_NOT_VALIDATION",
  "offsets":list(OFFSETS),"ticker_count":67,"trade_count":len(rows),
  "atr_normalization":"UNAVAILABLE_IN_V1_UNLESS_SEPARATELY_RESOLVED_FROM_FROZEN_PREDICTORS",
  "summary":summary,"checkpoint_dir":a.checkpoint_dir,"search_run":False,"refit":False,"winner_selection":False,
  "verification_a_accessed":False,"verification_b_accessed":False,"sol_calls":0}
 Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 o=summary["overall"]["ALL"];print("REPORT="+a.output);print(f"TICKERS=67 TRADES={len(rows)}")
 print(f"MAE mean={o['mae']['mean']:.6f} p25={o['mae']['p25']:.6f} median={o['mae']['median']:.6f} p75={o['mae']['p75']:.6f} p90={o['mae']['p90']:.6f}")
 print(f"MFE mean={o['mfe']['mean']:.6f} median={o['mfe']['median']:.6f} MAE_BEFORE_MFE={o['mae_before_mfe_fraction']:.3f}")
 for off in OFFSETS:
  z=o["delayed_entries"][f"{off:.3f}"];print(f"OFFSET={off:.3%} fill={z['filled']}/{z['eligible']} rate={z['fill_rate']:.3f} missedW={z['missed_original_winners']} avoidedL={z['avoided_original_losers']} medRet={(z['terminal_return']['median'] or 0):.6f} medDelta={(z['return_delta_vs_same_filled_originals']['median'] or 0):.6f} medPostMAE={(z['post_fill_mae']['median'] or 0):.6f}")
 print("SEARCH_RUN=False");print("REFIT=False");print("WINNER_SELECTION=False");print("VERIFICATION_A_ACCESSED=False");print("VERIFICATION_B_ACCESSED=False");print("SOL_CALLS=0")
if __name__=="__main__":main()
