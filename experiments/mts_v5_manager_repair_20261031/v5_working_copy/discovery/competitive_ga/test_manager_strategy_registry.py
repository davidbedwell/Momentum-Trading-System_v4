import unittest
from .manager_strategy_registry import readiness,require_all,AdapterStatus,FAMILIES
class TestRegistry(unittest.TestCase):
 def test_all_families_declared(self):
  self.assertEqual(tuple(s.family for s in readiness()),FAMILIES)
 def test_missing_adapters_block_full_ga(self):
  with self.assertRaises(RuntimeError):require_all()
 def test_complete_registry_passes(self):
  self.assertTrue(require_all([AdapterStatus(f,'test',True,'test') for f in FAMILIES]))
if __name__=='__main__':unittest.main()
