"""Inspect frozen defense/R-1 transitions in 2020; no strategy changes."""
import json
from collections import Counter
from engines.portfolio_replay.historical_defense import HistoricalDefense
from discovery.competitive_ga.ga6_entry_execution_diagnostic import PRICES
import pandas as pd

def run():
    p=pd.read_parquet(PRICES,columns=["date"])
    days=sorted(pd.to_datetime(p[(p.date>="2020-01-01")&(p.date<="2020-12-31")].date).dt.strftime("%Y-%m-%d").unique())
    d=HistoricalDefense()
    changes=[]
    prev=None
    count=Counter()
    for i,day in enumerate(days):
        state=d.state(day)
        count["defense" if state else "normal"]+=1
        if prev is None or state!=prev:
            changes.append({"session":i,"date":day,"state":"DEFENSE" if state else "NORMAL"})
        prev=state
    return {"sessions":len(days),"state_counts":dict(count),"transitions":changes}
if __name__=="__main__":print(json.dumps(run(),indent=2))
