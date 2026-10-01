#!/usr/bin/env python3
import argparse, json, statistics
from pathlib import Path

RULE = {
    "rule_id": "MTS_V4_CROSS_TICKER_RETENTION_V1",
    "minimum_executable_trades": 10,
    "require_fixed_horizon_mean_gt": 0.0,
    "require_fixed_horizon_median_gt": 0.0,
    "purpose": "FALSIFICATION_RETENTION_ONLY_NOT_VALIDATION_NOT_PROMOTION",
}
FAMILIES = (
    "BREAKOUT","MARKET_REGIME_STRUCTURE","MEAN_REVERSION","MOMENTUM",
    "RELATIVE_CROSS_SECTIONAL","TREND","VOLATILITY","VOLUME_LIQUIDITY",
)

def stats(paths):
    r=[float(x["fixed_horizon_return"]) for x in paths if x.get("fixed_horizon_return") is not None]
    return {
        "count": len(r),
        "mean": statistics.fmean(r) if r else None,
        "median": statistics.median(r) if r else None,
        "positive_fraction": (sum(x > 0 for x in r)/len(r)) if r else None,
    }

def disposition(s):
    if s["count"] < RULE["minimum_executable_trades"]:
        return "SPARSE_RECORDED_NOT_RETAINED"
    if s["mean"] <= 0 or s["median"] <= 0:
        return "NONPOSITIVE_RECORDED_NOT_RETAINED"
    return "RETAIN_FOR_FALSIFICATION"

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--report", action="append", required=True, help="TICKER=trade_path_report.json")
    ap.add_argument("--replacement", action="append", default=[], help="TICKER:FAMILY=corrected_trade_path_report.json")
    ap.add_argument("--output", required=True)
    a=ap.parse_args()

    reports={}
    for item in a.report:
        ticker,path=item.split("=",1); reports[ticker]=Path(path)
    replacements={}
    for item in a.replacement:
        key,path=item.split("=",1); ticker,family=key.split(":",1)
        replacements[(ticker,family)]=Path(path)

    rows=[]
    for ticker,path in reports.items():
        d=json.loads(path.read_text())
        if d.get("scientific_boundary") != "DISCOVERY_POST_SEARCH_ANALYSIS_ONLY_NOT_VALIDATION_NOT_PROMOTION":
            raise SystemExit(f"{ticker}: unexpected scientific boundary {d.get('scientific_boundary')!r}")
        for family in FAMILIES:
            source=d
            source_path=path
            if (ticker,family) in replacements:
                source_path=replacements[(ticker,family)]
                source=json.loads(source_path.read_text())
            optimizers=source.get("results",{}).get(family,{})
            seen={}
            for optimizer,candidates in optimizers.items():
                if not candidates:
                    continue
                c=candidates[0]
                cid=c.get("candidate_id")
                key=cid or json.dumps(c.get("genome",{}),sort_keys=True)
                if key in seen:
                    seen[key]["optimizers"].append(optimizer)
                    continue
                s=stats(c.get("paths",[]))
                row={
                    "ticker":ticker,"family":family,"optimizers":[optimizer],
                    "candidate_id":cid,"genome":c.get("genome"),
                    "source_report":str(source_path),"statistics":s,
                    "disposition":disposition(s),
                }
                seen[key]=row
                rows.append(row)

    retained=[r for r in rows if r["disposition"]=="RETAIN_FOR_FALSIFICATION"]
    out={
        "format":"MTS_V4_CROSS_TICKER_RETENTION_MANIFEST_V1",
        "scientific_boundary":"DISCOVERY_SELECTION_FOR_FALSIFICATION_ONLY_NOT_VALIDATION_NOT_PROMOTION",
        "retention_rule":RULE,
        "candidate_selection_mutated":False,
        "verification_accessed":False,
        "sol_calls":0,
        "all_top_candidates":rows,
        "retained_candidates":retained,
    }
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(f"REPORT={a.output}")
    print(f"TICKERS={len(reports)}")
    print(f"TOP_CANDIDATES_UNIQUE={len(rows)}")
    print(f"RETAINED_FOR_FALSIFICATION={len(retained)}")
    for ticker in reports:
        n=sum(r["ticker"]==ticker and r["disposition"]=="RETAIN_FOR_FALSIFICATION" for r in rows)
        print(f"{ticker}_RETAINED={n}")
    print("CANDIDATE_SELECTION_MUTATED=False")
    print("VERIFICATION_ACCESSED=False")
    print("SOL_CALLS=0")

if __name__=="__main__":
    main()
