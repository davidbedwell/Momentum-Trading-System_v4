#!/usr/bin/env python3
from __future__ import annotations
import argparse,gzip,json,math,os,statistics
from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path
from MTS_V4.derived_market_updater import YFinanceDailyMarketSource
from MTS_V4.derived_market_store import DerivedMarketQuery,ParquetDerivedMarketStore
from MTS_V4.search_candidate_analysis import _compile_signal
FAMS=("MOMENTUM","BREAKOUT","TREND","MEAN_REVERSION","VOLATILITY","VOLUME_LIQUIDITY","RELATIVE_CROSS_SECTIONAL","MARKET_REGIME_STRUCTURE")
DEPTHS=(.01,.02,.03,.05,.075,.10);REC=(.25,.50,.75,1.0);G={}
def uniq(r,f):
 s=set();z=[]
 for o in ("random","ga"):
  for c in r["families"][f][o]["top_candidates"]:
   if c["candidate_id"] not in s:s.add(c["candidate_id"]);z.append(c)
 return z
def accepted(sig,h):
 z=[];n=0
 for i,on in enumerate(sig):
  if on and i>=n:z.append(i);n=i+h
 return z
def efficiency(vals):
 if len(vals)<2:return None
 den=sum(abs(vals[i]-vals[i-1]) for i in range(1,len(vals)))
 return abs(vals[-1]-vals[0])/den if den else None
def init(cfg,meta):G.update(cfg=cfg,meta=meta)
def cp(t):return Path(G["cfg"]["checkpoint"])/f"{t}.json.gz"
def process(t):
 p=cp(t)
 if p.exists():
  try:
   with gzip.open(p,"rt") as f:r=json.load(f)
   if r.get("format")=="MTS_V4_TRAJECTORY_PARTIAL_RECOVERY_TARGET_V1":return t,True,r
  except:pass
 m=G["meta"][t];sr=json.loads(Path(m["report"]).read_text());store=ParquetDerivedMarketStore(G["cfg"]["root"])
 pred=list(store.query(DerivedMarketQuery(universe_id=sr["universe_id"],feature_set_id="mts_market_predictors",feature_set_version=sr["predictor_feature_set_version"],security_ids=(sr["security_id"],))));pred.sort(key=lambda x:str(x["effective_date"]))
 pd=[str(x["effective_date"])[:10] for x in pred];bars=list(YFinanceDailyMarketSource().fetch(ticker=t,start_date=pd[0],end_date=pd[-1]));bars.sort(key=lambda x:str(x["date"]));bd={str(x["date"])[:10]:i for i,x in enumerate(bars)};rows=[]
 for fam in FAMS:
  for cand in uniq(sr,fam):
   h=int(cand["genome"]["forward_horizon"])
   for pi in accepted(_compile_signal(pred,cand),h):
    ri=bd.get(pd[pi])
    if ri is None or ri+1>=len(bars) or ri+h>=len(bars):continue
    ei=ri+1;xi=ri+h
    if xi<=ei:continue
    path=bars[ei:xi+1];ref=float(path[0]["open"]);exitp=float(path[-1]["close"])
    lows=[float(x["low"]) for x in path];cl=[float(x["close"]) for x in path];mi=min(range(len(lows)),key=lambda j:lows[j]);trough=lows[mi];mae=trough/ref-1
    reclaim=next((j for j in range(mi+1,len(path)) if cl[j]>=ref),None)
    decline_cl=[ref]+cl[:mi+1];traj={"mae":mae,"mae_offset":mi,"decline_per_session":mae/max(mi,1),
      "max_one_session_close_decline":min([cl[0]/ref-1]+[cl[j]/cl[j-1]-1 for j in range(1,mi+1)]) if mi>=0 else None,
      "decline_efficiency":efficiency(decline_cl)}
    for n in (1,2,3):
     j=min(n,len(path)-1);cur=min(lows[:j+1])/ref-1
     traj[f"mae_fraction_by_{n}s"]=abs(cur/mae) if mae<0 else None
    if mae<0:
     band10=abs(mae)*.10;band25=abs(mae)*.25
     traj["sessions_within_10pct_of_mae"]=sum(abs((x/ref-1)-mae)<=band10 for x in lows)
     traj["sessions_within_25pct_of_mae"]=sum(abs((x/ref-1)-mae)<=band25 for x in lows)
    if reclaim is not None:
     traj["sessions_mae_to_reclaim"]=reclaim-mi;traj["rebound_per_session"]=((cl[reclaim]/trough)-1)/max(reclaim-mi,1)
     traj["rebound_decline_speed_ratio"]=traj["rebound_per_session"]/abs(traj["decline_per_session"]) if traj["decline_per_session"] else None
     traj["rebound_efficiency"]=efficiency([trough]+cl[mi:reclaim+1])
    cells=[]
    for dep in DEPTHS:
     for frac in REC:
      runlow=ref;eligible=False;confirm=None;confirm_trough=None;eligj=None
      for j,x in enumerate(path[:-1]):
       runlow=min(runlow,float(x["low"]))
       ae=runlow/ref-1
       if ae<=-dep:
        if not eligible:eligible=True;eligj=j
        target=runlow+frac*(ref-runlow)
        if float(x["close"])>=target:
         confirm=j;confirm_trough=runlow;break
      z={"depth":dep,"recovery_fraction":frac,"eligible":eligible,"eligibility_offset":eligj,"confirmation_offset":confirm}
      if confirm is not None and confirm+1<len(path):
       ep=float(path[confirm+1]["open"]);post=path[confirm+1:]
       z.update({"entry":ep,"entry_vs_reference":ep/ref-1,"sessions_to_confirmation":confirm-(eligj or 0),"terminal_return":exitp/ep-1,"win":exitp>ep,
        "post_entry_mae":min(float(q["low"])/ep-1 for q in post),"post_entry_mfe":max(float(q["high"])/ep-1 for q in post),
        "original_terminal_return":exitp/ref-1,"delta_vs_original_return":exitp/ep-exitp/ref,"running_trough_at_confirmation":confirm_trough})
      cells.append(z)
    rows.append({"ticker":t,"cohort":m["cohort"],"family":fam,"candidate_id":cand["candidate_id"],"horizon":h,"signal_date":pd[pi],"reference":ref,
      "original_terminal_return":exitp/ref-1,"trajectory":traj,"cells":cells})
 out={"format":"MTS_V4_TRAJECTORY_PARTIAL_RECOVERY_TARGET_V1","ticker":t,"rows":rows,"search_run":False,"refit":False,"rule_selection":False,"verification_a_accessed":False,"verification_b_accessed":False}
 p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix(".tmp.gz")
 with gzip.open(tmp,"wt") as f:json.dump(out,f,separators=(",",":"))
 os.replace(tmp,p);return t,False,out
