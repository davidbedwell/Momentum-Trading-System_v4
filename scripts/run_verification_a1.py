#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,statistics,gzip,os
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path
from MTS_V4.derived_market_store import DerivedMarketQuery,ParquetDerivedMarketStore
from MTS_V4.search_candidate_analysis import _compile_signal

EXPECTED_PROTOCOL_SHA="d70d6cf94a76aeccb1c53a11048ca3c46fee1cd59cf3de1cc61073993af15fa1"
EXPECTED_SELECTION_SHA="7b2e52076175d28c01350a7caa0d7e334df2f2bd7045ffc73b092d42a29a76a5"
FAMS=("MOMENTUM","BREAKOUT","TREND","MEAN_REVERSION","VOLATILITY","VOLUME_LIQUIDITY","RELATIVE_CROSS_SECTIONAL","MARKET_REGIME_STRUCTURE")
G={}

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def uniq(r,f):
 s=set();z=[]
 for o in ("random","ga"):
  for c in r["families"][f][o]["top_candidates"]:
   if c["candidate_id"] not in s:s.add(c["candidate_id"]);z.append(c)
 return z
def accepted(signals,predictors,outcomes,h):
 oi={(str(r["security_id"]),str(r["effective_date"])):r for r in outcomes};out=[];cool=0;col=f"forward_return_{h}__v1"
 for pr,on in zip(predictors,signals):
  r=oi.get((str(pr["security_id"]),str(pr["effective_date"])))
  v=None if r is None else r.get(col)
  if on and v is not None and cool==0:
   out.append(float(v));cool=h
  if cool:cool-=1
 return out
def stats(v):
 return {"n":len(v),"mean":statistics.fmean(v) if v else None,"median":statistics.median(v) if v else None}
def cp_path(t):return Path(G["checkpoint_dir"])/f"{t}.json.gz"
def process_target(row):
 t=row["ticker"];sid=row["security_id"];cp=cp_path(t)
 if cp.exists():
  try:
   with gzip.open(cp,"rt") as f:r=json.load(f)
   if r.get("format")=="MTS_V4_VERIFICATION_A1_TARGET_V1" and r.get("ticker")==t:return t,True,r
  except Exception:pass
 store=ParquetDerivedMarketStore(G["derived_root"])
 template=G["template"]
 pred=list(store.query(DerivedMarketQuery(universe_id=template["universe_id"],feature_set_id="mts_market_predictors",feature_set_version=template["predictor_feature_set_version"],security_ids=(sid,))))
 pred.sort(key=lambda x:str(x["effective_date"]))
 out=list(store.query(DerivedMarketQuery(universe_id=template["universe_id"],feature_set_id="mts_historical_outcomes",feature_set_version=template["outcome_feature_set_version"],security_ids=(sid,))))
 comp_rows=[]
 for fz in G["frozen"]:
  sigs=[_compile_signal(pred,c) for c in fz["members"]]; ids=fz["member_candidate_ids"];ti=ids.index(fz["trigger_candidate_id"])
  if fz["form"]=="ALL": combo=[all(s[i] for s in sigs) for i in range(len(pred))]
  elif fz["form"]=="2_OF_3": combo=[sum(bool(s[i]) for s in sigs)>=2 for i in range(len(pred))]
  elif fz["form"]=="3_OF_4": combo=[sum(bool(s[i]) for s in sigs)>=3 for i in range(len(pred))]
  else: raise RuntimeError("unknown composite form")
  gated=[bool(sigs[ti][i]) and bool(combo[i]) for i in range(len(pred))]
  h=int(fz["members"][ti]["genome"]["forward_horizon"]);cv=accepted(gated,pred,out,h);bv=accepted(sigs[ti],pred,out,h)
  cs,bs=stats(cv),stats(bv);usable=cs["n"]>=10 and bs["n"]>=10
  good=usable and cs["mean"]>bs["mean"] and cs["median"]>bs["median"]
  comp_rows.append({"source_ticker":fz["source_ticker"],"trigger_family":fz["trigger_family"],"member_families":fz["member_families"],"form":fz["form"],"size":fz["size"],"trigger_candidate_id":fz["trigger_candidate_id"],"member_candidate_ids":fz["member_candidate_ids"],"horizon":h,"composite":cs,"trigger":bs,"usable":usable,"positive_both":good,"delta_mean":(cs["mean"]-bs["mean"]) if usable else None,"delta_median":(cs["median"]-bs["median"]) if usable else None})
 fam_rows=[]
 for f in FAMS:
  for src,c in G["sources"][f]:
   h=int(c["genome"]["forward_horizon"]);col=f"forward_return_{h}__v1"
   base=[float(x[col]) for x in out if x.get(col) is not None]
   if not base:continue
   vals=[]
   oi={(str(x["security_id"]),str(x["effective_date"])):x for x in out}
   for pr,on in zip(pred,_compile_signal(pred,c)):
    if not on:continue
    x=oi.get((str(pr["security_id"]),str(pr["effective_date"])))
    if x is not None and x.get(col) is not None:vals.append(float(x[col]))
   if len(vals)<10:continue
   em=statistics.fmean(vals)-statistics.fmean(base);ed=statistics.median(vals)-statistics.median(base)
   fam_rows.append({"source_ticker":src,"family":f,"candidate_id":c["candidate_id"],"horizon":h,"n":len(vals),"excess_mean":em,"excess_median":ed,"positive_both":em>0 and ed>0})
 r={"format":"MTS_V4_VERIFICATION_A1_TARGET_V1","ticker":t,"security_id":sid,"sector":row["sector"],"size_band":row["size_band"],"composites":comp_rows,"families":fam_rows,"search_run":False,"refit":False,"verification_b_accessed":False,"sol_calls":0}
 cp.parent.mkdir(parents=True,exist_ok=True);tmp=cp.with_suffix(cp.suffix+".tmp")
 with gzip.open(tmp,"wt",compresslevel=6) as f:json.dump(r,f,separators=(",",":"))
 os.replace(tmp,cp);return t,False,r

