import unittest,importlib.util,sys
from pathlib import Path
from study import cycle_risk
p=Path('/opt/mts/ga7-deploy/ga7_audit_v2/reports/ga7_final_518/ga6_ga7_common_execution_reference_v1.py')
s=importlib.util.spec_from_file_location('reference',p);e=importlib.util.module_from_spec(s);sys.modules[s.name]=e;s.loader.exec_module(e)
class Tests(unittest.TestCase):
 def test_partial_accounting(self):
  events=[dict(session=0,action='BUY',qty=10,price=10,cost=100.1),dict(session=1,action='BUY',qty=5,price=9,cost=45.045),dict(session=2,action='SELL',qty=5,price=11,net=54.945,reason='REDUCE'),dict(session=3,action='SELL',qty=10,price=8,net=79.92,reason='INTRADAY_STOP_ASSUMED')]
  z=cycle_risk(events,{0:(10,9,10,0),1:(9,8,9,.1),2:(11,10,11,0),3:(9,7,8,0)})
  self.assertAlmostEqual(z['pnl'],54.945+79.92+1-145.145);self.assertEqual((z['adds'],z['reductions'],z['stop_fills']),(1,1,1));self.assertLessEqual(z['exposed_state_low'],z['post_fill_low']);self.assertLessEqual(z['post_fill_low'],z['fill_marks'])
 def run_synthetic(self,scale=1,future=10):
  # Dynamic toy decisions prove executor plumbing only. These are not GA rules.
  days=[e.Day(str(i),{t:e.Bar(10,11,9.5,future if i==5 else 10,sector=t) for t in ['A','B','C']}) for i in range(6)]
  def decide(i,day,h):
   if i==0:return [e.Order(i,'A','ENTER',weight=.8*scale,stop_pct=.04,earnings_clear=True),e.Order(i,'B','ENTER',weight=.8*scale,stop_pct=.04,earnings_clear=True)]
   if i==1:return [e.Order(i,'A','EXIT')]
   # Freed settled capital competes for a fresh, dynamically generated C order.
   if i==3:return [e.Order(i,'C','ENTER',weight=.8*scale,stop_pct=.04,earnings_clear=True)]
   return []
  return e.run(days,config=e.Config(symbol_cap=1,per_position_risk_cap=1,aggregate_risk_cap=1,sector_position_cap=3),initial_cash=1000,decision_fn=decide)
 def test_cash_redeployment(self):
  r=self.run_synthetic();buys=[x for x in r.events if x['action']=='BUY'];self.assertEqual({x['ticker'] for x in buys},{'A','B','C'});self.assertTrue(any(x['action']=='SETTLE' for x in r.events));self.assertGreaterEqual(r.final_cash,0);self.assertEqual(len(r.nav),6)
 def test_scaled_sizing_changes_competition(self):
  a=self.run_synthetic();b=self.run_synthetic(.5);self.assertNotEqual([x['qty'] for x in a.events if x['action']=='BUY'],[x['qty'] for x in b.events if x['action']=='BUY'])
 def test_future_prefix(self):
  # Valid alternative future OHLC, changed only last close.
  a=self.run_synthetic(future=10);b=self.run_synthetic(future=10.5);self.assertEqual(a.nav[:-1],b.nav[:-1]);self.assertEqual(a.events,b.events)
if __name__=='__main__':unittest.main()
