import tempfile,pathlib
import numpy as np,pandas as pd
from scripts.thirteen_window_cash_rate_20261011 import session_cash_returns
with tempfile.TemporaryDirectory() as d:
 p=pathlib.Path(d)/'rf.csv'
 p.write_text('observation_date,DGS3MO\n2020-01-01,3\n2020-01-03,5\n')
 cal=pd.bdate_range('2020-01-02',periods=4)
 r=session_cash_returns(cal,p)
 assert len(r)==4 and np.isfinite(r).all()
 assert np.isclose(r[0],(1.03)**(1/252)-1)
 assert np.isclose(r[1],(1.03)**(1/252)-1)
 assert np.isclose(r[2],(1.05)**(1/252)-1)
print('CASH_RATE_NO_LOOKAHEAD_TEST_PASS')
