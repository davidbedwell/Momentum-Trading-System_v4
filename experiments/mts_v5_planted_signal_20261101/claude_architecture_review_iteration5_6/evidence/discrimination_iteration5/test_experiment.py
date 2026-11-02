import copy,unittest
import experiment as e
class EngineeringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.p,cls.f,cls.truth=e.generate(77,'learnable')
    def test_bands_and_abstain(self):
        for mu,t in zip(e.MU,e.TIERS):self.assertEqual(e.label(mu,.0001,200,200),t)
        self.assertEqual(e.label(.004,.003,400,200),'UNKNOWN')
        self.assertEqual(e.label(.012,.001,99,200),'UNKNOWN')
    def test_disjoint_and_calibration_not_point_fit(self):
        self.assertLess(max(e.FIT)+2,min(e.CAL));self.assertLess(max(e.CAL)+2,e.START)
        m=e.fit(self.p,self.f);p=copy.deepcopy(self.p)
        # All calibration execution prices changed, keeping fit and its price predictors intact.
        for i in range(min(e.CAL)+1,max(e.CAL)+3):p[i]=[x*(1+.0001*(i-min(e.CAL))) for x in p[i]]
        changed=e.fit(p,self.f)
        for a,b in zip(m,changed):
            for key in ['mean','slope','center','threshold']:self.assertEqual(a[key],b[key])
        self.assertTrue(any(a['radius']!=b['radius'] for a,b in zip(m,changed)))
        self.assertTrue(all(len(a['train_dates'])<=400 and len(a['cal_dates'])<=200 for a in m))
    def test_test_outcomes_not_fit_and_future_not_prediction(self):
        states,m,_=e.predict(self.p,self.f);p=copy.deepcopy(self.p)
        for i in range(e.START+12,e.N):p[i]=[x*.9 for x in p[i]]
        ss,mm,_=e.predict(p,self.f)
        self.assertEqual(m,mm);self.assertEqual(states['candidate'][:10],ss['candidate'][:10])
    def test_gate_has_coverage_without_price_only(self):
        ss,m,a=e.predict(self.p,self.f)
        self.assertGreater(sum(z['label']!='UNKNOWN' for row in ss['candidate'] for z in row),0)
    def test_monitor_maturity_and_multiplicity(self):
        m=e.fit(self.p,self.f)
        self.assertEqual(e.monitor(self.p,self.f,m,e.START+21),[])
        p,f,_=e.generate(88,'reversal');_,_,alarms=e.predict(p,f)
        for a in alarms:self.assertLessEqual(a['last_signal']+3,a['index']);self.assertGreater(a['threshold'],.01)
    def test_ledger_cash_risk_horizon_costs(self):
        ss,_,_=e.predict(self.p,self.f);metric,trades,daily=e.replay(self.p,ss['candidate'],scale=1.5)
        self.assertLessEqual(metric['max_modeled_risk'],.02+1e-12)
        self.assertTrue(all(d['cash']>=0 for d in daily));self.assertGreater(metric['costs'],0)
        for t in trades:
            self.assertEqual(t['exit_index'],t['entry_index']+1)
            self.assertAlmostEqual(t['net'],e.observed(self.p,t['signal'],t['j']))
        cash,tt,dd=e.replay(self.p,ss['candidate'],'cash');self.assertEqual(cash['total_return'],0);self.assertEqual(tt,[])
    def test_gap_audit_is_not_realized_cap(self):
        p=copy.deepcopy(self.p)
        for i in range(e.START+2,e.N):p[i]=[x*.5 for x in p[i]]
        ss=[[dict(mean=.012,label='GREAT') for _ in range(24)] for i in range(126)]
        metric,_,_=e.replay(p,ss)
        self.assertGreater(metric['gap_loss_exceedances'],0)
    def test_pit_rejects_missing_future_and_accepts_provenance(self):
        with self.assertRaises(ValueError):e.validate_pit([{}])
        row=dict(asset='X',feature='f',value=1,event_time='2020-01-01T00:00:00+00:00',release_time='2020-01-02T00:00:00+00:00',available_time='2020-01-02T01:00:00+00:00',decision_time='2020-01-03T00:00:00+00:00',revision_id='r0',source_uri='local:fixture',source_sha256='a'*64,vintage_id='v0')
        self.assertEqual(e.validate_pit([row]),[row]);row['available_time']='2021-01-01T00:00:00+00:00'
        with self.assertRaises(ValueError):e.validate_pit([row])
    def test_original_baseline_integration(self):
        ss,alarms=e.baseline(self.p,self.f);self.assertEqual(len(ss),126);self.assertEqual(len(ss[0]),24)
if __name__=='__main__':unittest.main()
