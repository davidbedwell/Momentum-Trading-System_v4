import json,random,unittest
from scripts.audit_evolution_domains_20261010 import schema,valid,mutate,audit
class DomainAuditTests(unittest.TestCase):
 def test_all_original_parents_valid(self):
  from scripts.audit_evolution_domains_20261010 import FILES
  s=schema()
  for line in FILES['gen1_parents'].open():
   self.assertTrue(valid(json.loads(line)['chromosomes'],s))
 def test_bounded_numeric_and_categorical(self):
  s=schema();f='MOMENTUM';g={k:(v['values'][0] if v['kind']=='categorical' else v['min']) for k,v in s[f].items()}
  self.assertTrue(valid([[f,g]],s))
  rng=random.Random(22)
  for _ in range(100):
   child=mutate([[f,g]],rng,s);self.assertTrue(valid(child,s))
  bad=json.loads(json.dumps(g));bad['context_threshold']=2
  self.assertFalse(valid([[f,bad]],s))
  bad=json.loads(json.dumps(g));bad['direction']='SIDEWAYS'
  self.assertFalse(valid([[f,bad]],s))
 def test_audit_counts(self):
  a=audit()
  self.assertEqual(a['files']['gen1_parents']['outside_proposed_bounds'],0)
  self.assertEqual(a['files']['gen2_children']['count'],1200)
if __name__=='__main__':unittest.main()
