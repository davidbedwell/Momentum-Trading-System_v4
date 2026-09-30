#!/usr/bin/env python3
import argparse, json
from collections import Counter, defaultdict
from pathlib import Path

def canon(g):
    return json.dumps(g or {}, sort_keys=True, separators=(",",":"))

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",required=True)
    p.add_argument("--falsification-dir",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()

    m=json.loads(Path(a.manifest).read_text())
    retained=m["retained_candidates"]
    by_cid={r["candidate_id"]:r for r in retained}
    diagnostics=[]
    for fp in sorted(Path(a.falsification_dir).glob("*_FROZEN_CANDIDATE_FALSIFICATION_20260930.json")):
        d=json.loads(fp.read_text())
        for name,r in d["results"].items():
            src=next(x for x in d["sources"] if x["name"]==name)
            base=by_cid[src["candidate_id"]]
            thirds=r["chronological_thirds"]
            third_means=[x["statistics"]["mean"] for x in thirds if x["statistics"]["count"]]
            third_medians=[x["statistics"]["median"] for x in thirds if x["statistics"]["count"]]
            loo=r["leave_one_out"]
            diagnostics.append({
                "ticker":base["ticker"],"family":base["family"],"candidate_id":src["candidate_id"],
                "genome":base["genome"],"genome_key":canon(base["genome"]),
                "optimizers":base["optimizers"],"trade_count":r["trade_count"],
                "mean":r["fixed_horizon_statistics"]["mean"],
                "median":r["fixed_horizon_statistics"]["median"],
                "positive_fraction":r["fixed_horizon_statistics"]["positive_fraction"],
                "trimmed_mean":r["trimmed_mean"],
                "top1_share":r["winner_concentration"]["top_1_share_of_positive_returns"],
                "top3_share":r["winner_concentration"]["top_3_share_of_positive_returns"],
                "loo_mean_min":loo.get("mean_min") if loo.get("available") else None,
                "chronological_third_means":third_means,
                "chronological_third_medians":third_medians,
                "all_thirds_mean_positive":bool(third_means) and all(x is not None and x>0 for x in third_means),
                "all_thirds_median_positive":bool(third_medians) and all(x is not None and x>0 for x in third_medians),
            })

    family=defaultdict(list)
    exact=defaultdict(list)
    shape=defaultdict(list)
    for r in diagnostics:
        family[r["family"]].append(r)
        exact[(r["family"],r["genome_key"])].append(r)
        # Conceptual shape: same family + same genome fields and categorical values;
        # numeric thresholds are deliberately not declared equivalent.
        g=r["genome"] or {}
        sig=tuple(sorted((k,v) for k,v in g.items() if not isinstance(v,(int,float))))
        shape[(r["family"],sig)].append(r)

    fam_rows=[]
    for fam,rows in sorted(family.items()):
        fam_rows.append({
            "family":fam,
            "ticker_count":len({r["ticker"] for r in rows}),
            "candidate_count":len(rows),
            "all_thirds_mean_positive_count":sum(r["all_thirds_mean_positive"] for r in rows),
            "all_thirds_median_positive_count":sum(r["all_thirds_median_positive"] for r in rows),
            "loo_mean_positive_count":sum((r["loo_mean_min"] or 0)>0 for r in rows),
            "median_trade_count":sorted(r["trade_count"] for r in rows)[len(rows)//2],
        })

    exact_rows=[]
    for (fam,gk),rows in exact.items():
        tickers=sorted({r["ticker"] for r in rows})
        if len(tickers)>=2:
            exact_rows.append({"family":fam,"tickers":tickers,"ticker_count":len(tickers),"genome":rows[0]["genome"]})
    exact_rows.sort(key=lambda x:(-x["ticker_count"],x["family"],x["tickers"]))

    shape_rows=[]
    for (fam,sig),rows in shape.items():
        tickers=sorted({r["ticker"] for r in rows})
        if len(tickers)>=2:
            shape_rows.append({"family":fam,"tickers":tickers,"ticker_count":len(tickers),
                               "shared_categorical_structure":dict(sig),"candidate_count":len(rows)})
    shape_rows.sort(key=lambda x:(-x["ticker_count"],x["family"],x["tickers"]))

    out={
        "format":"MTS_V4_CROSS_TICKER_RECURRENCE_V1",
        "scientific_boundary":"DISCOVERY_RECURRENCE_DESCRIPTION_ONLY_NOT_VALIDATION_NOT_PROMOTION",
        "source_manifest":a.manifest,
        "candidate_count":len(diagnostics),
        "ticker_count":len({r["ticker"] for r in diagnostics}),
        "family_recurrence":fam_rows,
        "exact_genome_recurrence":exact_rows,
        "conceptual_structure_recurrence":shape_rows,
        "candidate_diagnostics":diagnostics,
        "important_limitations":[
            "Family recurrence is not independent replication because each ticker was searched independently within the same predefined family library.",
            "Exact genome recurrence is descriptive Discovery evidence only and is not untouched validation.",
            "Conceptual structure recurrence preserves categorical genome structure only; numeric threshold differences are not treated as equivalent.",
            "No Verification A or B observations are accessed.",
            "No transaction-cost assumption is introduced here."
        ],
        "candidate_selection_mutated":False,"verification_accessed":False,"sol_calls":0,
    }
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(f"REPORT={a.output}")
    print(f"TICKERS={out['ticker_count']}")
    print(f"CANDIDATES={out['candidate_count']}")
    print("FAMILY_RECURRENCE="+";".join(f"{x['family']}:{x['ticker_count']}" for x in fam_rows))
    print(f"EXACT_GENOME_RECURRENCES_GE2={len(exact_rows)}")
    print(f"CONCEPTUAL_STRUCTURE_RECURRENCES_GE2={len(shape_rows)}")
    print("CANDIDATE_SELECTION_MUTATED=False")
    print("VERIFICATION_ACCESSED=False")
    print("SOL_CALLS=0")

if __name__=="__main__":
    main()
