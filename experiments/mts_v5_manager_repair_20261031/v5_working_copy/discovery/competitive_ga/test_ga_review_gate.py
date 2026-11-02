import unittest
from datetime import datetime,timezone
from .ga_review_gate import review_due,ValidationEvidence,eligible_for_promotion
class TestReviewGate(unittest.TestCase):
 def test_friday_night(self):
  r=review_due(datetime(2026,10,30,23,0,tzinfo=timezone.utc))
  self.assertTrue(r.review)
  self.assertFalse(r.evolve)
 def test_regime_event(self):
  r=review_due(datetime(2026,10,27,18,0,tzinfo=timezone.utc),True,True)
  self.assertEqual(r.reason,'DRAMATIC_REGIME_CHANGE')
  self.assertTrue(r.evolve)
 def test_no_daily_retraining(self):
  self.assertFalse(review_due(datetime(2026,10,27,18,0,tzinfo=timezone.utc)).review)
 def test_naive_time_rejected(self):
  with self.assertRaises(ValueError):review_due(datetime(2026,10,30,23))
 def test_promotion_gate(self):
  e=ValidationEvidence(.10,.15,.12,.10,True,True,True,True,.02,True)
  self.assertTrue(eligible_for_promotion(e))
  self.assertFalse(eligible_for_promotion(ValidationEvidence(.10,.15,.12,.10,False,True,True,True,.02,True)))
  self.assertFalse(eligible_for_promotion(ValidationEvidence(.10,.15,.12,.25,True,True,True,True,.02,True)))
if __name__=='__main__':unittest.main()
