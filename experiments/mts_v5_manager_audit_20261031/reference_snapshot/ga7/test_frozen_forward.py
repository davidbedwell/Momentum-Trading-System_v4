import tempfile,unittest,json
from pathlib import Path
from ga7.frozen_forward import read_final_generation
class FrozenForwardTests(unittest.TestCase):
 def test_requires_completed_generation(self):
  with tempfile.TemporaryDirectory() as root:
   with self.assertRaisesRegex(ValueError,'No completed generation'):
    read_final_generation(root)
 def test_rejects_empty_generation(self):
  with tempfile.TemporaryDirectory() as root:
   Path(root,'generation_0001.jsonl').write_text('')
   with self.assertRaisesRegex(ValueError,'Empty generation'):
    read_final_generation(root)
if __name__=='__main__':unittest.main()
