#!/usr/bin/env python3
import argparse, json, subprocess, sys
from collections import defaultdict
from pathlib import Path

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifest", required=True)
    p.add_argument("--output-dir", required=True)
    a=p.parse_args()

    manifest=json.loads(Path(a.manifest).read_text())
    if manifest.get("scientific_boundary") != "DISCOVERY_SELECTION_FOR_FALSIFICATION_ONLY_NOT_VALIDATION_NOT_PROMOTION":
        raise SystemExit("unexpected manifest scientific boundary")
    if manifest.get("candidate_selection_mutated") is not False:
        raise SystemExit("manifest candidate_selection_mutated must be false")
    if manifest.get("verification_accessed") is not False:
        raise SystemExit("manifest verification_accessed must be false")

    grouped=defaultdict(list)
    for r in manifest["retained_candidates"]:
        grouped[r["ticker"]].append(r)

    outdir=Path(a.output_dir); outdir.mkdir(parents=True, exist_ok=True)
    total=0
    reports=[]
    for ticker in sorted(grouped):
        cmd=[sys.executable,"scripts/analyze_frozen_candidate_falsification.py"]
        for i,r in enumerate(grouped[ticker],1):
            name=f"{ticker}_{r['family']}_{i}"
            optimizer=r["optimizers"][0]
            spec=f"{name}={r['source_report']}:{r['family']}:{optimizer}:0"
            cmd += ["--candidate", spec]
        target=outdir / f"{ticker}_FROZEN_CANDIDATE_FALSIFICATION_20260930.json"
        cmd += ["--output", str(target)]
        subprocess.run(cmd, check=True)
        total += len(grouped[ticker])
        reports.append(str(target))

    summary={
        "format":"MTS_V4_11_TICKER_FALSIFICATION_BATCH_V1",
        "scientific_boundary":"DISCOVERY_FALSIFICATION_ONLY_NOT_VALIDATION_NOT_PROMOTION",
        "source_manifest":a.manifest,
        "ticker_count":len(grouped),
        "candidate_count":total,
        "reports":reports,
        "candidate_selection_mutated":False,
        "verification_accessed":False,
        "sol_calls":0,
    }
    summary_path=outdir/"MTS_11_TICKER_FALSIFICATION_BATCH_SUMMARY_20260930.json"
    summary_path.write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print("="*72)
    print(f"SUMMARY={summary_path}")
    print(f"TICKERS={len(grouped)}")
    print(f"CANDIDATES={total}")
    print("CANDIDATE_SELECTION_MUTATED=False")
    print("VERIFICATION_ACCESSED=False")
    print("SOL_CALLS=0")

if __name__=="__main__":
    main()
