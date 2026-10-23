import unittest
import pandas as pd
from daily_simulator import simulate

class SimulatorTests(unittest.TestCase):
    def setUp(self):
        dates=pd.bdate_range('2026-10-19',periods=8)
        self.bars=pd.DataFrame([{'date':d,'symbol':s,'Open':100+i,'Close':101+i,'tradable_bar':True} for i,d in enumerate(dates) for s in ('ABC','XYZ')])
        self.ranks=pd.DataFrame([{'date':d,'symbol':'ABC','score':1.0} for d in dates])
        self.verified={'ABC'}
        self.schedules={'ABC':[]}
    def test_next_open_and_max_hold(self):
        eq,tr=simulate(self.bars,self.ranks,self.schedules,self.verified,hold_sessions=2,max_positions=1,price_adjustment_type="backward_adjusted_verified")
        self.assertEqual(tr.iloc[0].date,'2026-10-20')
        self.assertEqual(tr.iloc[0].side,'buy')
        self.assertEqual(tr.iloc[1].side,'sell')
        self.assertEqual(tr.iloc[1].date,'2026-10-22')
        self.assertEqual(len(eq),8)
    def test_missing_schedule_no_buys(self):
        _,tr=simulate(self.bars,self.ranks,{},set(),hold_sessions=2,price_adjustment_type="backward_adjusted_verified")
        self.assertTrue(tr.empty)
    def test_earnings_blocks_entry(self):
        self.schedules['ABC']=[{'date':'2026-10-22','known_at':'2026-10-15T12:00:00+00:00'}]
        _,tr=simulate(self.bars,self.ranks,self.schedules,self.verified,hold_sessions=2,price_adjustment_type="backward_adjusted_verified")
        self.assertTrue(tr.empty or tr.iloc[0].date>='2026-10-27')
    def test_entry_threshold_rejects_candidates(self):
        _,tr=simulate(self.bars,self.ranks,self.schedules,self.verified,hold_sessions=2,price_adjustment_type='backward_adjusted_verified',entry_threshold=2.0)
        self.assertTrue(tr.empty)
    def test_entry_threshold_accepts_candidates(self):
        _,tr=simulate(self.bars,self.ranks,self.schedules,self.verified,hold_sessions=2,price_adjustment_type='backward_adjusted_verified',entry_threshold=0.5)
        self.assertFalse(tr.empty)
    def test_close_stop_exits_next_open(self):
        bars=self.bars.copy()
        bars.loc[(bars.symbol=='ABC') & (bars.date==bars.date.unique()[2]),'Close']=80
        _,tr=simulate(bars,self.ranks,self.schedules,self.verified,hold_sessions=8,stop_loss=.10,price_adjustment_type='backward_adjusted_verified')
        self.assertEqual(tr.iloc[1].side,'sell')
        self.assertEqual(tr.iloc[1].date,'2026-10-22')
    def test_trailing_stop_exits_next_open(self):
        bars=self.bars.copy()
        bars.loc[(bars.symbol=='ABC') & (bars.date==bars.date.unique()[2]),'Close']=80
        _,tr=simulate(bars,self.ranks,self.schedules,self.verified,hold_sessions=8,trailing_stop=.10,price_adjustment_type='backward_adjusted_verified')
        self.assertEqual(tr.iloc[1].side,'sell')
    def test_invalid_stops(self):
        with self.assertRaises(ValueError):simulate(self.bars,self.ranks,self.schedules,self.verified,stop_loss=1.5,price_adjustment_type='backward_adjusted_verified')
    def test_replacement_only_when_margin_met(self):
        bars=self.bars.copy()
        ranks=pd.DataFrame([{'date':d,'symbol':s,'score':(1. if s=='ABC' else (3. if i>=2 else 0.))} for i,d in enumerate(bars.date.unique()) for s in ('ABC','XYZ')])
        eq,tr=simulate(bars,ranks,{'ABC':[],'XYZ':[]},{'ABC','XYZ'},hold_sessions=8,max_positions=1,replace_threshold=1.0,price_adjustment_type='backward_adjusted_verified')
        self.assertTrue(((tr.symbol=='ABC')&(tr.side=='sell')).any())
        self.assertTrue(((tr.symbol=='XYZ')&(tr.side=='buy')).any())
    def test_replacement_margin_blocks(self):
        bars=self.bars.copy()
        ranks=pd.DataFrame([{'date':d,'symbol':s,'score':(1. if s=='ABC' else (3. if i>=2 else 0.))} for i,d in enumerate(bars.date.unique()) for s in ('ABC','XYZ')])
        eq,tr=simulate(bars,ranks,{'ABC':[],'XYZ':[]},{'ABC','XYZ'},hold_sessions=8,max_positions=1,replace_threshold=5.0,price_adjustment_type='backward_adjusted_verified')
        self.assertFalse(((tr.symbol=='ABC')&(tr.side=='sell')).any())
    def test_price_mode_fail_closed(self):
        with self.assertRaises(ValueError):simulate(self.bars,self.ranks,self.schedules,self.verified)
        with self.assertRaises(ValueError):simulate(self.bars,self.ranks,self.schedules,self.verified,price_adjustment_type='unadjusted_with_actions')
    def test_dividend_credited_to_cash(self):
        bars=self.bars.copy();bars['Stock Splits']=0.0;bars['Dividends']=0.0
        _,base=simulate(bars,self.ranks,self.schedules,self.verified,hold_sessions=8,price_adjustment_type='unadjusted_with_actions')
        bars.loc[(bars.symbol=='ABC') & (bars.date==bars.date.unique()[2]),'Dividends']=1.0
        eq,tr=simulate(bars,self.ranks,self.schedules,self.verified,hold_sessions=8,price_adjustment_type='unadjusted_with_actions')
        self.assertFalse(base.empty)
        self.assertGreater(eq.iloc[2].cash,0)
    def test_split_preserves_equity(self):
        bars=self.bars.copy();bars['Stock Splits']=0.0;bars['Dividends']=0.0
        bars[['Open','Close']]=bars[['Open','Close']].astype(float)
        d=bars.date.unique()[2]
        bars.loc[(bars.symbol=='ABC') & (bars.date>=d),['Open','Close']]/=2
        bars.loc[(bars.symbol=='ABC') & (bars.date==d),'Stock Splits']=2.0
        eq,tr=simulate(bars,self.ranks,self.schedules,self.verified,hold_sessions=8,price_adjustment_type='unadjusted_with_actions')
        self.assertEqual(tr.iloc[0].side,'buy')
        self.assertGreater(eq.iloc[2].equity,90000)
    def test_discovery_boundary(self):
        with self.assertRaises(ValueError):simulate(self.bars,self.ranks,self.schedules,self.verified,price_adjustment_type='backward_adjusted_verified',discovery_end_date='2026-10-20')
    def test_hold_cap(self):
        with self.assertRaises(ValueError):simulate(self.bars,self.ranks,self.schedules,self.verified,hold_sessions=41,price_adjustment_type="backward_adjusted_verified")

if __name__=='__main__':unittest.main()
