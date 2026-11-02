"""Quantify why chronologically calibrated native GA6 signals fail manager gates."""
import json
from collections import Counter
import pandas as pd
from discovery.competitive_ga.ga6_native_position_replay import run
from discovery.competitive_ga.chronological_shadow_feed import ShadowFeed
from discovery.competitive_ga.ga6_entry_execution_diagnostic import SIGNALS,PRICES
from discovery.competitive_ga.manager_policy_v2 import Genes

def audit():
    _,fills=run(output="ATTRIBUTED")
    feed=ShadowFeed(fills)
    signals=pd.read_csv(SIGNALS)
    prices=pd.read_parquet(PRICES,columns=["date"])
    dates=sorted(pd.to_datetime(prices[(prices.date>="2020-01-01")&(prices.date<="2020-12-31")].date).dt.strftime("%Y-%m-%d").unique())
    byday={d:g for d,g in signals.groupby("signal_date")}
    genes=Genes()
    counts=Counter()
    stats=[]
    first_eligible=None
    owners=Counter()
    for i,day in enumerate(dates):
        feed.advance(i)
        if i<21 or day not in byday:continue
        for row in byday[day].itertuples():
            cal=feed.estimate(row.chromosome_id,i)
            if cal is None:
                counts["uncalibrated"]+=1
                continue
            counts["calibrated"]+=1
            owners[row.chromosome_id]+=1
            score=cal["edge"]-genes.risk_penalty*max(0,cal["downside"])
            stats.append((cal["edge"],cal["downside"],score,cal["matured_samples"]))
            if score>=genes.min_edge:
                counts["passed_score"]+=1
                if first_eligible is None:first_eligible=day
            else:
                counts["rejected_score"]+=1
                if cal["edge"]<genes.min_edge:counts["raw_edge_below_gate"]+=1
                if cal["edge"]>=genes.min_edge:counts["downside_penalty_rejection"]+=1
    df=pd.DataFrame(stats,columns=["edge","downside","score","samples"])
    return {"counts":dict(counts),"threshold":genes.min_edge,"first_score_pass":first_eligible,
            "calibrated_chromosomes":len(owners),
            "quantiles":{k:{str(q):round(float(df[k].quantile(q)),6) for q in [0,.1,.5,.9,1]}
                         for k in ["edge","downside","score","samples"]} if len(df) else {},
            "status":"DIAGNOSTIC_NOT_PERFORMANCE_CERTIFICATION"}
if __name__=="__main__":print(json.dumps(audit(),indent=2))