def med(x):return statistics.median(x) if x else None
def main():
 a=argparse.ArgumentParser()
 for x in ("d2-dir","d2b-dir","d2-classification","d2b-manifest","derived-market-root","checkpoint-dir","output"):a.add_argument("--"+x,required=True)
 a.add_argument("--workers",type=int,default=8);q=a.parse_args();meta={}
 for x in json.loads(Path(q.d2_classification).read_text())["tickers"]:
  t=x["ticker"];meta[t]={"cohort":"D2_50","report":str(Path(q.d2_dir)/f"{t}_COMPUTATIONAL_SEARCH_20260930.json")}
 for x in json.loads(Path(q.d2b_manifest).read_text())["tickers"]:
  t=x["ticker"];meta[t]={"cohort":"D2B_SUPPLEMENT","report":str(Path(q.d2b_dir)/f"{t}_COMPUTATIONAL_SEARCH_20260930.json")}
 if len(meta)!=67:raise RuntimeError(f"expected 67, got {len(meta)}")
 cfg={"root":q.derived_market_root,"checkpoint":q.checkpoint_dir};rows=[]
 with ProcessPoolExecutor(max_workers=q.workers,initializer=init,initargs=(cfg,meta)) as ex:
  fs={ex.submit(process,t):t for t in sorted(meta)}
  for n,f in enumerate(as_completed(fs),1):
   t,reused,r=f.result();rows.extend(r["rows"]);print(f"[{n}/67] {'RESUMED' if reused else 'COMPLETE'}={t}",flush=True)
 table=[]
 for dep in DEPTHS:
  for frac in REC:
   z=[c for r in rows for c in r["cells"] if c["depth"]==dep and c["recovery_fraction"]==frac and c["eligible"]]
   cf=[c for c in z if c.get("entry") is not None];origw=sum(c.get("original_terminal_return",0)>0 for c in z);retw=sum(c.get("original_terminal_return",0)>0 for c in cf)
   table.append({"depth":dep,"recovery_fraction":frac,"eligible":len(z),"confirmed":len(cf),"confirmation_rate":len(cf)/len(z) if z else None,
    "win_rate":sum(c["win"] for c in cf)/len(cf) if cf else None,"mean_return":statistics.fmean(c["terminal_return"] for c in cf) if cf else None,"median_return":med([c["terminal_return"] for c in cf]),
    "median_entry_vs_reference":med([c["entry_vs_reference"] for c in cf]),"median_sessions_to_confirmation":med([c["sessions_to_confirmation"] for c in cf]),
    "median_post_mae":med([c["post_entry_mae"] for c in cf]),"median_post_mfe":med([c["post_entry_mfe"] for c in cf]),
    "original_winners_filtered":origw-retw,"original_losers_filtered":(len(z)-origw)-(len(cf)-retw)})
 # trajectory by original outcome
 tr={}
 for lab,fn in (("ORIGINAL_WIN",lambda r:r["original_terminal_return"]>0),("ORIGINAL_LOSS",lambda r:r["original_terminal_return"]<=0)):
  rr=[r["trajectory"] for r in rows if r["trajectory"]["mae"]<0 and fn(r)];keys=("mae","mae_offset","decline_per_session","max_one_session_close_decline","mae_fraction_by_1s","mae_fraction_by_2s","mae_fraction_by_3s","sessions_within_10pct_of_mae","sessions_within_25pct_of_mae","sessions_mae_to_reclaim","rebound_per_session","rebound_decline_speed_ratio","decline_efficiency","rebound_efficiency")
  tr[lab]={"n":len(rr),**{k:{"median":med([x[k] for x in rr if x.get(k) is not None]),"mean":statistics.fmean([x[k] for x in rr if x.get(k) is not None]) if any(x.get(k) is not None for x in rr) else None} for k in keys}}
 out={"format":"MTS_V4_DISCOVERY_TRAJECTORY_PARTIAL_RECOVERY_SUMMARY_V1","trade_count":len(rows),"trajectory_by_original_outcome":tr,"partial_recovery_table":table,"detail_location":q.checkpoint_dir,
  "search_run":False,"refit":False,"rule_selection":False,"verification_a_accessed":False,"verification_b_accessed":False,"sol_calls":0}
 Path(q.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("REPORT="+q.output);print(f"TRADES={len(rows)}")
 for lab,z in tr.items():print(f"{lab} n={z['n']} medMAE={z['mae']['median']:.4f} medToMAE={z['mae_offset']['median']:.1f} medDeclinePerSession={z['decline_per_session']['median']:.4f} medReboundSpeedRatio={(z['rebound_decline_speed_ratio']['median'] or 0):.3f}")
 print("PARTIAL_RECOVERY_TABLE")
 for z in table:print(f"AE={z['depth']:.1%} REC={z['recovery_fraction']:.0%} eligible={z['eligible']} confirmed={z['confirmed']} rate={(z['confirmation_rate'] or 0):.3f} win={(z['win_rate'] or 0):.3f} meanRet={(z['mean_return'] or 0):.4f} medEntryVsRef={(z['median_entry_vs_reference'] or 0):+.4f} medDays={(z['median_sessions_to_confirmation'] or 0):.1f} filtW={z['original_winners_filtered']} filtL={z['original_losers_filtered']}")
 print("SEARCH_RUN=False REFIT=False RULE_SELECTION=False VERIFICATION_A_ACCESSED=False VERIFICATION_B_ACCESSED=False SOL_CALLS=0")
if __name__=="__main__":main()
