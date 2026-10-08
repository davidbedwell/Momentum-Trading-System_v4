"""Freeze and audit the existing exposed DEV50 as a GA4 validation bank.

This does not pretend DEV50 is pristine, or that a GA4 candidate's genome
can be reconstructed from an ID-only evolutionary ledger. It reads membership
from the 50 reconstructed search reports; no protected A/B or BLIND17 reads.
"""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
REPORTS=Path("/home/ubuntu/mts-v4-preserved50-search-reconstructed-20261005")
CAL=ROOT/"Research/Runs/layered/stage2-opportunity-v3-20261007/calibration"
SOURCE=Path("/home/ubuntu/mts-v4-market-store-RECONSTRUCTED-20261004/raw_yfinance")
def digest(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1048576),b""):h.update(chunk)
    return h.hexdigest()
def main():
    paths=sorted(REPORTS.glob("*_COMPUTATIONAL_SEARCH_RECONSTRUCTED_20261005.json"))
    members=[]
    for p in paths:
        v=json.loads(p.read_text())
        t=v["ticker"];raw=SOURCE/(t+".parquet")
        members.append({"ticker":t,"security_id":v["security_id"],
                        "source_report_sha256":digest(p),
                        "raw_ohlcv_sha256":digest(raw) if raw.exists() else None})
    train=Path("/home/ubuntu/mts-ga-dev117-permitted-20261006")
    training={p.stem for p in train.glob("*.parquet")}
    overlap=sorted({m["ticker"] for m in members}&training)
    ledger_paths=[CAL/"nsga2_batch_evolutionary_evidence.json",CAL/"ga4_short_evolutionary_evidence.json"]
    ledgers=[{"name":p.name,"sha256":digest(p) if p.is_file() else None} for p in ledger_paths]
    failures=[]
    if len(members)!=50 or len({m["ticker"] for m in members})!=50:
        failures.append("preserved DEV50 membership is not exactly 50 unique tickers")
    if overlap:failures.append("DEV50 overlaps existing GA4 DEV117 evaluator: "+",".join(overlap))
    if any(m["raw_ohlcv_sha256"] is None for m in members):
        failures.append("missing historical OHLCV for one or more DEV50 stocks")
    if any(x["sha256"] is None for x in ledgers):
        failures.append("missing frozen GA4 search evidence ledger")
    result={"status":"ELIGIBLE_FOR_EXPOSED_BANK_VALIDATION" if not failures else "BLOCKED",
            "classification":"PREVIOUSLY_EXPOSED_DEV50_NOT_PRISTINE",
            "limitations":["Prior DEV50 defensive research prevents claims of pristine validation",
                           "GA4 evolutionary ledger stores candidate IDs but not reproducible genome definitions; selected genomes must be recovered or deterministically replayed before scoring",
                           "Historical cross-sectional features require isolated-bank reconstruction"],
            "members":members,"count":len(members),"training_dev117_count":len(training),
            "training_overlap":overlap,"frozen_ga4_ledgers":ledgers,"failures":failures}
    CAL.mkdir(parents=True,exist_ok=True)
    target=CAL/"ga4_exposed_dev50_eligibility.json"
    target.write_text(json.dumps(result,indent=2))
    print(json.dumps({"status":result["status"],"count":len(members),
                      "training_overlap":len(overlap),"failures":failures,
                      "manifest":str(target)}))
if __name__=="__main__":main()
