import unittest
from pathlib import Path
import pandas as pd
from Core.layered_ga.ga4_optional_human_context import load_optional_context
class OptionalHumanContextTests(unittest.TestCase):
 def test_missing_artifacts_do_not_gate_machine_discovery(self):
  p=pd.DataFrame({'security_id':['A'],'effective_date':['2020-01-01'],'sector_id':['Technology']})
  frame,ref=load_optional_context(p,Path('/nonexistent-stage1-context'),{'galaxy_context.parquet':'fake'},lambda path: path.read_bytes())
  self.assertIsNone(frame)
  self.assertEqual(ref['status'],'UNAVAILABLE_OPTIONAL')
if __name__=='__main__':unittest.main()
