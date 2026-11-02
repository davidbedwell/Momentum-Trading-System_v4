"""End-to-end research replay of manager V3 orders using genuine GA6 entry
signals, existing next-open Replay kernel, and explicitly uncalibrated mode.
NO performance certification: calibration is unavailable, so no entries.
"""
import json
from pathlib import Path
import pandas as pd
from engines.portfolio_replay.kernel import Replay,Bar,Signal
from engines.portfolio_replay.historical_defense import HistoricalDefense
from discovery.competitive_ga.ga6_entry_execution_diagnostic import SIGNALS,PRICES
from discovery.competitive_ga.native_manager_bridge import orders_from_native
from discovery.competitive_ga.manager_policy_v2 import Genes

def run():
    signals=pd.read_csv(SIGNALS)
    prices=pd.read_parquet(PRICES,columns=["date","ticker","open","close","dividends"])
    prices=prices[(prices.date>="2020-01-01")&(prices.date<="2020-12-31")].copy()
    prices["date"]=pd.to_datetime(prices.date).dt.strftime("%Y-%m-%d")
    by_date={d:g for d,g in prices.groupby("date")}
    by_signal={d:g for d,g in signals.groupby("signal_date")}
    replay=Replay()
    defense=HistoricalDefense()
    observed=0
    rejected=0
    for day in sorted(by_date):
        bars={r.ticker:Bar(float(r.open),float(r.close),float(r.dividends))
              for r in by_date[day].itertuples() if r.open>0 and r.close>0}
        active=defense.state(day)
        replay.day(day,bars,(),defense=active)
        nav=replay.nav[-1][1]
        holdings={t:replay.shares[t]*bars[t].close/nav for t in replay.shares if t in bars}
        cash=replay.cash/nav
        rows=[]
        if day in by_signal:
            for r in by_signal[day].itertuples():
                if r.ticker not in bars:continue
                observed+=1
                rows.append((r.ticker,r.chromosome_id,"GA6","ENTER",
                             float(r.target_weight),None))
        decisions=orders_from_native(rows,holdings,cash,Genes(),active)
        rejected+=len(rows) if not decisions else 0
        replay.pending=[Signal(t,"MANAGER",origin,weight) for t,(act,weight,origin) in decisions.items()]
    result={"sessions":len(replay.nav),"native_signal_rows_considered":observed,
            "uncalibrated_rows_without_orders":rejected,
            "fills":len(replay.ledger),"ending_nav":replay.nav[-1][1],
            "status":"FAIL_CLOSED_INTEGRATION_TEST",
            "note":"No matured calibration provided; manager correctly makes no purchases. This is not a strategy backtest."}
    return result

if __name__=="__main__":print(json.dumps(run(),indent=2))
