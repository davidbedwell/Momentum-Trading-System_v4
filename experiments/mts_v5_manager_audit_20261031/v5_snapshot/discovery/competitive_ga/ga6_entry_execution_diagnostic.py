"""2020 GA6 authentic entry-signal execution diagnostic.

Signals originate from frozen GA6 chromosomes, not synthetic momentum.
Ten-session exits are an explicitly imposed diagnostic liquidation policy,
NOT native GA6 exits. No GA7 signals or learning in this experiment.
"""
import json
from pathlib import Path
import pandas as pd
import numpy as np
from engines.portfolio_replay.kernel import Replay,Bar,Signal
from engines.portfolio_replay.historical_defense import HistoricalDefense

SIGNALS=Path('/opt/mts/ga6/runs/selector_learning_fourfold_20261025/signal_smoke_2020_DEV79_NO_OUTCOMES.csv')
PRICES=Path('/opt/mts/ga5_redesign/exploratory79_ga4_enriched.parquet')
OUT=Path('/opt/mts/synthetic-market-lab/reports/ga6_2020_entry_execution_diagnostic.json')

def run():
    s=pd.read_csv(SIGNALS)
    if s.empty:raise ValueError('no native signals')
    if not s.entry_earliest_next_session.all():raise ValueError('invalid signal chronology')
    p=pd.read_parquet(PRICES,columns=['date','ticker','open','close','dividends'])
    p=p[(p.date>='2020-01-01')&(p.date<='2020-12-31')].copy()
    p['date']=pd.to_datetime(p.date).dt.strftime('%Y-%m-%d')
    dates=sorted(p.date.unique())
    signal_map={d:g for d,g in s.groupby('signal_date')}
    replay=Replay()
    defense=HistoricalDefense()
    entry_session={}
    for i,day in enumerate(dates):
        bars={r.ticker:Bar(float(r.open),float(r.close),float(r.dividends))
              for r in p[p.date==day].itertuples() if r.open>0 and r.close>0}
        active=defense.state(day)
        signals=[]
        if not active:
            # Explicit 10-session liquidation diagnostic, not GA6 exit grammar.
            for t in replay.shares:
                if i-entry_session.get(t,i)>=10:
                    signals.append(Signal(t,'GA6','DIAGNOSTIC_EXIT',0.))
            if day in signal_map:
                for row in signal_map[day].itertuples():
                    if row.ticker not in bars or row.ticker in replay.shares:continue
                    if any(x.ticker==row.ticker for x in signals):continue
                    signals.append(Signal(row.ticker,'GA6',row.chromosome_id,
                                          min(.10,float(row.target_weight))))
                    entry_session.setdefault(row.ticker,i+1)
        replay.day(day,bars,signals,defense=active)
        for t in list(entry_session):
            if t not in replay.shares and not any(x.ticker==t and x.target_weight>0 for x in replay.pending):
                del entry_session[t]
    nav=np.array([v[1] for v in replay.nav])
    dd=1-nav/np.maximum.accumulate(nav)
    result={'label':'GA6 native entry signal 2020 research diagnostic with artificial 10-session exit',
            'sessions':len(dates),'native_signal_rows':len(s),
            'unique_chromosomes':int(s.chromosome_id.nunique()),
            'fills':len(replay.ledger),'ending_nav':round(float(nav[-1]),2),
            'net_return':round(float(nav[-1]/nav[0]-1),6),
            'max_drawdown':round(float(dd.max()),6),
            'limitations':'Entry-only GA6 signal smoke, 3 preselected chromosomes, artificial 10-session exits, no GA7, no authentic selector, no calibrated chromosome scores, no earnings gate, no independent PIT certification; NOT performance evidence for deployment.'}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2))
    return result
if __name__=='__main__':print(json.dumps(run(),indent=2))
