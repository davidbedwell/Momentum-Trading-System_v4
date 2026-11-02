"""Historical SPY-only defense benchmark. Not GA6/GA7 performance."""
import json
from pathlib import Path
import pandas as pd
import numpy as np
from engines.portfolio_replay.kernel import Bar,Signal,Replay
from engines.portfolio_replay.historical_defense import HistoricalDefense

SPY=Path('/opt/mts/ga6-git-backup/Research/Data/Comparators/SPY_YFINANCE_2005_2026.parquet')
def evaluate():
    df=pd.read_parquet(SPY).sort_values('date')
    df=df[(df.date>='2005-09-14')&(df.date<='2026-09-14')]
    cases={}
    for label,defended in [('buy_hold',False),('frozen_defense',True)]:
        replay=Replay(fees=.001,cap=1.)
        defense=HistoricalDefense()
        was_active=False
        first=True
        for row in df.itertuples():
            day=str(row.date.date())
            active=defense.state(day) if defended else False
            # Buy and hold from first actionable session; defense reentry uses
            # existing research kernel and thus buys at the following open.
            signal=[Signal('SPY','BENCHMARK','SPY',1.)] if (first or was_active) and not active else []
            first=False
            was_active=active
            replay.day(day,{'SPY':Bar(float(row.open),float(row.close),float(row.dividends))},signal,defense=active)
        nav=np.array([x[1] for x in replay.nav])
        dd=1-nav/np.maximum.accumulate(nav)
        years=(df.date.iloc[-1]-df.date.iloc[0]).days/365.25
        cases[label]={'ending_nav':round(float(nav[-1]),2),'cagr':round(float((nav[-1]/nav[0])**(1/years)-1),6),
                      'max_drawdown':round(float(dd.max()),6),'fills':len(replay.ledger),
                      'sessions':len(nav)}
    return {'study':'SPY buy-and-hold vs frozen historical A_v2/B/B1/C/R1 defense',
            'source':str(SPY),'date_start':str(df.date.iloc[0].date()),
            'date_end':str(df.date.iloc[-1].date()),'results':cases,
            'limitations':'SPY only; not GA6/GA7; historical detector tape not independently PIT-certified; no SGOV yield; research execution only.'}
if __name__=='__main__':
    result=evaluate()
    out=Path('/opt/mts/synthetic-market-lab/reports/historical_spy_defense_benchmark.json')
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
