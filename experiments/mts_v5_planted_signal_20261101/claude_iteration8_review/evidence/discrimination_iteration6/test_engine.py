import copy,unittest
import engine as x
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.p,cls.f,_=x.generate(9182,'learnable');cls.ss,cls.models,_=x.e.predict(cls.p,cls.f)
 def test_future_invariance_and_maturity(self):
  now=x.START+8;p=copy.deepcopy(self.p);f=copy.deepcopy(self.f)
  for i in range(now,len(p)):p[i]=[v*.3 for v in p[i]]
  for i in range(now+1,len(f)):f[i]=[4-c for c in f[i]]
  a=x.Gate(self.p,self.f,self.models);b=x.Gate(p,f,self.models)
  self.assertEqual(a(now,self.ss['candidate'][8],[]),b(now,self.ss['candidate'][8],[]))
  self.assertEqual(a.trace,b.trace)
 def test_no_outcome_before_available(self):
  a=x.Gate(self.p,self.f,self.models);now=x.START+3
  t=dict(signal=now-2,net=-1,debit=100,j=0)
  a(now,self.ss['candidate'][3],[t]);self.assertEqual(a.trace[-1]['matured_fills'],0)
 def test_gating_and_null(self):
  a=x.Gate(self.p,self.f,self.models);a.latched=True
  self.assertTrue(all(z['label']=='UNKNOWN' for z in a(x.START,self.ss['candidate'][0],[])))
  p,f,_=x.generate(9182,'null');ss,_,_=x.e.predict(p,f)
  self.assertTrue(all(z['label']=='UNKNOWN' for row in ss['candidate'] for z in row))
 def test_stable_false_alarm_probe(self):
  a=x.Gate(self.p,self.f,self.models)
  for k,now in enumerate(range(x.START,x.END)):a(now,self.ss['candidate'][k],[])
  self.assertEqual(a.events,[])
 def test_accounting_cash_cost_risk_and_gap_three_replays(self):
  m,ts,ds=x.replay(self.p,copy.deepcopy(self.ss['candidate']))
  self.assertGreater(m['costs'],0);self.assertLessEqual(m['max_modeled_risk'],.02)
  self.assertTrue(all(d['cash']>=-1e-8 for d in ds))
  self.assertAlmostEqual(m['final_nav']-100000,sum(t['debit']*t['net'] for t in ts),places=7)
  for t in ts:
   self.assertEqual(t['exit_index'],t['entry_index']+1)
   self.assertAlmostEqual(t['net'],x.e.observed(self.p,t['signal'],t['j']))
  m,ts,_=x.replay(self.p,self.ss['candidate'],'cash');self.assertEqual(m['total_return'],0);self.assertEqual(m['costs'],0);self.assertEqual(ts,[])
  p=copy.deepcopy(self.p)
  for i in range(x.START+2,len(p)):p[i]=[v*.5 for v in p[i]]
  ss=[[dict(mean=.012,label='GREAT') for j in range(24)] for k in range(126)]
  m,_,_=x.replay(p,ss);self.assertGreater(m['gap_loss_exceedances'],0)
 def test_original_dgp_identity_and_uninformative_breadth(self):
  p,f,t=x.generate(3,'reversal');a,b,c=x.e.generate(3,'reversal');self.assertEqual((p,f,t),(a,b,c))
  q,_,_=x.generate(3,'learnable');self.assertEqual(p,q)
  r,_,_=x.generate(3,'random_reversal',650);self.assertEqual(p,r)
if __name__=='__main__':unittest.main()
