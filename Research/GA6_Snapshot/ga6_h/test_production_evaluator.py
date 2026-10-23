import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch
from context_free_genome import Genome
from production_evaluator import HistoricalDiscoveryEvaluator
from evolution_engine import run
class EvaluatorWiringTests(unittest.TestCase):
 def test_real_evaluator_contract(self):
  g=Genome({'op':'AND','children':[{'feature':'momentum','window':20,'threshold':0,'direction':'>=','transform':'raw'},{'feature':'volume','window':20,'threshold':0,'direction':'>=','transform':'raw'}]})
  adapter=HistoricalDiscoveryEvaluator([],{},set())
  with self.assertRaises(ValueError):adapter(g)
 def test_runner_accepts_non_diagnostic_evaluator(self):
  def measured_mock(g):
   return {'net_ev':.01,'ev_per_session':.001,'reliability':.5,'training_consistency':.8,'opportunity_coverage':.2}
  with tempfile.TemporaryDirectory() as d:
   result=run(d,population=4,generations=1,evaluator=measured_mock,evaluator_id='historical_mock_test')
   self.assertEqual(result['mode'],'historical_mock_test')
   self.assertTrue((Path(d)/'checkpoint.json').exists())
