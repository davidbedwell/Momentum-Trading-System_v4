import unittest
from Core.layered_ga.ga4_selection_adjusted_validation import validate

class SelectionTests(unittest.TestCase):
    def test_equal_performance_does_not_pass(self):
        x=validate({'a':[True]*25},[True]*25,[.1]*25,list(range(25)),attempts=1,digest='frozen')
        self.assertFalse(x['results']['a']['pass'])
        self.assertFalse(x['independently_verified'])
    def test_attempt_count_required(self):
        with self.assertRaises(ValueError):
            validate({'a':[True]*25,'b':[True]*25},[True]*25,[.1]*25,list(range(25)),attempts=1,digest='frozen')
    def test_small_clusters_fail(self):
        x=validate({'a':[True]*4},[True]*4,[.1]*4,list(range(4)),attempts=1,digest='frozen')
        self.assertFalse(x['results']['a']['pass'])
