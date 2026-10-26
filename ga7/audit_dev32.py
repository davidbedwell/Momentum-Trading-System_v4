"""DEV32 selection audit: historical eligibility, financial evidence, and bias flags."""
import argparse
import json
from pathlib import Path
import pandas as pd

def audit(frame, selection, *, cutoff="2005-09-14"):
    frame=frame.copy()
    frame["date"]=pd.to_datetime(frame["date"])
    selected=[r["ticker"] for r in selection["tickers"]]
    eligible=set(frame.loc[frame.date <= pd.Timestamp(cutoff),"ticker"])
    failures=[]
    if len(selected)!=32 or len(set(selected))!=32:
        failures.append("Selection must contain 32 distinct securities")
    if set(selected)-eligible:
        failures.append("Selected securities unavailable at cutoff")
    sectors=frame.groupby("ticker").sector_name.agg(lambda x:x.mode().iloc[0])
    if len(set(sectors.loc[selected]))!=len(set(sectors)):
        failures.append("Missing sector")
    if frame.duplicated(["ticker","date"]).any():
        failures.append("Duplicate ticker/date observations")
    if any(r.get("financial_solvency")!="PIT_VERIFIED" for r in selection["tickers"]):
        failures.append("No audited PIT financial solvency evidence")
    if "PROVISIONAL" in selection.get("status",""):
        failures.append("Selector output is provisional")
    if len(set(frame.ticker))!=79:
        failures.append("Expected DEV79 source")
    per_sector=sectors.value_counts().sort_index()
    chosen=sectors.loc[selected].value_counts().reindex(per_sector.index,fill_value=0)
    gap=(chosen/32-per_sector/79).abs()
    return {"pass_for_evolution":not failures,"blocking_findings":failures,
        "sector_total_variation_distance":float(gap.sum()/2),
        "sector_max_weight_gap":float(gap.max()),
        "eligible_at_cutoff":len(eligible),
        "selected_count":len(selected),
        "selected_with_coverage_at_cutoff":len(set(selected)&eligible),
        "source_survivorship_certified":False,
        "financial_solvency_certified":False}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--data",required=True)
    ap.add_argument("--selection",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    frame=pd.read_parquet(args.data,columns=["ticker","date","sector_name"])
    selection=json.loads(Path(args.selection).read_text())
    report=audit(frame,selection)
    Path(args.out).write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps(report,indent=2,sort_keys=True))
if __name__=="__main__":
    main()
