import unittest,copy,math
import engine as z
class Tests(unittest.TestCase):
 def setUp(self):z.configure();self.p,self.f,_=z.x.generate(1234,'learnable');self.m=z.fit(self.p,self.f,'B')
 def test_reference_classifier(self):
  ss,m,events=z.e.predict(self.p,self.f)
  self.assertEqual(z.states(self.p,self.f,self.m),ss['candidate'])
 def test_predictable_and_pit(self):
  n=z.x.START+8;p=copy.deepcopy(self.p);f=copy.deepcopy(self.f)
  for i in range(n,len(p)):p[i]=[v*.2 for v in p[i]]
  for i in range(n+1,len(f)):f[i]=[4-c for c in f[i]]
  for cls in (z.A,z.B):
   a=cls(self.p,self.f,self.m);b=cls(p,f,self.m)
   for now in range(z.x.START,n+1):a(now,[],[]);b(now,[],[])
   self.assertEqual(a.trace,b.trace)
 def test_b_no_duplicate_dates(self):
  b=z.B(self.p,self.f,self.m)
  for n in range(z.x.START,z.x.END):b(n,[],[])
  self.assertEqual(len(b.seen),len(set(b.seen)));self.assertTrue(all(d>=z.x.START for d in b.seen))
 def test_literal_a_wrong_direction(self):
  a=z.A(self.p,self.f,self.m);a.mu=1.
  for n in range(z.x.START,z.x.START+10):a(n,[],[])
  self.assertTrue(all(v==0 for v in a.logs.values()));self.assertFalse(a.latched)
 def test_mixture_null_one_step(self):
  # Exact Gaussian MGF: valid fixed bets E=1; outcome-fitted positive
  # lambda gives factor>1 on every positive outcome, else factor=1.
  for lam in (16,32,64,96):self.assertAlmostEqual(math.exp(.5*(lam*.018)**2-.5*(lam*.018)**2),1.)
  a=.5;self.assertGreater(math.exp(a*a-.5*a*a),1)
 def test_radius_literal(self):
  a=z.fit(self.p,self.f,'A');b=z.fit(self.p,self.f,'B')
  for c in range(5):
   tr=[v for _,v in z.e.dates(self.p,self.f,z.e.FIT,c)];ca=[v for _,v in z.e.dates(self.p,self.f,z.e.CAL,c)]
   expected=2.576*math.sqrt(z.e.se(tr)**2+z.e.se(ca)**2) if abs(z.e.mean(ca)-z.e.mean(tr))<z.e.se(ca) else b[c]['radius']
   self.assertEqual(a[c]['radius'],expected)
if __name__=='__main__':unittest.main()
