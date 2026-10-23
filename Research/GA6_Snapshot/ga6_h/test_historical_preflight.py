import unittest
import pandas as pd
from historical_preflight import preflight
class PreflightTests(unittest.TestCase):
 def setUp(self):
  self.bars=pd.DataFrame([{'date':'2026-01-05','symbol':'A','Open':100.,'High':101.,'Low':99.,'Close':100.,'Volume':10000,'Stock Splits':0.,'Dividends':0.,'tradable_bar':True}])
  self.evidence={'source':'audited_vendor','coverage_audited':True,'asof_timestamp_audited':True,'corporate_actions_verified':True}
 def test_valid_explicit_evidence(self):self.assertTrue(preflight(self.bars,{'A':[]},{'A'},discovery_end='2026-01-31',evidence=self.evidence)['passed'])
 def test_missing_provenance(self):self.assertFalse(preflight(self.bars,{'A':[]},{'A'},discovery_end='2026-01-31')['passed'])
 def test_bad_ohlc(self):
  b=self.bars.copy();b.loc[0,'High']=90
  self.assertFalse(preflight(b,{'A':[]},{'A'},discovery_end='2026-01-31',evidence=self.evidence)['passed'])
 def test_duplicate_bar(self):
  b=pd.concat([self.bars,self.bars],ignore_index=True)
  self.assertFalse(preflight(b,{'A':[]},{'A'},discovery_end='2026-01-31',evidence=self.evidence)['passed'])
