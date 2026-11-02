"""2020 R-1 tape chronology and post-recovery GA6 entry opportunity counts."""
import csv,json
from collections import Counter
import pandas as pd
from engines.portfolio_replay.historical_defense import DEFAULT_TAPE
from discovery.competitive_ga.ga6_entry_execution_diagnostic import SIGNALS

def run():
    with open(DEFAULT_TAPE,newline="") as f:rows=list(csv.DictReader(f))
    rows=[r for r in rows if "2020-02-01"<=r["date"]<="2020-06-30"]
    changes=[]
    prev=None
    for r in rows:
        state=(r["defensive"],r["A_v2"],r["B"],r["B1"],r["C"],r["exit"])
        if r["entry"]=="True" or r["exit"]=="True" or r["defensive"]!=prev:
            changes.append({"date":r["date"],"defensive":r["defensive"],"entry":r["entry"],
                            "exit":r["exit"],"A":r["A_v2"],"B":r["B"],"B1":r["B1"],"C":r["C"]})
        prev=r["defensive"]
    signals=pd.read_csv(SIGNALS)
    post=signals[(signals.signal_date>="2020-05-28")&(signals.signal_date<="2020-12-31")]
    return {"transition_evidence":changes,"post_recovery_signal_rows":len(post),
            "post_recovery_unique_tickers":int(post.ticker.nunique()),
            "post_recovery_chromosomes":int(post.chromosome_id.nunique()),
            "monthly_signal_rows":{str(k):int(v) for k,v in post.groupby(post.signal_date.str.slice(0,7)).size().items()}}
if __name__=="__main__":print(json.dumps(run(),indent=2))
