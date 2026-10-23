import unittest
import pandas as pd
from causal_indicators import enrich

class CausalIndicatorTests(unittest.TestCase):
 def setUp(self):
  dates=pd.bdate_range('2026-01-01',periods=16)
  self.bars=pd.DataFrame([{'date':dt,'symbol':sym,'Close':100+i*(1 if sym=='A' else 2),'Volume':1000+i,'sector':('Tech' if sym=='A' else 'Other')} for sym in ('A','B') for i,dt in enumerate(dates)])
 def test_all_families_and_past_only(self):
  out=enrich(self.bars,windows=(5,))
  row=out[(out.symbol=='A')].iloc[-1]
  for name in ('acceleration','trend','liquidity','relative_strength','sector_strength','breadth'):
   self.assertTrue(pd.notna(row[f'{name}_5']),name)
 def test_future_append_does_not_change_past(self):
  a=enrich(self.bars[self.bars.date<=self.bars.date.unique()[13]],windows=(5,))
  b=enrich(self.bars,windows=(5,))
  for col in ('acceleration_5','trend_5','liquidity_5','relative_strength_5','sector_strength_5','breadth_5'):
   left=a[a.symbol=='A'].set_index('date')[col]
   right=b[b.symbol=='A'].set_index('date')[col].reindex(left.index)
   pd.testing.assert_series_equal(left,right)
 def test_no_sector_is_missing(self):
  out=enrich(self.bars.drop(columns=['sector']),windows=(5,))
  self.assertTrue(out.sector_strength_5.isna().all())
