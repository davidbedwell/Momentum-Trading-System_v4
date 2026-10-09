"""Frozen 6% SHORT borrowing economics and order eligibility checks."""
import unittest
ANNUAL_BORROW_RATE=0.06
DAYS_IN_BROKER_YEAR=360

def borrow_fee(collateral_value,calendar_days):
    if collateral_value < 0 or calendar_days < 0: raise ValueError('negative collateral or days')
    return collateral_value * ANNUAL_BORROW_RATE * calendar_days / DAYS_IN_BROKER_YEAR

def short_entry_allowed(quoted_rate,borrow_available):
    return bool(borrow_available and quoted_rate is not None and 0 <= quoted_rate <= ANNUAL_BORROW_RATE)

class BorrowPolicyTests(unittest.TestCase):
    def test_fee(self):self.assertAlmostEqual(borrow_fee(10000,20),33.333333333333336)
    def test_zero_days(self):self.assertEqual(borrow_fee(10000,0),0)
    def test_below_cap(self):self.assertTrue(short_entry_allowed(0.03,True))
    def test_at_cap(self):self.assertTrue(short_entry_allowed(0.06,True))
    def test_above_cap(self):self.assertFalse(short_entry_allowed(0.06001,True))
    def test_unavailable(self):self.assertFalse(short_entry_allowed(0.03,False))
    def test_unknown_quote(self):self.assertFalse(short_entry_allowed(None,True))
    def test_invalid(self):self.assertFalse(short_entry_allowed(-0.01,True))
if __name__=='__main__':unittest.main()
