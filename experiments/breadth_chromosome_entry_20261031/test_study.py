import unittest
import numpy as np
import pandas as pd
from study import causal_features,regime,contrast,ROOT
from ga8_study import reconstruct
class StudyTests(unittest.TestCase):
 def test_threshold_boundaries(self):
  self.assertEqual(list(regime(pd.Series([.399,.4,.6,.601,np.nan]))),['weak','medium','medium','strong','missing'])
 def test_prefix_causality_and_eligibility(self):
  dates=pd.bdate_range('2000-01-01',periods=260);p=pd.Series(np.linspace(100,150,260),index=dates)
  x=pd.DataFrame({str(i):p+i for i in range(20)});f=causal_features(p,{'DEV79':x})
  pd.testing.assert_frame_equal(f.iloc[:220],causal_features(p.iloc[:220],{'DEV79':x.iloc[:220]}))
  self.assertTrue(f.DEV79_b50.iloc[:49].isna().all());self.assertEqual(f.DEV79_n50.iloc[49],20)
  self.assertTrue(causal_features(p,{'DEV79':x.iloc[:,:19]}).DEV79_b50.isna().all())
 def test_partial_fills_dividends_and_no_double_slippage(self):
  def fill(date,act,q,price):return dict(date=date,ticker='A',gene=0,quantity=q,price=price,cost=999,action=act)
  fills=[fill('2023-01-02','ENTRY',10,100),fill('2023-01-03','ADD',2,90),fill('2023-01-04','REDUCE',6,110),fill('2023-01-05','EXIT',6,120)]
  div=pd.DataFrame({'A':[0,1,2,0]},index=pd.to_datetime(['2023-01-02','2023-01-03','2023-01-04','2023-01-05']))
  closed,opened=reconstruct(fills,div);self.assertFalse(opened);self.assertEqual(len(closed),1)
  self.assertAlmostEqual(closed[0]['dividends'],34)
  self.assertAlmostEqual(closed[0]['pnl'],660+720+34-1180-(1000+180+660+720)*.0001)
 def test_archival_counts_and_feature_lag(self):
  t=pd.read_csv(ROOT/'trades.csv.gz',usecols=['entry_date','feature_date','identity_sample','system'])
  self.assertTrue((pd.to_datetime(t.feature_date)<pd.to_datetime(t.entry_date)).all())
  self.assertEqual(len(t),int(pd.read_csv(ROOT/'ledger_inventory.csv').trades.sum()))
  g=pd.read_csv(ROOT/'ga8_inventory.csv');self.assertEqual(list(g.closed),[133,809,555]);self.assertEqual(int(g.open_excluded.sum()),11)
  gt=pd.read_csv(ROOT/'ga8_trades.csv');self.assertAlmostEqual(gt[gt.year.eq(2023)].pnl.sum(),float(g[g.year.eq(2023)].final_nav.iloc[0])-100000,places=6)
if __name__=='__main__':unittest.main()
