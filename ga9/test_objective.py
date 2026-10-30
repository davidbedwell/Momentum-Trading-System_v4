import unittest
from dataclasses import replace
import numpy as np
import pandas as pd
from .execution import Panel, Gene, Manager, replay, metrics
from .objective import HorizonMix, fit, predict, labels, benchmark, objective


def fixture(no_edge=False):
    n=220
    close=np.column_stack([100*1.001**np.arange(n),100*.990**np.arange(n)])
    if no_edge:
        close=np.column_stack([100*.999**np.arange(n)]*2)
    opens=np.vstack([close[0],close[:-1]])
    z=np.tile([2.,-2.],(n,1))
    features={k:z.copy() for k in ['trend','momentum','relative_strength','volatility','volume','recursive','breadth']}
    return Panel(pd.bdate_range('2022-01-03',periods=n),['A','B'],opens,close,np.zeros_like(close),
                 np.vstack([np.zeros(2),close[1:]/close[:-1]-1]),features,np.zeros_like(close,dtype=int),np.ones(n),synthetic_benchmark_fixture=True)

class ObjectiveTests(unittest.TestCase):
    def test_relative_edge_deployment_and_abstention(self):
        for no_edge in [False,True]:
            p=fixture(no_edge)
            g=Gene('trend',threshold=-3,hold_sessions=60,add=10,exit_threshold=-10)
            model=fit(p,g,HorizonMix((5,60),(.5,.5)),'2022-07-01')
            signals=predict(p,g,model)
            result=replay(p,[replace(g,threshold=0)],Manager(slots=1),'2022-07-01','2023',True,signals[None],True)
            if no_edge:
                self.assertEqual(result['fills'],[])
            else:
                rel,_=labels(p,5,'2022-07-01')
                self.assertGreater(rel[0,0],0)
                self.assertLess(rel[0,1],0)
                self.assertGreater(signals[150,0],signals[150,1])
                self.assertTrue(result['fills'])
                self.assertEqual({f['ticker'] for f in result['fills']},{'A'})
                self.assertGreater(result['metrics']['final_nav'],100000)

    def test_objective_gain_loss_and_gate(self):
        def r(nav): return dict(metrics=metrics(nav,[],[0]*len(nav),len(nav)))
        passive=r([100000,101000])
        gain,loss,breach=r([100000,102000]),r([100000,99000]),r([91000,150000])
        self.assertGreater(objective(gain,passive),objective(loss,passive))
        self.assertLess(loss['metrics']['excess_pp'],0)
        self.assertGreater(objective(breach,passive),objective(loss,passive))
        boundary=r([92000,100000]); objective(boundary,passive)
        self.assertTrue(boundary['metrics']['feasible'])

    def test_training_cutoff_and_future_invariance(self):
        p=fixture(); g=Gene('trend'); mix=HorizonMix()
        a=fit(p,g,mix,'2022-07-01')
        p.close[130:]*=10
        p.open[130:]*=10
        self.assertEqual(a,fit(p,g,mix,'2022-07-01'))
        for c in a['components']:
            self.assertGreaterEqual(c['horizon'],1)
        self.assertIn(120,mix.sessions)

    def test_listing_sleeve_cash(self):
        p=fixture(); p.symbols[1]='GEV'
        p.open[:50,1]=np.nan; p.close[:50,1]=np.nan
        b=benchmark(p,'2022','2023')
        self.assertAlmostEqual(b['equity'][20]['cash'],50000)
        self.assertEqual(b['equity'][50]['cash'],0)

if __name__=='__main__': unittest.main()

class ControllingRiskAndUniverseTests(unittest.TestCase):
    def test_eight_percent_is_reference_not_gate(self):
        from .risk import DRAWDOWN_REFERENCE, risk_feasible
        self.assertEqual(DRAWDOWN_REFERENCE,.08)
        self.assertTrue(risk_feasible(.25))
        passive={'metrics':dict(max_drawdown=.1,cagr=.1,calmar=1,final_nav=110000)}
        candidate={'metrics':dict(max_drawdown=.15,cagr=.2,calmar=1.33,final_nav=120000)}
        objective(candidate,passive)
        self.assertTrue(candidate['metrics']['success'])

    def test_relative_labels_use_cash_sleeve_for_unlisted_member(self):
        p=fixture();p.close[:50,1]=np.nan;p.open[:50,1]=np.nan
        rel,absolute=labels(p,5,'2023')
        entry=1.0005*1.0001
        passive=((p.open[6,0]/(p.open[1,0]*entry)-1)+0)/2
        self.assertAlmostEqual(rel[0,0],absolute[0,0]-passive)
        # A different evaluated sample MUST yield a different benchmark label.
        p.symbols=['A'];p.open=p.open[:,:1];p.close=p.close[:,:1]
        p.dividends=p.dividends[:,:1]
        single,_=labels(p,5,'2023')
        self.assertNotAlmostEqual(single[0,0],rel[0,0])

    def test_actual_optimizer_prefers_funded_a_and_no_edge_abstains(self):
        from .evolution import search, funded
        for no_edge in [False,True]:
            p=fixture(no_edge)
            c,models,log=search(p,2023,generations=1,population=4,budget=10,horizons=(5,20))
            r=funded(p,c,models,'2022-07-01','2023')
            if no_edge:
                self.assertEqual(r['fills'],[])
            else:
                self.assertTrue(r['fills'])
                self.assertEqual({f['ticker'] for f in r['fills']},{'A'})
                self.assertGreater(log['selection_metrics']['excess_pp'],0)
                self.assertTrue(log['selection_metrics']['feasible'])

    def test_unknown_sector_cap_is_enforced_at_fills(self):
        from .evolution import Candidate, funded
        p=fixture(); g=Gene('trend',weight=.09,add=100,hold_sessions=60)
        mix=HorizonMix((5,), (1.,)); model=fit(p,g,mix,'2022-07-01')
        c=Candidate((g,),Manager(sector_cap=.02),mix)
        r=funded(p,c,[model],'2022-07-01','2023')
        self.assertGreater(r['audit']['sector_rejections'],0)
        self.assertLess(r['metrics']['max_sector_weight'],.025)  # includes subsequent price drift

