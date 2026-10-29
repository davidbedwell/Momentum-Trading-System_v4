#!/usr/bin/env python3
import json, hashlib
from pathlib import Path
import numpy as np, pandas as pd
import run_ga_redesign_approved_20261006 as ga

def main():
 d67,d50,dev,dates,X,RX,rf,names,groups,P,px,COST=ga.build_arrays(); fs=ga.folds(dev)
 frozen=[]; meta=[]
 for fi in range(4):
  p=ga.ROOT/f"Research/State/MTS_GA_REDESIGN_FOLD{fi}_TRAIN_FINALISTS_20261006.json"
  if not p.exists(): raise SystemExit(f"MISSING_FOLD_{fi}")
  payload=json.loads(p.read_text())
  if payload.get("fold")!=fi: raise SystemExit(f"FOLD_ID_MISMATCH_{fi}")
  tr,bl=fs[fi]
  if payload["train_tickers"]!=tr: raise SystemExit(f"TRAIN_SET_MISMATCH_{fi}")
  expected=hashlib.sha256("\n".join(bl).encode()).hexdigest()
  if payload["blind_tickers_sha256"]!=expected: raise SystemExit(f"BLIND_HASH_MISMATCH_{fi}")
  frozen.append({"path":str(p),"sha256":ga.sha(p)}); meta.append(payload)
 print("BARRIER_OK",json.dumps(frozen),flush=True)
 idx={t:i for i,t in enumerate(dev)}; blind=[]
 for fi,(tr,bl) in enumerate(fs):
  rows=[]; bi=np.array([idx[t] for t in bl])
  for n,z in enumerate(meta[fi]["finalists"]):
   g=z["genome"]; bm=ga.evaluate(g,X,RX,rf,dates,bi,COST)
   sens={str(cc):ga.evaluate(g,X,RX,rf,dates,bi,cc) for cc in (0,5,10,20)}
   eps={}; pr,_,_,_=ga.simulate(g,X[:,bi,:],RX[:,bi],rf,COST[:,bi])
   for name,a,b in ga.EPISODES:
    mask=(dates>=pd.Timestamp(a))&(dates<=pd.Timestamp(b)); eps[name]=ga.v2.metrics(pr[mask],dates[mask]) if mask.any() else None
   rows.append({"train":z["train"],"blind":bm,"cost_sensitivity":sens,"episodes":eps,"genome":g})
   print(f"BLIND FOLD={fi} FINALIST={n+1}/{len(meta[fi]['finalists'])}",flush=True)
  blind.append({"fold":fi,"rows":rows})
 out={"format":"MTS_GA_REDESIGN_APPROVED_V1","status":"DEV117_COMPLETE","freeze_sha256":ga.sha(ga.FREEZE),"features":names,"groups":groups,"comparators":{"SPY":ga.spy_comparator(dates),"SAFE":ga.v2.metrics(rf,dates),"SPY_sha256":ga.sha(ga.SPY)},"training_freezes":frozen,"blind_transport":blind,"validation_note":"80/37 folds are cross-stock transport; crash evidence counted by independent episode, not fold-session multiplication.","next_stage":"DV25 remains sealed pending post-DEV117 decision"}
 ga.OUT.write_text(json.dumps(out,indent=2))
 rp=ga.ROOT/"Research/Reports/MTS_GA_REDESIGN_FINAL_REPORT_20261006.md"
 lines=["# MTS GA Redesign — Final DEV117 Report","",f"Status: {out['status']}","","## Frozen training sets"]+[f"- Fold {i}: {x['sha256']}" for i,x in enumerate(frozen)]+["","## Blind cross-stock transport"]
 for f in blind:
  lines.append(f"### Fold {f['fold']}")
  for r in f["rows"]: lines.append(f"- Train CAGR {r['train']['cagr']:.3%}, MDD {r['train']['mdd']:.3%}; blind CAGR {r['blind']['cagr']:.3%}, MDD {r['blind']['mdd']:.3%}; SAFE {r['blind']['safe_fraction']:.3%}")
 lines+=["","## Governance","All four training finalist sets were frozen and SHA-256 hashed before any blind37 replay. DV25/A25/A75/B100 were not opened. Crash episodes are reported as independent market episodes, not multiplied across folds."]
 rp.write_text("\n".join(lines)+"\n"); print("COMPLETE",ga.OUT,rp,flush=True)
if __name__=="__main__": main()
