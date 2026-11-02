import unittest
import pandas as pd
from .horizons_next_open_execution import Book,queue
from .horizons_session_settlement import SessionSettlement
class TestSessionSettlement(unittest.TestCase):
 def test_holiday_gap_and_t_plus_one(self):
  cal=SessionSettlement(pd.to_datetime(['2026-07-02','2026-07-06','2026-07-07']))
  b=Book(cash=0.,shares={'A':100.})
  cal.advance(b,'2026-07-02');queue(b,{'A':{'target_weight':0.}})
  cal.execute(b,{'A':100.},sector_by_ticker={'A':'tech'},return_tickers=['A'])
  self.assertEqual(b.cash,0.);self.assertEqual(b.unsettled_cash,10000.)
  with self.assertRaises(ValueError):cal.advance(b,'2026-07-03')
  cal.advance(b,'2026-07-06')
  self.assertEqual(b.cash,10000.);self.assertEqual(b.unsettled_cash,0.)
 def test_controller_blocks_correlated_orders(self):
  import numpy as np
  cal=SessionSettlement(['2026-01-05','2026-01-06'])
  b=Book()
  cal.advance(b,'2026-01-05')
  queue(b,{'A':{'target_weight':.1},'B':{'target_weight':.1},'C':{'target_weight':.1}})
  x=np.sin(np.arange(70)*.37)/100
  history=np.column_stack([x,x,x])
  with self.assertRaisesRegex(ValueError,'correlated cluster'):
   cal.execute(b,{'A':100.,'B':100.,'C':100.},sector_by_ticker={'A':'tech','B':'health','C':'energy'},prior_returns=history,return_tickers=['A','B','C'])
  self.assertEqual(b.shares,{})
  self.assertEqual(b.cash,100000.)
 def test_no_skipped_sessions(self):
  cal=SessionSettlement(['2026-01-05','2026-01-06','2026-01-07'])
  with self.assertRaises(ValueError):cal.advance(Book(),'2026-01-06')
 def test_bad_calendar(self):
  with self.assertRaises(ValueError):SessionSettlement(['2026-01-05','2026-01-05'])
if __name__=='__main__':unittest.main()