def main():
 p=argparse.ArgumentParser()
 for x in ("protocol","selection","frozen-robustness","source-manifest","d2-dir","d2b-dir","d2-classification","d2b-manifest","derived-market-root","output","checkpoint-dir"):p.add_argument("--"+x,required=True)
 p.add_argument("--workers",type=int,default=8);a=p.parse_args()
 if sha(a.protocol)!=EXPECTED_PROTOCOL_SHA:raise RuntimeError("protocol hash mismatch")
 if sha(a.selection)!=EXPECTED_SELECTION_SHA:raise RuntimeError("selection hash mismatch")
 sel=json.loads(Path(a.selection).read_text())
 if len(sel["a1"])!=20 or len(sel["verification_a_remaining"])!=80:raise RuntimeError("selection cardinality mismatch")
 if any(sel.get(k) is not False for k in ("outcomes_accessed","predictors_accessed","prices_accessed","search_run","verification_b_accessed")):raise RuntimeError("selection boundary flags invalid")
 rob=json.loads(Path(a.frozen_robustness).read_text());man=json.loads(Path(a.source_manifest).read_text())
 mrows={(r["ticker"],r["candidate_id"]):r for r in man["retained_candidates"]};cache={}
 def load(st,cid):
  k=(st,cid)
  if k in cache:return cache[k]
  mr=mrows[k];trade=json.loads(Path(mr["source_report"]).read_text());search=json.loads(Path(trade["source_search_report"]).read_text())
  for opt in mr["optimizers"]:
   for c in trade["results"][mr["family"]][opt]:
    if c.get("candidate_id")==cid:
     z={"candidate_id":c["candidate_id"],"family_id":c["family_id"],"genome":c["genome"]};cache[k]=(search,z);return cache[k]
  raise RuntimeError("candidate not found")
 frozen=[]
 for r in rob["instances"]:
  members=[load(r["ticker"],cid)[1] for cid in r["member_candidate_ids"]]
  frozen.append({"source_ticker":r["ticker"],"trigger_candidate_id":r["trigger_candidate_id"],"trigger_family":r["trigger_family"],"member_candidate_ids":r["member_candidate_ids"],"member_families":r["member_families"],"form":r["form"],"size":r["size"],"members":members})
 meta={}
 for x in json.loads(Path(a.d2_classification).read_text())["tickers"]:meta[x["ticker"]]=Path(a.d2_dir)/f"{x['ticker']}_COMPUTATIONAL_SEARCH_20260930.json"
 for x in json.loads(Path(a.d2b_manifest).read_text())["tickers"]:meta[x["ticker"]]=Path(a.d2b_dir)/f"{x['ticker']}_COMPUTATIONAL_SEARCH_20260930.json"
 sources=defaultdict(list);template=None
 for t,pth in sorted(meta.items()):
  r=json.loads(Path(pth).read_text());template=template or r
  for f in FAMS:
   for c in uniq(r,f):sources[f].append((t,c))
 global G
 G={"checkpoint_dir":a.checkpoint_dir,"derived_root":a.derived_market_root,"frozen":frozen,"sources":dict(sources),"template":template}
 done=[]
 with ProcessPoolExecutor(max_workers=a.workers) as ex:
  fut={ex.submit(process_target,r):r["ticker"] for r in sel["a1"]}
  n=0
  for x in as_completed(fut):
   t,reused,r=x.result();done.append(r);n+=1;print(f"[{n}/20] {'RESUMED' if reused else 'COMPLETE'}={t}",flush=True)
 cgroups=defaultdict(list)
 for tr in done:
  for r in tr["composites"]:cgroups[(r["trigger_family"],tuple(sorted(r["member_families"])),r["form"],r["size"])].append((tr["ticker"],r))
 csum=[]
 for k,rs in sorted(cgroups.items()):
  u=[(t,r) for t,r in rs if r["usable"]];g=[(t,r) for t,r in u if r["positive_both"]]
  csum.append({"trigger_family":k[0],"member_families":list(k[1]),"form":k[2],"size":k[3],"usable":len(u),"positive_both":len(g),"fraction":len(g)/len(u) if u else None,"usable_tickers":len({t for t,_ in u}),"positive_tickers":len({t for t,_ in g}),"median_delta_mean":statistics.median([r["delta_mean"] for _,r in u]) if u else None,"median_delta_median":statistics.median([r["delta_median"] for _,r in u]) if u else None})
 fsum=[]
 for f in FAMS:
  rs=[(tr["ticker"],r) for tr in done for r in tr["families"] if r["family"]==f];g=[x for x in rs if x[1]["positive_both"]]
  fsum.append({"family":f,"usable":len(rs),"positive_both":len(g),"fraction":len(g)/len(rs) if rs else None,"usable_targets":len({t for t,_ in rs}),"positive_targets":len({t for t,_ in g}),"usable_sources":len({r["source_ticker"] for _,r in rs}),"positive_sources":len({r["source_ticker"] for _,r in g}),"median_excess_mean":statistics.median([r["excess_mean"] for _,r in rs]) if rs else None,"median_excess_median":statistics.median([r["excess_median"] for _,r in rs]) if rs else None})
 out={"format":"MTS_V4_VERIFICATION_A1_STRUCTURAL_REPLAY_V1","protocol_sha256":EXPECTED_PROTOCOL_SHA,"selection_sha256":EXPECTED_SELECTION_SHA,"a1_count":20,"remaining_a_count":80,"methodology":{"new_search":False,"new_genomes":False,"refit":False,"winner_selection":False,"usable_n_min":10,"transaction_costs":"NOT_APPLIED_STRUCTURAL_VERIFICATION_ONLY"},"composite_summary":csum,"family_summary":fsum,"targets":done,"verification_b_accessed":False,"sol_calls":0}
 Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("REPORT="+a.output)
 for z in csum:print(f"COMP {z['trigger_family']}|{'+'.join(z['member_families'])}|{z['form']} positive={z['positive_both']}/{z['usable']} frac={(z['fraction'] or 0):.3f} tickers={z['positive_tickers']}/{z['usable_tickers']} medDM={(z['median_delta_mean'] or 0):.6f} medDMed={(z['median_delta_median'] or 0):.6f}")
 for z in sorted(fsum,key=lambda q:(-(q["fraction"] or -1),q["family"])):print(f"FAM {z['family']} positive={z['positive_both']}/{z['usable']} frac={(z['fraction'] or 0):.3f} targets={z['positive_targets']}/{z['usable_targets']} sources={z['positive_sources']}/{z['usable_sources']} medEM={(z['median_excess_mean'] or 0):.6f} medED={(z['median_excess_median'] or 0):.6f}")
 print("SEARCH_RUN=False");print("REFIT=False");print("VERIFICATION_B_ACCESSED=False");print("SOL_CALLS=0")
if __name__=="__main__":main()
