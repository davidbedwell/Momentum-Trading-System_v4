import unittest
import numpy as np
import pandas as pd
import study
class Tests(unittest.TestCase):
 def test_prefix_and_previous_close(self):
  dates=pd.bdate_range('2020-01-01',periods=260);x=pd.DataFrame({str(i):np.arange(260)+i+1. for i in range(21)},index=dates)
  a=study.multi.build(x,dates);b=study.multi.build(x.iloc[:230],dates[:230]);pd.testing.assert_frame_equal(a.iloc[:230],b)
  self.assertTrue((pd.to_datetime(a.feature_date.dropna())<a.feature_date.dropna().index).all());self.assertEqual(a.b200.first_valid_index(),dates[200]);self.assertEqual(a.b10.iloc[10],1)
 def test_selection_ignores_future_nav(self):
  dates=pd.bdate_range('2009-01-01',periods=1500);nav=np.linspace(100000,200000,len(dates));v=nav.copy();v[dates>=pd.Timestamp('2012-01-01')]=1
  self.assertEqual(study.rank_candidates(nav,dates,'2012-01-01'),study.rank_candidates(v,dates,'2012-01-01'))
 def test_archived_accounting_and_timing(self):
  t=pd.read_csv(study.R/'trades.csv.gz',parse_dates=['entry_date','exit_date','feature_date']);self.assertTrue((t.feature_date<t.entry_date).all());np.testing.assert_allclose(t.net_return,t.pnl/t.acquisition_cost,rtol=1e-10)
  self.assertTrue((t.mae_return<=1e-12).all());self.assertFalse(t.duplicated(['system','chromosome_id','entry_date','exit_date','ticker','fold']).any())
  s=pd.read_csv(study.R/'selection.csv');self.assertEqual(len(s),18)
  audit=pd.read_csv(study.R/'fold_audit.csv');self.assertEqual(int(audit.test_trades.sum()),len(t[t.system!='GA8']))
  self.assertEqual(t[t.system=='GA8'].groupby('year').size().to_dict(),{2023:133,2024:809,2025:555})
  for z in audit.itertuples():self.assertEqual(z.test_trades,len(t[(t.fold==z.fold)&(t.system==z.system)&(t.chromosome_id==z.chromosome_id)]))
  for z in s.itertuples():
   g=t[(t.fold==z.fold)&(t.chromosome_id==z.chromosome_id)&(t.system==z.system)];self.assertTrue((g.entry_date>=pd.Timestamp(z.training_end)).all());self.assertTrue((g.exit_date<pd.Timestamp(z.test_end)).all())
 def test_scaled_fill_accounting(self):
  fills=[dict(action='BUY',ticker='A',session=0,qty=10,price=10,cost=100.1,stop=9),dict(action='SELL',ticker='A',session=1,qty=5,price=11,net=54.945),dict(action='SELL',ticker='A',session=2,qty=5,price=12,net=59.94)]
  bars={(i,'A'):(10,9,0) for i in range(3)};o=study.reconstruct(dict(fills=fills),bars);cost,mae,pnl=o[('A',0,2)];self.assertAlmostEqual(cost,100.1);self.assertAlmostEqual(pnl,14.785);self.assertLess(mae,0)
if __name__=='__main__':unittest.main()
