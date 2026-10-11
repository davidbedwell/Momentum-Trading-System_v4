import unittest
from datetime import date,timedelta
from Core.layered_ga.normal_regime_tape import RegimeClose,compile_normal_tape,normal_entry_decisions,defensive_transition_dates

class TestNormalTape(unittest.TestCase):
    def row(self,n,**kw):
        s=dict(a=False,b=False,b1=False,c=False,r1=False);s.update(kw)
        return RegimeClose(date(2020,1,1)+timedelta(days=n),**s)
    def test_conflict_defensive_wins(self):
        t=compile_normal_tape([self.row(0),self.row(1,b1=True,r1=True),self.row(2,r1=True)])
        self.assertEqual([r[1] for r in t],['NORMAL','DEFENSIVE','NORMAL'])
        self.assertEqual(normal_entry_decisions(t)[1][1],False)
        self.assertEqual(defensive_transition_dates(t),(self.row(1).day,))
    def test_all_crash_detectors(self):
        for signal in ('a','b','b1','c'):
            t=compile_normal_tape([self.row(0,**{signal:True})])
            self.assertEqual(t[0][1],'DEFENSIVE')
    def test_no_r1_no_release(self):
        t=compile_normal_tape([self.row(0,c=True),self.row(1)])
        self.assertEqual(t[-1][1],'DEFENSIVE')
    def test_fail_closed(self):
        with self.assertRaises(ValueError):compile_normal_tape([])
        with self.assertRaises(ValueError):compile_normal_tape([self.row(1),self.row(0)])
        with self.assertRaises(ValueError):compile_normal_tape([self.row(0),self.row(0)])
        with self.assertRaises(ValueError):compile_normal_tape([self.row(0,r1=None)])
    def test_release_only_when_defensive(self):
        t=compile_normal_tape([self.row(0,r1=True)])
        self.assertEqual(t[0][1],'NORMAL')

if __name__=='__main__':unittest.main()
