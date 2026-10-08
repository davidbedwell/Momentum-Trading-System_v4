import unittest
from unittest.mock import patch
from types import SimpleNamespace
from Core.layered_ga.ga4_relationship_catalog import relationship_record
from scripts import run_ga4_parallel_dev80 as runner

class TradeSideIsolationTests(unittest.TestCase):
 def test_candidate_ids_differ_by_side(self):
  points=[{'horizon':i,'ev_net':0.0,'mae_mean':0.0,'n':1,'effective_n':1} for i in range(1,64)]
  def record(side):
   curve=SimpleNamespace(side=side,points=points,pareto_horizons=(),pareto_ranges=())
   return relationship_record(chromosomes=['MOMENTUM:{}'],context={'scope':'DEV80_ELIGIBLE'},curve=curve,fold='DEV80',data_provenance='test')
  a,b=record('LONG'),record('SHORT')
  self.assertNotEqual(a['candidate_id'],b['candidate_id'])
  self.assertEqual(a['side'],'LONG');self.assertEqual(b['side'],'SHORT')
 def test_runner_passes_side_in_both_metadata_modes(self):
  calls=[]
  def fake(**kwargs):
   calls.append(kwargs)
   return {'side':kwargs['side'],'daily_horizon_evidence':[{'horizon':i,'ev_net':0.0,'lcb95':0.0,'mae_mean':0.0,'mae_tail5':0.0} for i in range(1,64)],'pareto_horizons':[],'pareto_ranges':[]}
  for linked in (None,object()):
   with patch.object(runner,'initialize',return_value=(None,None,None,None,None,'test',linked,{'status':'ALIGNED_METADATA_NOT_PIT_CERTIFIED'})),patch.object(runner,'evaluate_conditional_candidate',side_effect=fake):
    runner.evaluate_long((('MOMENTUM',{}),))
    runner.evaluate_short((('MOMENTUM',{}),))
  self.assertEqual([x['side'] for x in calls],['LONG','SHORT','LONG','SHORT'])
  self.assertEqual([x.get('stage1_context_frame') is not None for x in calls],[False,False,True,True])
if __name__=='__main__':unittest.main()