class PositionOpportunityTests(unittest.TestCase):
    def test_entry_ineligibility_does_not_become_forced_native_exit(self):
        from .evolution import Candidate, funded
        from .objective import holding_predict
        p=fixture();g=Gene('trend',threshold=1.,add=100,hold_sessions=100,exit_threshold=-10)
        mix=HorizonMix((60,),(1.,));model=fit(p,g,mix,'2022-07-01')
        # Entry threshold can be raised while conditional holding forecast stays known.
        strict=replace(g,threshold=3.)
        self.assertTrue(np.isneginf(predict(p,strict,model)[150,0]))
        self.assertGreater(holding_predict(p,strict,model)[150,0],0)
        p.features['trend'][150:160,0]=.8  # loses entry eligibility during an existing holding
        c=Candidate((g,),Manager(slots=1),mix)
        r=funded(p,c,[model],'2022-07-01','2023')
        self.assertGreater(r['audit']['holds'],0)
        self.assertFalse(any(f['reason']=='opportunity_cost' for f in r['fills']))

class HorizonLifecycleTests(unittest.TestCase):
    def test_planned_expiries_follow_frozen_distribution(self):
        from .evolution import Candidate, funded
        p=fixture();g=Gene('trend',add=100,hold_sessions=999,exit_threshold=-10)
        mix=HorizonMix((2,60),(.5,.5));model=fit(p,g,mix,'2022-07-01')
        c=Candidate((g,),Manager(slots=1),mix)
        a=funded(p,c,[model],'2022-07-01','2023')
        b=funded(p,c,[model],'2022-07-01','2023')
        self.assertEqual(a['fills'],b['fills'])
        planned={h['planned_hold_sessions'] for day in a['equity'] for h in day['holdings_detail']}
        self.assertTrue(planned)
        self.assertTrue(planned <= {1,59})
        self.assertNotIn(999,planned)

class DiscriminationTests(unittest.TestCase):
    def test_constant_prediction_serializes_as_null_ic(self):
        import json
        from .objective import discrimination
        p=fixture()
        g=Gene('trend')
        mix=HorizonMix((5,),(1.,))
        model=fit(p,g,mix,'2022-07-01')
        p.symbols=[f'X{k}' for k in range(79)]
        for name in ['open','close','dividends','returns','niche']:
            setattr(p,name,np.tile(getattr(p,name),(1,40))[:,:79])
        p.features={k:np.tile(v,(1,40))[:,:79] for k,v in p.features.items()}
        # Identical forecast bins across a wider cross-section can have tiny
        # floating point std but exactly constant ranks. IC is unavailable.
        model['components'][0]['bins']=[dict(count=100,relative=.00013,cash=.001)]*6
        report=discrimination(p,[g],[model],mix,'2022-07-01','2023')
        json.dumps(report,allow_nan=False)
        self.assertIsNone(report[0][0]['mean_rank_ic'])

class RejectedCandidateTests(unittest.TestCase):
    def test_risk_breached_candidate_is_retained_but_not_selected(self):
        from .evolution import search
        p=fixture()
        # A forecast trained before July cannot anticipate this later close gap.
        p.close[150:,0]*=.1
        p.open[151:,0]*=.1
        candidate,models,log=search(p,2023,generations=1,population=4,budget=10,horizons=(60,))
        self.assertEqual(log['rejected_risk'], [])
        self.assertTrue(all(r['metrics']['max_drawdown']>.08 for r in log['rejected_risk']))
        self.assertNotIn(candidate.id,{r['id'] for r in log['rejected_risk']})
        self.assertTrue(log['selection_metrics']['feasible'])
