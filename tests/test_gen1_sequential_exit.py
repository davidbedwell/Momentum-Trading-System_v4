import unittest
from Core.layered_ga.gen1_sequential_exit import replay

class SequentialExitTests(unittest.TestCase):
    def test_first_exit_and_loss_avoided(self):
        calls=[]
        def policy(s):
            calls.append(s['age'])
            return s['age']==2
        r=replay(100,[105,110,80,70],[{'age':i} for i in range(1,5)],policy,roundtrip_cost=.01)
        self.assertEqual(calls,[1,2]);self.assertEqual(r['exit_index'],1)
        self.assertAlmostEqual(r['realized_net'],.09)
        self.assertAlmostEqual(r['loss_avoided'],.40)
    def test_false_exit_and_forced_horizon(self):
        r=replay(100,[95,110],[{'age':1},{'age':2}],lambda _:True)
        self.assertAlmostEqual(r['missed_recovery'],.15)
        f=replay(100,[95,110],[{'age':1},{'age':2}],lambda _:False)
        self.assertTrue(f['forced']);self.assertEqual(f['gain_vs_horizon'],0)
    def test_short_and_invalid(self):
        r=replay(100,[90,120],[{},{}],lambda _:True,side=-1,roundtrip_cost=.02)
        self.assertAlmostEqual(r['realized_net'],.08)
        with self.assertRaises(ValueError):replay(100,[90],[{},{}],lambda _:False)

if __name__=='__main__':unittest.main()
