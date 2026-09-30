#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,hashlib,json
from collections import Counter
from pathlib import Path

def main():
 p=argparse.ArgumentParser(description="Attach frozen sector evidence to an already-run Discovery-2 sample without changing selection or outcomes.")
 p.add_argument("--sample-manifest",required=True);p.add_argument("--sector-csv",required=True);p.add_argument("--output",required=True)
 a=p.parse_args(); src=Path(a.sample_manifest); sec=Path(a.sector_csv); out=Path(a.output)
 d=json.loads(src.read_text())
 with sec.open(newline="",encoding="utf-8") as f: rows=list(csv.DictReader(f))
 sectors={str(r["security_id"]).strip():str(r["sector"]).strip() for r in rows}
 if len(sectors)!=len(rows) or any(not x or x.upper()=="UNCLASSIFIED" for x in sectors.values()):
  raise RuntimeError("sector evidence must be unique and fully classified")
 tagged=[]
 for x in d["tickers"]:
  y=dict(x); y["sector"]=sectors.get(str(x["security_id"]),"")
  if not y["sector"]: raise RuntimeError(f'missing sector for {x["ticker"]}')
  tagged.append(y)
 artifact={"format":"MTS_V4_DISCOVERY_2_RETROACTIVE_SECTOR_CLASSIFICATION_V1",
  "scientific_role":"DESCRIPTIVE_CROSS_ANALYSIS_ONLY_NOT_RETROACTIVE_STRATIFIED_SELECTION",
  "source_sample_manifest":str(src.resolve()),"source_sample_sha256":hashlib.sha256(src.read_bytes()).hexdigest(),
  "sector_csv":str(sec.resolve()),"sector_csv_sha256":hashlib.sha256(sec.read_bytes()).hexdigest(),
  "selection_changed":False,"search_rerun":False,"outcomes_inspected_for_classification":False,
  "tickers":tagged,"sector_counts":dict(sorted(Counter(x["sector"] for x in tagged).items())),
  "size_counts":dict(sorted(Counter(x["size_band"] for x in tagged).items())),
  "candidate_selection_mutated":False,"verification_accessed":False,"sol_calls":0}
 if out.exists(): raise RuntimeError(f"refusing to overwrite frozen artifact: {out}")
 out.write_text(json.dumps(artifact,indent=2,sort_keys=True)+"\n")
 print(f"OUTPUT={out}");print("COUNT="+str(len(tagged)));print("SECTOR_COUNTS="+json.dumps(artifact["sector_counts"],sort_keys=True))
 print("SELECTION_CHANGED=False");print("SEARCH_RERUN=False");print("VERIFICATION_ACCESSED=False");print("SOL_CALLS=0")
if __name__=="__main__": main()
