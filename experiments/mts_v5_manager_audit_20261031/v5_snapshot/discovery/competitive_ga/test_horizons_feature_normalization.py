import unittest
import pandas as pd
from .horizons_native_score import STOCK,MARKET
from .horizons_feature_normalization import normalize
class TestNormalization(unittest.TestCase):
 def test_rank_and_prior_only(self):
  rows=[]
  for day in range(62):
   for ticker,v in [('A',.1),('B',.9)]:
    row=dict(date=pd.Timestamp('2026-01-01')+pd.Timedelta(days=day),ticker=ticker)
    row.update({k:v for k in STOCK});row.update({k:float(day) for k in MARKET});rows.append(row)
  result=normalize(pd.DataFrame(rows))
  self.assertEqual(result.loc[(result.date==pd.Timestamp('2026-01-01'))&(result.ticker=='A'),'ret5'].iloc[0],0.)
  self.assertEqual(result.loc[(result.date==pd.Timestamp('2026-01-01'))&(result.ticker=='B'),'ret5'].iloc[0],1.)
  self.assertEqual(result.loc[result.date==pd.Timestamp('2026-01-01'),'mret5'].iloc[0],.5)
  self.assertEqual(result.loc[result.date==pd.Timestamp('2026-03-02'),'mret5'].iloc[0],1.)
if __name__=='__main__':unittest.main()
