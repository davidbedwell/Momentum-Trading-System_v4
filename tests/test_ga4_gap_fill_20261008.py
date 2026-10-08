import unittest
from Core.layered_ga.ga4_gap_fill import emergency_exit

class GapFillTests(unittest.TestCase):
    def test_long_gap_fills_open_not_stop(self):
        x=emergency_exit("LONG",100,90,[{"open":85,"high":89,"low":80}])
        self.assertEqual((x["fill"],x["type"]),(85,"GAP_THROUGH"))
    def test_short_gap_fills_open_not_stop(self):
        x=emergency_exit("SHORT",100,110,[{"open":120,"high":125,"low":115}])
        self.assertEqual((x["fill"],x["type"]),(120,"GAP_THROUGH"))
    def test_intraday_long_stop(self):
        self.assertEqual(emergency_exit("LONG",100,90,[{"open":95,"high":99,"low":89}])["fill"],90)
    def test_intraday_short_stop(self):
        self.assertEqual(emergency_exit("SHORT",100,110,[{"open":105,"high":112,"low":103}])["fill"],110)
    def test_no_breach(self):
        self.assertIsNone(emergency_exit("LONG",100,90,[{"open":100,"high":105,"low":95}]))
if __name__=="__main__":
    unittest.main()
