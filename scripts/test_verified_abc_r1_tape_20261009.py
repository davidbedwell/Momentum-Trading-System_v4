import csv,tempfile,unittest
from pathlib import Path
from scripts.replay_verified_abc_r1_tape_20261009 import run
class TapeTests(unittest.TestCase):
 def test_replay_and_hash(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'tape.csv';o=Path(td)/'report.json'
   with p.open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['date','A','B','C','R1_evidence']);w.writerows([['2026-01-01',1,0,0,0],['2026-01-02',0,0,0,0],['2026-01-03',0,0,0,1]])
   r=run(p,o);self.assertEqual(r['crash_entries'],['2026-01-01']);self.assertEqual(r['r1_exits'],['2026-01-03']);self.assertEqual(r['defensive_sessions'],2);self.assertTrue(o.exists())
 def test_missing_signals_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'tape.csv';p.write_text('date,A,B,C,R1_evidence\n2026-01-01,1,,0,0\n')
   with self.assertRaises(ValueError):run(p,Path(td)/'report.json')
if __name__=='__main__':unittest.main()
