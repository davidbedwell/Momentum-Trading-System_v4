import tempfile
import unittest
from datetime import datetime,timezone
from pathlib import Path
from .ga_review_ledger import ReviewLedger

class TestReviewLedger(unittest.TestCase):
 def test_friday_once_persistent(self):
  with tempfile.TemporaryDirectory() as root:
   path=Path(root)/'reviews.sqlite'
   t=datetime(2026,10,30,23,tzinfo=timezone.utc)
   self.assertIsNotNone(ReviewLedger(path).claim(t))
   self.assertIsNone(ReviewLedger(path).claim(t))
   self.assertEqual(len(ReviewLedger(path).events()),1)
 def test_regime_requires_stable_id(self):
  with tempfile.TemporaryDirectory() as root:
   ledger=ReviewLedger(Path(root)/'reviews.sqlite')
   t=datetime(2026,10,27,20,tzinfo=timezone.utc)
   with self.assertRaises(ValueError):ledger.claim(t,True,True)
   self.assertIsNotNone(ledger.claim(t,True,True,'crash-001'))
   self.assertIsNone(ledger.claim(t,True,True,'crash-001'))
   self.assertIsNotNone(ledger.claim(t,True,True,'crash-002'))
 def test_no_daily_claim(self):
  with tempfile.TemporaryDirectory() as root:
   ledger=ReviewLedger(Path(root)/'reviews.sqlite')
   self.assertIsNone(ledger.claim(datetime(2026,10,27,20,tzinfo=timezone.utc)))
   self.assertEqual(ledger.events(),[])
if __name__=='__main__':unittest.main()
