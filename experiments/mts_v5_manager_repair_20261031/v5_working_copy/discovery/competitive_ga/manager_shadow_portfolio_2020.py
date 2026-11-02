"""Research-only 2020 manager portfolio using chronological native GA6 shadow
calibration. Shadow outcomes are replay-derived and not PIT-certified.
"""
import json
import numpy as np
import pandas as pd
from engines.portfolio_replay.kernel import Replay,Bar,Signal
from engines.portfolio_replay.historical_defense import HistoricalDefense
from discovery.competitive_ga.ga6_entry_execution_diagnostic import SIGNALS,PRICES
from discovery.competitive_ga.ga6_native_position_replay import run as native_run
from discovery.competitive_ga.chronological_shadow_feed import ShadowFeed
from discovery.competitive_ga.native_manager_bridge import orders_from_native
from discovery.competitive_ga.manager_policy_v2 import Genes

def run():
    _,attributed=native_run(output="ATTRIBUTED")
    feed=ShadowFeed(attributed)
    signals=pd.read_csv(SIGNALS)
    frame=pd.read_parquet(PRICES,columns=["date","ticker","open","close","dividends"])
    frame=frame[(frame.date>="2020-01-01")&(frame.date<="2020-12-31")].copy()
    frame["date"]=pd.to_datetime(frame.date).dt.strftime("%Y-%m-%d")
    byday={d:g for d,g in frame.groupby("date")}
    bysignal={d:g for d,g in signals.groupby("signal_date")}
    replay=Replay()
    defense=HistoricalDefense()
    orders=0
    calibrated_rows=0
    first_order=None
    for i,day in enumerate(sorted(byday)):
        bars={r.ticker:Bar(float(r.open),float(r.close),float(r.dividends))
              for r in byday[day].itertuples() if r.open>0 and r.close>0}
        active=defense.state(day)
        replay.day(day,bars,(),defense=active)
        feed.advance(i)
        nav=replay.nav[-1][1]
        holdings={t:q*bars[t].close/nav for t,q in replay.shares.items() if t in bars}
        rows=[]
        if i>=21 and day in bysignal:
            for r in bysignal[day].itertuples():
                if r.ticker not in bars:continue
                cal=feed.estimate(r.chromosome_id,i)
                if cal:calibrated_rows+=1
                rows.append((r.ticker,r.chromosome_id,"GA6","ENTER",float(r.target_weight),cal))
        decisions=orders_from_native(rows,holdings,replay.cash/nav,Genes(),active)
        replay.pending=[Signal(t,"MANAGER",origin,weight) for t,(action,weight,origin) in decisions.items()]
        if decisions and first_order is None:first_order=day
        orders+=len(decisions)
    navs=np.array([v[1] for v in replay.nav])
    return {"sessions":len(navs),"native_shadow_fills":len(attributed),
            "shadow_realized_outcomes":len(feed.calibrator.outcomes),
            "calibrated_signal_rows":calibrated_rows,
            "manager_orders":orders,"portfolio_fills":len(replay.ledger),
            "first_order_date":first_order,"ending_nav":round(float(navs[-1]),2),
            "net_return":round(float(navs[-1]/navs[0]-1),6),
            "max_drawdown":round(float(np.max(1-navs/np.maximum.accumulate(navs))),6),
            "limitations":"Entry-only GA6 manager proposals; 3 preselected chromosomes; no held-position native exits, no GA7, no PIT certification, no earnings gate, no settled-ledger parity. Not deployable."}
if __name__=="__main__":print(json.dumps(run(),indent=2))
