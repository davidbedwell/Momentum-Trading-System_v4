from dataclasses import replace
import unittest
from .functionality_fixture import fixture,execute

class ManagerControls(unittest.TestCase):
    def test_ranking_sizing_and_cash(self):
        p,g,m=fixture();a=execute(p,g,m)
        b=execute(p,g,replace(m,niche_bias=(-2.,2.,0.)))
        self.assertNotEqual(a['fills'][0]['ticker'],b['fills'][0]['ticker'])
        c=execute(p,g,replace(m,size_scale=.3))
        self.assertLess(c['fills'][0]['notional'],a['fills'][0]['notional'])
        self.assertEqual(execute(p,g,replace(m,entry_floor=10))['fills'],[])
    def test_manager_exit_and_native_precedence(self):
        p,g,m=fixture();r=execute(p,g,replace(m,exit_floor=3))
        self.assertTrue(any(f['reason']=='manager_exit' for f in r['fills']))
        p.features['trend'][:]=-1
        r=execute(p,g,replace(m,exit_floor=3))
        self.assertTrue(any(f['reason']=='native_exit' for f in r['fills']))
    def test_specialist_bias_routes_same_symbol(self):
        p,g,m=fixture()
        g=[g[0],replace(g[0],family='volume')]
        a=execute(p,g,replace(m,specialist_bias=(4.,0.)))
        b=execute(p,g,replace(m,specialist_bias=(0.,4.)))
        self.assertEqual(a['fills'][0]['gene'],0)
        self.assertEqual(b['fills'][0]['gene'],1)

    def test_add_switch_changes_fills(self):
        p,g,m=fixture();p.close[2:]=103.;p.open[3:]=103.
        p.features['momentum'][:]=1.;p.features['trend'][:]=1.
        g=[replace(x,add=.001) for x in g]
        m=replace(m,reserve=0.)
        yes=execute(p,g,m);no=execute(p,g,replace(m,allow_add=False))
        self.assertTrue(any(f['action']=='ADD' for f in yes['fills']))
        self.assertFalse(any(f['action']=='ADD' for f in no['fills']))

    def test_reduce_and_add_control(self):
        p,g,m=fixture();r=execute(p,g,replace(m,reduce_floor=3,allow_add=False))
        self.assertTrue(any(f['action']=='REDUCE' for f in r['fills']))
        self.assertFalse(any(f['action']=='ADD' for f in r['fills']))

if __name__=='__main__':unittest.main()
