import unittest
from ga7.engine import Genome
from ga7.request_replay import replay_requests

class ReplayTests(unittest.TestCase):
    def test_entry_and_exit_requests(self):
        g = Genome("momentum","a","b","AND",0,0,.08,2,"signal_decay",.02)
        sessions = []
        for i in range(6):
            price = 100+i
            sessions.append((str(i), {"AAA":{"open":price,"close":price+.5,
                "low":price-.5,"eligible":True,"dividend":0.,
                "features":{"a":1.,"b":1.}}},False))
        metrics, ledger = replay_requests(g,sessions,lambda genome,bar:True)
        self.assertGreater(metrics["requests"],0)
        self.assertTrue(any(r["action"]=="ENTER" for r in ledger.requests))
        self.assertGreater(metrics["trades"],0)
        self.assertTrue(all(not r["calibrated"] for r in ledger.requests))
        self.assertGreater(metrics["trades"],0)

    def test_partial_reduction_and_final_liquidation_accounting(self):
        g = Genome("momentum","a","b","AND",0,0,.10,1,"signal_decay",.02)
        prices = [(100.,100.), (100.,100.), (100.,100.), (98.,98.),
                  (98.,100.), (99.,99.)]
        sessions = []
        for i, (op, close) in enumerate(prices):
            sessions.append((str(i), {"AAA":{"open":op,"close":close,
                "low":min(op,close),"eligible":True,"dividend":0.,
                "features":{"a":1.,"b":1.}}},False))
        metrics, ledger = replay_requests(g,sessions,lambda genome,bar:True,
                                         cash_yield=0.)
        self.assertGreaterEqual(metrics["outcomes"],1)
        self.assertEqual(len(ledger.outcomes),metrics["outcomes"])
        self.assertTrue(all(x["horizon_sessions"]>0 for x in ledger.outcomes))
        self.assertGreaterEqual(metrics["trades"],1)
        self.assertTrue(0 < metrics["final_nav"] < 200000)

    def test_defense_blocks_entry(self):
        g = Genome("momentum","a","b","AND",0,0,.08,2,"signal_decay",.02)
        sessions = [(str(i),{"AAA":{"open":100.,"close":100.,
            "low":99.,"eligible":True,"features":{"a":1.,"b":1.}}},True)
            for i in range(3)]
        metrics, ledger = replay_requests(g,sessions,lambda genome,bar:True)
        self.assertEqual(metrics["trades"],0)
        self.assertEqual(len(ledger.requests),0)

if __name__ == "__main__":
    unittest.main()
