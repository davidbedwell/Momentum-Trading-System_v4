"""Chronological synthetic replay smoke; NOT GA6/GA7 signal parity or learning."""
import json,sys
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path("/opt/Momentum-Trading-System_v5-alpha")
sys.path.insert(0,str(ROOT))
from engines.portfolio_replay.kernel import Bar,Signal,Replay
from discovery.competitive_ga.synthetic_adapter import load_fsynth

def run(market,lookback=20,top=5,fee=.001):
    df=load_fsynth(market)
    dates=sorted(df.Date.unique())
    stocks=sorted(df.Ticker.unique())
    opens=df.pivot(index="Date",columns="Ticker",values="Open").reindex(index=dates,columns=stocks)
    closes=df.pivot(index="Date",columns="Ticker",values="Close").reindex(index=dates,columns=stocks)
    if opens.isna().any().any() or closes.isna().any().any():raise ValueError("incomplete panel")
    o=opens.to_numpy();c=closes.to_numpy()
    replay=Replay(fees=fee)
    for t,day in enumerate(dates):
        bars={stock:Bar(float(o[t,j]),float(c[t,j])) for j,stock in enumerate(stocks)}
        signals=[]
        if t>=lookback:
            # Uses only today's close and earlier close, never t+1.
            momentum=c[t]/c[t-lookback]-1
            picks=np.argsort(-momentum,kind="stable")[:top]
            signals=[Signal(stocks[j],"CAUSAL_BASELINE","20d_momentum",.1,float(momentum[j])) for j in picks if momentum[j]>0]
            # Explicit zero-weight signals exit holdings not retained in current top selection.
            selected={s.ticker for s in signals}
            signals.extend(Signal(ticker,"CAUSAL_BASELINE","exit",0,-1) for ticker in replay.shares if ticker not in selected)
        replay.day(str(pd.Timestamp(day).date()),bars,signals)
    nav=np.array([x[1] for x in replay.nav])
    peak=np.maximum.accumulate(nav)
    return {"market":str(market),"label":"non-GA causal momentum baseline smoke","sessions":len(dates),"stocks":len(stocks),
            "ending_nav":round(float(nav[-1]),2),"net_return":round(float(nav[-1]/nav[0]-1),6),
            "max_drawdown":round(float(np.max(1-nav/peak)),6),"fills":len(replay.ledger),
            "certified":False,"limitations":"No native GA6/GA7 signals, no authoritative defense, no mature counterfactual learner, no production accounting parity."}

if __name__=="__main__":
    path=Path(sys.argv[1]);result=run(path)
    print(json.dumps(result,sort_keys=True))
