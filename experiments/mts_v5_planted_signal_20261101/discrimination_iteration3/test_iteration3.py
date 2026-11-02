"""Contract tests authored before implementation and portfolio execution."""
import unittest
import experiment as e

class Contracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.days,cls.coarse,cls.f,cls.p,_=e.generate(17,'reversal')
        cls.states,cls.ledger,cls.alarms=e.predict(cls.days,cls.f)
    def test_maturation_all_eligible(self):
        self.assertEqual(len(self.ledger),6000)
        for z in self.ledger:
            self.assertEqual(z['execution_index'],z['index']+1)
            self.assertEqual(z['maturity_index'],z['index']+2)
            if z['available_index'] is not None:self.assertGreater(z['available_index'],z['maturity_index'])
        self.assertEqual(sum(z['realized_net'] is None for z in self.ledger),24)
    def test_pit_future_prices(self):
        days=list(self.days);days[128:]=[(d,{}) for d,b in days[128:]]
        states,ledger,_=e.predict(days,self.f)
        self.assertEqual(states[:129],self.states[:129])
        self.assertTrue(any(z['missingness']=='MISSING' for z in ledger))
    def test_future_features(self):
        f=[list(v) for v in self.f];f[128:]=[[0]*24 for _ in f[128:]]
        states,_,_=e.predict(self.days,f)
        self.assertEqual(states[:129],self.states[:129])
    def test_decision_api_no_truth_or_forecasts(self):
        import inspect
        self.assertEqual(list(inspect.signature(e.predict).parameters),['days','features'])
    def test_absolute_unknown(self):
        self.assertEqual(e.infer(0,.001,40,20),'AVERAGE')
        self.assertEqual(e.infer(0,.003,40,20),'UNKNOWN')
        self.assertEqual(e.infer(.01,.001,19,40),'UNKNOWN')
        self.assertTrue(all(c['label']=='UNKNOWN' for c in self.states[20]))
    def test_drift_after_maturation(self):
        hit=[a for a in self.alarms if a['index']>=126]
        self.assertTrue(hit)
        self.assertGreaterEqual(hit[0]['index'],129)
        self.assertTrue(all(c['label']=='UNKNOWN' for c in self.states[hit[0]['index']]))
    def test_reliability_is_causal(self):
        for i,cells in enumerate(self.states):
            for c in cells:
                self.assertLess(c['latest_outcome_signal'],i-2)
                self.assertGreaterEqual(c['radius'],0)
                self.assertTrue(0<=c['reliability']<=1)
    def test_null_abstention(self):
        days,_,f,_,_=e.generate(18,'null');states,_,_=e.predict(days,f)
        self.assertTrue(all(c['label']=='UNKNOWN' for cells in states[:30] for c in cells))
    def test_cost(self):
        self.assertAlmostEqual(self.ledger[0]['realized_net'],e.observed(self.days,0,0))
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

    def test_independent_calibration_mean_frozen(self):
        before,_=e.fit(self.days,self.f)
        days=list(self.days)
        for i in range(81,124):
            d,bars=days[i];days[i]=(d,{t:e.k.Bar(v.open*1.001,v.close*1.001) for t,v in bars.items()})
        after,_=e.fit(days,self.f)
        self.assertEqual([c['mean'] for c in before],[c['mean'] for c in after])
    def test_holdout_never_fits(self):
        days=list(self.days)
        days[126:]=[(d,{t:e.k.Bar(v.open*2,v.close*2) for t,v in bars.items()}) for d,bars in days[126:]]
        self.assertEqual(e.fit(days,self.f),e.fit(self.days,self.f))
    def test_posterior_and_all_thresholds(self):
        cells,_=e.fit(self.days,self.f)
        for c in cells:
            self.assertAlmostEqual(sum(c['posterior']),1.)
            if c['label']!='UNKNOWN':
                self.assertEqual(e.tier(c['mean']-c['radius']),c['label'])
                self.assertEqual(e.tier(c['mean']+c['radius']),c['label'])
                self.assertGreaterEqual(max(c['posterior']),.95)
        for mu,t in zip((-.012,-.004,0.,.004,.012),e.TIERS):self.assertEqual(e.infer(mu,.0001,40,40),t)
    def test_date_correlation_blocks(self):
        _,_,n=e.block_stats([(i,.001*i) for i in range(40)])
        self.assertEqual(n,8)
    def test_cash_and_cost_accounting(self):
        bank=e.k.Replay(cash=100000,**e.s.COSTS)
        bank.pending=[e.k.Signal('A','GA7','a',.1,1,None,.02,.03)]
        bank.day('2030-01-02',{'A':e.k.Bar(100,100)})
        self.assertGreaterEqual(bank.cash,0.)
        self.assertLess(bank.nav[-1][1],100000)
        self.assertGreater(bank.ledger[-1][5],0.)
