import unittest,copy,math
import engine as z
class Tests(unittest.TestCase):
 def setUp(self):
  z.configure();self.p,self.f,_=z.x.generate(1234,'learnable');self.m=z.fit(self.p,self.f,'B');z.CUSUM.thresholds=[.1,.1]
 def test_classifier_matches_frozen(self):
  ss,m,events=z.e.predict(self.p,self.f);self.assertEqual(z.states(self.p,self.f,self.m),ss['candidate'])
 def test_c_matches_claude_equation(self):
  g=z.C_ablation(self.p,self.f,self.m);n=z.x.START
  expected={}
  for w in (2,4,8):
   vs=[z.contrast(self.p,self.f,d) for d in range(n-2-w,n-2)]
   if any(v is None for v in vs):expected[w]=0.;continue
   delta=z.e.mean(vs)-g.mu;sigma=.018/math.sqrt(w);lam=max(0,min(-delta/sigma**2,1/sigma));expected[w]=lam*(-delta)-.5*(lam*sigma)**2
  g(n,[],[]);self.assertEqual(g.logs,expected)
  g.mu=1.
  for n in range(z.x.START+1,z.x.START+10):g(n,[],[])
  self.assertTrue(g.latched)
 def test_pit_all_detectors(self):
  n=z.x.START+8;p=copy.deepcopy(self.p);f=copy.deepcopy(self.f)
  # Last permitted outcome d=n-3 exits at d+2=n-1; mutate price n onward.
  for i in range(n,len(p)):p[i]=[v*.2 for v in p[i]]
  for i in range(n+1,len(f)):f[i]=[4-c for c in f[i]]
  for cls in (z.B,z.C_ablation,z.CUSUM,z.x.Gate):
   a=cls(self.p,self.f,self.m);b=cls(p,f,self.m)
   for now in range(z.x.START,n+1):a(now,[],[]);b(now,[],[])
   self.assertEqual(a.trace,b.trace)
 def test_no_duplicate_dates(self):
  for cls in (z.B,z.CUSUM):
   g=cls(self.p,self.f,self.m)
   for n in range(z.x.START,z.x.END):g(n,[],[])
   self.assertEqual(len(g.seen),len(set(g.seen)));self.assertTrue(all(d>=z.x.START for d in g.seen))
 def test_radius_both_branches(self):
  for c,m in enumerate(z.fit_v3(self.p,self.f)):
   tr=[v for _,v in z.e.dates(self.p,self.f,z.e.FIT,c)];ca=[v for _,v in z.e.dates(self.p,self.f,z.e.CAL,c)]
   bias=abs(z.e.mean(ca)-z.e.mean(tr));a=z.e.se(tr);b=z.e.se(ca)
   expected=2.576*math.sqrt(a*a+b*b) if bias<b else max(2.576*a,bias+2.576*b)
   self.assertAlmostEqual(m['radius'],expected)
if __name__=='__main__':unittest.main()
