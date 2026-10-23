import unittest
from unittest.mock import patch
import pandas as pd
from context_free_genome import Genome
from historical_fitness import measured_discovery_fitness
class FitnessTests(unittest.TestCase):
 def setUp(self):
  self.g=Genome({'op':'AND','children':[{'feature':'momentum','window':20,'threshold':0,'direction':'>=','transform':'raw'},{'feature':'volume','window':20,'threshold':0,'direction':'>=','transform':'raw'}]},hold_sessions=2)
  self.folds=[]
  for month in (1,2):
   dates=pd.bdate_range(f'2026-{month:02d}-05',periods=8)
   self.folds.append({'bars':pd.DataFrame([{'date':d,'symbol':'A','Open':100+i,'Close':100+i,'tradable_bar':True,'eligible_signal':True,'return_20':.2,'volume_ratio_20':1.2,'Stock Splits':0.,'Dividends':0.} for i,d in enumerate(dates)])})
 def test_measured(self):
  m=measured_discovery_fitness(self.g,self.folds,{'A':[]},{'A'})
  self.assertGreater(m['net_ev'],0)
  self.assertGreater(m['opportunity_coverage'],0)
 def test_missing_earnings_fails(self):
  with self.assertRaises(ValueError):measured_discovery_fitness(self.g,self.folds,{},set())
 def test_overlap_fails(self):
  with self.assertRaises(ValueError):measured_discovery_fitness(self.g,[self.folds[0],self.folds[0]],{'A':[]},{'A'})
