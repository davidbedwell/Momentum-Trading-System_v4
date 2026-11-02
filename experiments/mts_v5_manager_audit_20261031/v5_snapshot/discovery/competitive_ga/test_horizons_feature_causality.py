"""Chronological prefix-invariance checks for Horizons reconstructed features."""
import unittest
import numpy as np
import pandas as pd
from .horizons_feature_reconstruction import raw_panel,STOCK_SOURCE
from .horizons_feature_normalization import normalize
from .horizons_native_score import FEATURES
class TestCausality(unittest.TestCase):
 def test_future_rows_do_not_change_past(self):
  dates=pd.bdate_range('2026-01-01',periods=85)
  rows=[]
  for i,date in enumerate(dates):
   for j,ticker in enumerate(('A','B','C')):
    row=dict(date=date,ticker=ticker,eligible=True)
    row.update({v:float(i+j+1)/100 for v in STOCK_SOURCE.values()})
    row['breadth_above_sma_200__v1']=.3+i/1000
    row['breadth_positive_20__v1']=.4+i/1000
    rows.append(row)
  frame=pd.DataFrame(rows)
  ext=pd.DataFrame({'date':dates,'vix':np.arange(85)+10.,'vvix':np.arange(85)+40.,'funding':np.arange(85)/100,'credit':np.arange(85)/200})
  full=normalize(raw_panel(frame,ext))
  cutoff=dates[70]
  prefix=normalize(raw_panel(frame.loc[frame.date<=cutoff],ext.loc[ext.date<=cutoff]))
  old=full.loc[full.date<=cutoff].reset_index(drop=True)
  self.assertEqual(len(old),len(prefix))
  np.testing.assert_allclose(old[list(FEATURES)].to_numpy(),prefix[list(FEATURES)].to_numpy(),rtol=0,atol=0,equal_nan=True)
if __name__=='__main__':unittest.main()
