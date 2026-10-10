import json,tempfile,unittest
from pathlib import Path
from scripts.run_evolution_v2_20261010 import reconcile,pool_for
from scripts.evolution_safety_20261010 import durable_append,atomic_json,packed_signal,overlap
from scripts.audit_evolution_domains_20261010 import schema
class RecoveryTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.out=Path(self.temp.name);self.config={'seed':1,'batch':2,'workers':6,'domain_sha256':'x','gen2_sha256':'y'}
 def tearDown(self):self.temp.cleanup()
 def candidate(self,i):return {'genome_hash':f'genome{i}','generation':1,'side':'LONG'}
 def test_restart_after_candidates_and_partial_evaluation(self):
  cs=[self.candidate(1),self.candidate(2)]
  durable_append(self.out/'candidates.jsonl',cs)
  durable_append(self.out/'evaluations.jsonl',[{'genome_hash':'genome1','status':'EVALUATED_UNCERTIFIED','points':[]}])
  st,c,r=reconcile(self.out,self.config)
  self.assertEqual(st['generation'],0)
  self.assertEqual(len(c),2)
  self.assertEqual([x['genome_hash'] for x in cs if x['genome_hash'] not in r],['genome2'])
 def test_partial_candidate_generation_fail_closed(self):
  durable_append(self.out/'candidates.jsonl',[self.candidate(1)])
  with self.assertRaisesRegex(RuntimeError,'Partial candidate'):reconcile(self.out,self.config)
 def test_conflicting_duplicate_evaluations_fail_closed(self):
  durable_append(self.out/'candidates.jsonl',[self.candidate(1),self.candidate(2)])
  durable_append(self.out/'evaluations.jsonl',[{'genome_hash':'genome1','status':'A'},{'genome_hash':'genome1','status':'B'}])
  with self.assertRaisesRegex(RuntimeError,'Conflicting'):reconcile(self.out,self.config)
 def test_config_mismatch_fail_closed(self):
  atomic_json(self.out/'state.json',{'config':{'seed':99},'generation':0})
  with self.assertRaisesRegex(RuntimeError,'configuration mismatch'):reconcile(self.out,self.config)
 def test_behavioral_overlap(self):
  a=packed_signal([1,0,1,0,0]);b=packed_signal([1,0,1,0,0]);c=packed_signal([0,1,0,1,0])
  self.assertEqual(overlap(a,b),1)
  self.assertEqual(overlap(a,c),0)
if __name__=='__main__':unittest.main()
