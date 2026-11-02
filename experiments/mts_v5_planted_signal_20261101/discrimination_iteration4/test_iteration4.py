import unittest
import experiment as e
class Contracts(unittest.TestCase):
    def test_gate(self):
        self.assertFalse(e.gate(.005,None,0)[0])
        self.assertFalse(e.gate(0,.005,0)[0])
        self.assertFalse(e.gate(0,None,5)[0])
        self.assertFalse(e.gate(0,0,0,True)[0])
        self.assertTrue(e.gate(0,0,0)[0])
    def test_five_tiers(self):
        for mu,t in zip((-.012,-.004,0,.004,.012),e.TIERS):self.assertEqual(e.infer(mu,.0001,40,40),t)
        self.assertEqual(e.infer(0,.003,40,40),'UNKNOWN')
    def test_provenance_and_future(self):
        days,_,f,_,_=e.generate(17,'reversal')
        x=e.predictors(days,f)
        changed=list(days);changed[128:]=[(d,{}) for d,b in days[128:]]
        self.assertEqual(x[:128],e.predictors(changed,f)[:128])
        a=e.fit(days,x,list(range(9)));self.assertEqual(a,e.fit(changed,x,list(range(9))))
    def test_ledger_lag(self):
        days,_,f,_,_=e.generate(18,'reversal');states,ledger,alarms=e.predict(days,f)
        self.assertEqual(len(ledger),6000)
        for z in ledger:
            self.assertEqual(z['execution_index'],z['index']+1)
            self.assertLessEqual(z['feature_latest_index'],z['index'])
            if z['available_index'] is not None:self.assertEqual(z['available_index'],z['index']+3)
        self.assertTrue(all(a['index']>=126 for a in alarms))
        self.assertTrue(all(a['last_signal']<=a['index']-3 for a in alarms))
    def test_reversal_veto_lag_constructed(self):
        # A post126 shock first becomes visible at129; three matured dates at131.
        alarm=None
        for now in range(126,140):
            available=[i for i in range(126,now-2)]
            recent=-.02 if len(available)>=3 else None
            if not e.gate(0,recent,0)[0]:alarm=now;break
        self.assertEqual(alarm,131)
    def test_entire_candidate_risk(self):
        ev=e.r.ScaleEvidence(50,2,True,.01,True,True,False)
        for gap in (.03,.24):
            bank=e.k.Replay(cash=95000,shares={'A':50},**e.s.COSTS)
            bank.pending=[e.k.Signal('A','GA7','a',.20,1,ev,.02,gap,.9)]
            bank.day('2030-01-02',{'A':e.k.Bar(100,100)})
            self.assertLessEqual(bank.risk_audit[-1]['modeled_equity_loss'],.02+1e-12)
            self.assertAlmostEqual(bank.shares['A']*100/100000,min(.20,.02/(gap+e.s.ROUND_TRIP)))
    def test_tplus1(self):
        bank=e.k.Replay(cash=0,shares={'A':1000},high_water=100000,settlement_sessions=1,**e.s.COSTS)
        bars={t:e.k.Bar(100,100) for t in ('A','B')}
        bank.pending=[e.k.Signal('A','GA7','a',0),e.k.Signal('B','GA7','b',.1,1,None,.02,.03)]
        bank.day('2030-01-02',bars);self.assertFalse(bank.shares);self.assertEqual(bank.cash,0);self.assertTrue(bank.unsettled)
        bank.pending=[e.k.Signal('B','GA7','b',.1,1,None,.02,.03)]
        bank.day('2030-01-03',bars);self.assertIn('B',bank.shares)

    def test_cash_cost_and_mdd_latch(self):
        bank=e.k.Replay(cash=100000,**e.s.COSTS)
        bank.pending=[e.k.Signal('A','GA7','a',.1,1,None,.02,.03)]
        bank.day('2030-01-02',{'A':e.k.Bar(100,100)})
        self.assertGreaterEqual(bank.cash,0)
        self.assertLess(bank.nav[-1][1],100000)
        self.assertGreater(bank.ledger[-1][5],0)
        bank.monitor(70000);self.assertTrue(bank.admission_halted)
        bank.monitor(110000);self.assertTrue(bank.admission_halted)
    def test_gate_controls_scaling_confirmation(self):
        days,_,_,p,_=e.generate(19,'learnable')
        ids=[list(range(24)) for _ in range(252)]
        cells=[[dict(mean=.012,label='UNKNOWN',radius=.001) for j in range(24)] for i in range(252)]
        cb=e.b.callbacks(ids,p,cells,'tier15',days)
        self.assertLess(cb['conditional_ev'](None,e.s.TICKERS[0],e.s.DATES[126]),0)
        cells[126][0]['label']='GREAT'
        self.assertGreater(cb['conditional_ev'](None,e.s.TICKERS[0],e.s.DATES[126]),0)
