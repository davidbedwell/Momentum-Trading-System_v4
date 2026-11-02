"""Independent saved-artifact accounting and blind-boundary checks."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
R=Path(__file__).resolve().parent
m=pd.read_csv(R/'metrics.csv');g=json.loads((R/'gates.json').read_text())
assert len(m)==20 and set(m.period)=={'discovery'}
assert not any(x['passed'] for x in g)
assert not list(R.glob('*/blind'))
counts=[]
for row in m.itertuples():
    p=R/row.basis/row.period/row.indicator
    monthly=pd.read_csv(p/'monthly.csv');daily=pd.read_csv(p/'daily_marks.csv');w=pd.read_csv(p/'holdings.csv');trials=pd.read_csv(p/'random_trials.csv')
    assert len(monthly)==120 and len(trials)==500
    assert (pd.to_datetime(monthly.signal_date)<pd.to_datetime(monthly.execution_date)).all()
    assert (pd.to_datetime(monthly.end_date)<pd.Timestamp('2019-01-01')).all()
    assert monthly.iloc[-1].terminal_close
    assert monthly.canceled_targets.sum()==0
    np.testing.assert_allclose(monthly.cost_fraction,.001*monthly.turnover,rtol=1e-10)
    np.testing.assert_allclose(w.groupby('execution_date').weight.sum(),1)
    nav=np.prod(1+monthly.strategy_return)
    np.testing.assert_allclose(nav,1+row.total_return)
    np.testing.assert_allclose(daily.strategy_nav.iloc[-1],nav)
    v=np.r_[1,daily.strategy_nav];dd=1-np.min(v/np.maximum.accumulate(v))
    np.testing.assert_allclose(dd,row.max_drawdown)
    counts.append(dict(basis=row.basis,indicator=row.indicator,min_eligible=int(monthly.eligible.min()),max_eligible=int(monthly.eligible.max()),min_k=int(monthly.k.min()),max_k=int(monthly.k.max()),nonfinite_signal_exclusions_sum=int(monthly.nonfinite_signal_excluded.sum()),months_with_nonfinite_exclusions=int((monthly.nonfinite_signal_excluded>0).sum())))
pd.DataFrame(counts).to_csv(R/'eligibility_summary.csv',index=False)
print('PASS: 20 discovery portfolios, 10,000 random paths, prior-close/month boundaries, no blind evaluation, costs, weights, terminal NAV and daily drawdowns independently reconciled.')
