import unittest
import pandas as pd
from Core.layered_ga.ga4_stage1_context_join import attach_context
class TestStage1Join(unittest.TestCase):
 def setUp(self):
  self.d=pd.DataFrame({'security_id':['A','B'],'effective_date':['2020-01-02','2010-01-02'],'sector_id':['Technology','Utilities']})
  self.g=pd.DataFrame({'date':['2020-01-02'],'state':['Up'],'strength':[.3],'trajectory':[.1],'rv20':[.2]})
  self.s=pd.DataFrame({'date':['2020-01-02'],'context_key':['XLK'],'state':['Flat'],'strength':[.2],'trajectory':[.4],'rv20':[.3],'rel20':[.1],'rel60':[.2]})
 def test_missing_is_preserved(self):
  o=attach_context(self.d,self.g,self.s)
  self.assertEqual(len(o),2)
  self.assertEqual(o.iloc[0].sector_etf,'XLK')
  self.assertTrue(pd.isna(o.iloc[1].galaxy_strength))
 def test_unknown_sector_rejected(self):
  self.d.loc[0,'sector_id']='Unknown'
  with self.assertRaises(ValueError):attach_context(self.d,self.g,self.s)
 def test_duplicate_context_rejected(self):
  with self.assertRaises(ValueError):attach_context(self.d,pd.concat([self.g,self.g]),self.s)
if __name__=='__main__':unittest.main()
