"""Chronological GA6 manager replay with incremental fill learning.
Fail-closed until independent matured outcomes exist. No fabricated bootstrap.
"""
import json
import pandas as pd
from engines.portfolio_replay.kernel import Replay,Bar,Signal
from engines.portfolio_replay.historical_defense import HistoricalDefense
from discovery.competitive_ga.ga6_entry_execution_diagnostic import SIGNALS,PRICES
from discovery.competitive_ga.native_manager_bridge import orders_from_native
from discovery.competitive_ga.manager_policy_v2 import Genes
from discovery.competitive_ga.replay_learning_adapter import ReplayLearningAdapter

def run():
    signals=pd.read_csv(SIGNALS)
    prices=pd.read_parquet(PRICES,columns=["date","ticker","open","close","dividends"])
    prices=prices[(prices.date>="2020-01-01")&(prices.date<="2020-12-31")].copy()
    prices["date"]=pd.to_datetime(prices.date).dt.strftime("%Y-%m-%d")
    by_date={d:g for d,g in prices.groupby("date")}
    by_signal={d:g for d,g in signals.groupby("signal_date")}
    replay=Replay()
    defense=HistoricalDefense()
    learning=ReplayLearningAdapter(min_samples=5)
    pending_owners={}
    observations=0
    orders=0
    for session,day in enumerate(sorted(by_date)):
        bars={r.ticker:Bar(float(r.open),float(r.close),float(r.dividends))
              for r in by_date[day].itertuples() if r.open>0 and r.close>0}
        active=defense.state(day)
        replay.day(day,bars,(),defense=active)
        # Only fills from previously queued orders can be ingested here.
        learning.consume(replay.ledger,session,pending_owners)
        pending_owners={}
        nav=replay.nav[-1][1]
        holdings={t:q*bars[t].close/nav for t,q in replay.shares.items() if t in bars}
        rows=[]
        for r in by_signal.get(day,()).itertuples() if day in by_signal else ():
            if r.ticker not in bars:continue
            observations+=1
            context=("GA6_ENTRY",)
            calibration=learning.calibrator.estimate(r.chromosome_id,context,session)
            rows.append((r.ticker,r.chromosome_id,"GA6","ENTER",
                         float(r.target_weight),calibration))
        decisions=orders_from_native(rows,holdings,replay.cash/nav,Genes(),active)
        for ticker,(action,weight,origin) in decisions.items():
            if action in ("ENTER","INCREASE"):
                pending_owners[ticker]=(origin,("GA6_ENTRY",))
        replay.pending=[Signal(t,"MANAGER",origin,weight) for t,(action,weight,origin) in decisions.items()]
        orders+=len(decisions)
    return {"sessions":len(replay.nav),"signals":observations,"orders":orders,
            "fills":len(replay.ledger),"matured_observations":len(learning.calibrator.outcomes),
            "ending_nav":round(replay.nav[-1][1],2),
            "status":"CAUSAL_REPLAY_WIRED_NO_BOOTSTRAP",
            "limitation":"No independent matured trade history to bootstrap calibration; zero trades expected. Not deployable."}

if __name__=="__main__":print(json.dumps(run(),indent=2))
