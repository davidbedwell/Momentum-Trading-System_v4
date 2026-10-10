import tempfile,unittest
from pathlib import Path
import numpy as np,pandas as pd
from Core.layered_ga.parquet_controller_adapter import route_from_parquet,controller_from_parquet
class ControllerAdapterTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory()
  self.path=Path(self.temp.name)/"states.parquet"
  self.frame=pd.DataFrame({"date":["2020-01-02","2020-01-03","2020-01-06","2020-01-07"],
   "A":[False,True,False,False],"B":[False]*4,"C":[False]*4,"R1":[False,False,False,True]})
 def tearDown(self):self.temp.cleanup()
 def test_real_controller_transitions(self):
  self.frame.to_parquet(self.path,index=False)
  r=route_from_parquet(self.path,self.frame.date)
  self.assertEqual([x["state"] for x in r["declarations"]],["NORMAL","DEFENSIVE","DEFENSIVE","NORMAL"])
  np.testing.assert_array_equal(r["normal_entries_allowed"],[True,False,False,True])
  np.testing.assert_array_equal(r["defensive_transition_closes"],np.array(["2020-01-03"],dtype="datetime64[D]"))
  self.assertEqual(r["declarations"][1]["cash_first_actions"],["cancel_conflicting_entries","liquidate_equity_to_cash"])
 def test_missing_signals_fail_closed(self):
  self.frame.drop(columns=["C"]).to_parquet(self.path,index=False)
  with self.assertRaises(ValueError):controller_from_parquet(self.path)
 def test_null_fails_closed(self):
  self.frame["R1"]=self.frame["R1"].astype("boolean");self.frame.loc[1,"R1"]=pd.NA;self.frame.to_parquet(self.path,index=False)
  with self.assertRaises(ValueError):controller_from_parquet(self.path)
 def test_bad_checksum_fails(self):
  self.frame.to_parquet(self.path,index=False)
  with self.assertRaises(ValueError):controller_from_parquet(self.path,expected_sha256="0"*64)
 def test_abc_priority(self):
  self.frame.loc[1,"R1"]=True;self.frame.to_parquet(self.path,index=False)
  rows,_,_=controller_from_parquet(self.path)
  self.assertEqual(rows[1]["state"],"DEFENSIVE")
if __name__=="__main__":unittest.main()