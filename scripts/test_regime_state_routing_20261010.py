import unittest
import numpy as np
from Core.layered_ga.regime_state_routing import normal_entry_eligibility,defensive_transition_closes
class StateRoutingTests(unittest.TestCase):
 def setUp(self):
  self.days=["2020-01-02","2020-01-03","2020-01-06","2020-01-07","2020-01-08"]
  self.states=["NORMAL","DEFENSIVE","DEFENSIVE","NORMAL","NORMAL"]
 def test_normal_defensive_normal(self):
  got=normal_entry_eligibility(self.days,self.days,self.states)
  np.testing.assert_array_equal(got,[True,False,False,True,True])
 def test_transition_only_once(self):
  got=defensive_transition_closes(self.days,self.states)
  np.testing.assert_array_equal(got,np.array(["2020-01-03"],dtype="datetime64[D]"))
 def test_no_future_state_leak(self):
  got=normal_entry_eligibility(["2020-01-01","2020-01-04","2020-01-09"],self.days,self.states)
  np.testing.assert_array_equal(got,[False,False,True])
 def test_bad_tape_rejected(self):
  with self.assertRaises(ValueError):
   normal_entry_eligibility(self.days,self.days,["NORMAL"]*4)
  with self.assertRaises(ValueError):
   normal_entry_eligibility(self.days,list(reversed(self.days)),self.states)
if __name__=="__main__":unittest.main()