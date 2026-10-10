import json,random,tempfile,unittest
from pathlib import Path
import numpy as np
from scripts.evolution_safety_20261010 import (domain_catalog,validate_genes,domain_mutate,packed_signal,overlap,atomic_json,recover_jsonl,durable_append)
class SafetyTests(unittest.TestCase):
 def test_overlap(self):
  a=packed_signal([1,0,1,0]);b=packed_signal([1,1,0,0])
  self.assertAlmostEqual(overlap(a,b),1/3)
  self.assertEqual(overlap(a,a),1)
  self.assertEqual(overlap(packed_signal([0,0]),packed_signal([0,0])),1)
  with self.assertRaises(ValueError):overlap(a,packed_signal([1]))
 def test_domain(self):
  catalog=domain_catalog();family='VOLATILITY'
  gene={k:values[0] for k,values in catalog[family].items()}
  self.assertTrue(validate_genes([[family,gene]],catalog))
  rng=random.Random(10)
  for _ in range(40):
   child=domain_mutate([[family,gene]],rng,catalog)
   self.assertTrue(validate_genes(child,catalog))
  bad=json.loads(json.dumps(gene));bad['threshold_quantile']=-999
  self.assertFalse(validate_genes([[family,bad]],catalog))
 def test_recovery(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'journal.jsonl';durable_append(p,[{'id':1},{'id':2}])
   with p.open('ab') as f:f.write(b'{"id":3')
   self.assertEqual(len(recover_jsonl(p)),2)
   durable_append(p,[{'id':3}])
   self.assertEqual([x['id'] for x in recover_jsonl(p)],[1,2,3])
   s=Path(t)/'state.json';atomic_json(s,{'generation':1})
   self.assertEqual(json.loads(s.read_text())['generation'],1)
if __name__=='__main__':unittest.main()
