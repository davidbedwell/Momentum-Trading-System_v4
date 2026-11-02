import tempfile,unittest
from pathlib import Path
from ga7.defense_contract import read_defense_state
HEADER='date,defensive,A_v2,B,B1,C,R1\n'
class DefenseContractTests(unittest.TestCase):
 def check(self,content):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'state.csv';p.write_text(content)
   return read_defense_state(p)
 def test_complete_state(self):
  x=self.check(HEADER+'2020-01-01,1,1,0,0,0,0\n2020-01-02,0,0,0,0,0,1\n')
  self.assertTrue(x['2020-01-02']['R1'])
 def test_reject_partial_state(self):
  with self.assertRaisesRegex(ValueError,'Full A-v2/B'):
   self.check('date,defensive\n2020-01-01,0\n')
 def test_r1_signal_can_overlap_active_trigger(self):
  x=self.check(HEADER+'2020-01-01,1,1,0,0,0,1\n')
  self.assertTrue(x['2020-01-01']['defensive'])
 def test_trigger_cannot_be_normal(self):
  with self.assertRaisesRegex(ValueError,'trigger marked normal'):
   self.check(HEADER+'2020-01-01,0,0,1,0,0,0\n')
 def test_r1_readiness_does_not_force_exit(self):
  x=self.check(HEADER+'2020-01-01,1,0,0,0,0,1\n')
  self.assertTrue(x['2020-01-01']['defensive'])
 def test_cannot_exit_defense_without_r1(self):
  with self.assertRaisesRegex(ValueError,'without R-1'):
   self.check(HEADER+'2020-01-01,1,0,0,1,0,0\n2020-01-02,0,0,0,0,0,0\n')
 def test_reject_unsorted_dates(self):
  with self.assertRaisesRegex(ValueError,'strictly increasing'):
   self.check(HEADER+'2020-01-02,0,0,0,0,0,0\n2020-01-01,0,0,0,0,0,0\n')
 def test_defense_persists_without_new_trigger(self):
  x=self.check(HEADER+'2020-01-01,1,1,0,0,0,0\n2020-01-02,1,0,0,0,0,0\n2020-01-03,0,0,0,0,0,1\n')
  self.assertTrue(x['2020-01-02']['defensive'])
if __name__=='__main__':unittest.main()
