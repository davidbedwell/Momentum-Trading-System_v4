from __future__ import annotations

import argparse
import json
from pathlib import Path

from MTS_V4.frozen_candidate_falsification import analyze_frozen_candidate, pairwise_candidate_overlap


def _parser():
    p=argparse.ArgumentParser(description="Falsification diagnostics for already-frozen Discovery trade-path candidates.")
    p.add_argument("--candidate",action="append",required=True,
        help="NAME=PATH_REPORT:FAMILY:OPTIMIZER[:RANK], rank defaults to 0")
    p.add_argument("--output",required=True)
    return p


def _load(spec):
    name,rest=spec.split("=",1)
    parts=rest.split(":")
    if len(parts) not in (3,4):
        raise RuntimeError("--candidate must be NAME=PATH_REPORT:FAMILY:OPTIMIZER[:RANK]")
    path,family,optimizer=parts[:3]
    rank=int(parts[3]) if len(parts)==4 else 0
    report=json.loads(Path(path).read_text())
    if report.get("scientific_boundary") != "DISCOVERY_POST_SEARCH_ANALYSIS_ONLY_NOT_VALIDATION_NOT_PROMOTION":
        raise RuntimeError(f"{name}: unsupported scientific boundary")
    candidate=report["results"][family][optimizer][rank]
    return name,path,family,optimizer,rank,report,candidate


def main(argv=None):
    args=_parser().parse_args(argv)
    loaded=[_load(s) for s in args.candidate]
    partitions={x[5]["partition_id"] for x in loaded}
    tickers={x[5]["ticker"] for x in loaded}
    if len(partitions)!=1 or len(tickers)!=1:
        raise RuntimeError("all candidates must share one ticker and one frozen scientific partition")
    raw={name:c for name,_,_,_,_,_,c in loaded}
    results={name:analyze_frozen_candidate(c) for name,c in raw.items()}
    out={
        "format":"MTS_V4_FROZEN_CANDIDATE_FALSIFICATION_V1",
        "ticker":next(iter(tickers)),"partition_id":next(iter(partitions)),
        "scientific_boundary":"DISCOVERY_FALSIFICATION_ONLY_NOT_VALIDATION_NOT_PROMOTION",
        "candidate_selection_mutated":False,
        "diagnostics":{
            "chronology_and_concentration":"AVAILABLE",
            "chronological_stability":"AVAILABLE_FIXED_THIRDS_NO_REFIT",
            "cross_candidate_same_entry_overlap":"AVAILABLE",
            "path_downside_and_leave_one_out":"AVAILABLE",
            "market_sector_attribution":"UNAVAILABLE_REQUIRES_EXPLICIT_BENCHMARK_CONTEXT_EVIDENCE",
            "net_transaction_cost_ev":"UNAVAILABLE_REQUIRES_FROZEN_ALL_IN_COST_ASSUMPTION",
        },
        "sources":[{
            "name":name,"path":path,"family":family,"optimizer":optimizer,"rank":rank,
            "candidate_id":candidate["candidate_id"],
        } for name,path,family,optimizer,rank,_,candidate in loaded],
        "results":results,
        "pairwise_overlap":pairwise_candidate_overlap(raw),
    }
    target=Path(args.output);target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(f"REPORT={target}")
    print(f"CANDIDATES={len(results)}")
    print("CANDIDATE_SELECTION_MUTATED=False")
    print("VERIFICATION_ACCESSED=False")
    print("SOL_CALLS=0")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
