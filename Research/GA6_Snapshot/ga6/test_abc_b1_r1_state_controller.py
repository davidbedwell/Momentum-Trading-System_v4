import unittest
from ga6.abc_b1_r1_state_controller import qualify_statefully
class ControllerTests(unittest.TestCase):
 def test_b1_alone_enters_and_r1_exits(self):
  rows=[dict(date=str(i),A=False,B=False,B1=(i==2),C=False,R1_evidence=(i>=3)) for i in range(1,7)]
  s=qualify_statefully(rows)
  self.assertFalse(s[0].defensive)
  self.assertTrue(s[1].entered_defensive)
  self.assertEqual(s[1].source,'B1')
  self.assertTrue(s[3].defensive)
  self.assertTrue(s[4].exited_defensive)
 def test_crash_overrides_recovery(self):
  rows=[dict(date=str(i),A=False,B=False,B1=(i in (1,4)),C=False,R1_evidence=True) for i in range(1,6)]
  s=qualify_statefully(rows)
  self.assertTrue(s[3].defensive)
  self.assertFalse(s[3].exited_defensive)
 def test_missing_b1_rejected(self):
  with self.assertRaises(ValueError):qualify_statefully([dict(date='1',A=False,B=False,C=False,R1_evidence=False)])
if __name__=='__main__':unittest.main()
