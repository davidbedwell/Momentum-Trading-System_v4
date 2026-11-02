"""Regression evidence for the offline repair playbook and bounded restart."""
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch
import numpy as np
from ga9.execution import Manager, Gene, replay
from ga9.exploratory import inputs, model_signal, edge_manager, experiment
from ga9.supervisor import Supervisor, atomic


class Tests(unittest.TestCase):
    def test_absolute_edges_cannot_be_overwhelmed_by_rank_bias(self):
        p,_,_=inputs('synthetic');a,b=378,567
        signal,_=model_signal(p,'momentum',a,20)
        base=Manager(slots=6,reserve=.3,risk_cap=.004,entry_floor=0.)
        def run(m):
            return replay(p,[Gene('momentum',threshold=0)],m,p.dates[a],p.dates[b],
                          detail=True,signal=signal,hold_signal=signal,edge_mode=True,absolute_edges=True)
        neutral=run(base);biased=run(replace(base,niche_bias=(-.4,)*3,specialist_bias=(-.5,)))
        self.assertGreater(neutral['metrics']['fills'],0)
        self.assertEqual(neutral['fills'],biased['fills'])
        for event in biased['events']:
            for row in event['ranked_candidates']:
                self.assertGreater(row['expected_net_edge_per_session'],0)
                self.assertLess(row['expected_net_edge_per_session'],.1)

    def test_adapter_preserves_capital_gates_and_does_not_force_fills(self):
        m=Manager(slots=0,reserve=1.,risk_cap=.004,correlation=.6,sector_cap=.1,
                  entry_floor=.8,niche_bias=(-.4,)*3,specialist_bias=(.5,))
        repaired=edge_manager(m)
        for key in ('slots','reserve','risk_cap','correlation','sector_cap'):
            self.assertEqual(getattr(repaired,key),getattr(m,key))
        p,_,_=inputs('synthetic');signal,_=model_signal(p,'momentum',378,20)
        z=replay(p,[Gene('momentum',threshold=0)],repaired,p.dates[378],p.dates[567],signal=signal,edge_mode=True,absolute_edges=True)
        self.assertEqual(z['metrics']['fills'],0)
        negative=np.full_like(signal,-np.inf)
        z=replay(p,[Gene('momentum',threshold=0)],edge_manager(Manager()),p.dates[378],p.dates[567],signal=negative,edge_mode=True,absolute_edges=True)
        self.assertEqual(z['metrics']['fills'],0)

    def test_repaired_real_experiment_has_fills_and_quarantine(self):
        with tempfile.TemporaryDirectory() as d:
            report=experiment(d,'real',seconds=20,evaluations=4,repair='edge_units_v2')
            self.assertGreater(report['total_fills'],0)
            self.assertGreater(report['positive_forecasts'],0)
            self.assertIsNotNone(report['best_active'])
            self.assertTrue((Path(d)/'best_active.json').exists())
            self.assertEqual(report['llm_spend_usd'],0)
            self.assertFalse(report['final_validation_allowed'])
            symbols=json.loads((Path(d)/'inputs.json').read_text())['symbols']
            self.assertFalse(set(symbols)&{'FB','META','XLNX'})

    def test_unknown_class_halts_without_experiment(self):
        with tempfile.TemporaryDirectory() as d:
            s=Supervisor(Path(d));calls=[]
            def step(name,args,seconds):
                calls.append((name,seconds));s.state['steps'][name]=dict(status='DONE',returncode=0)
                atomic(Path(d)/(name+'.json'),dict(classification='UNKNOWN_ZERO_FILL',action='Inspect eligibility'))
            with patch.object(s,'step',side_effect=step):s.recover_zero('real',Path(d)/'source')
            self.assertEqual(len(calls),1)
            self.assertEqual(s.state['recovery']['real']['outcome'],'BLOCKED')
            s.lock.close()

    def test_interrupted_attempt_only_one_retry_across_restarts(self):
        with tempfile.TemporaryDirectory() as d:
            s=Supervisor(Path(d));calls=[]
            def step(name,args,seconds):
                calls.append(name);s.state['steps'][name]=dict(status='TIMEOUT',returncode=-15)
            with patch.object(s,'step',side_effect=step):s.recover_zero('real',Path(d))
            self.assertEqual(len(calls),2)
            self.assertEqual(len(s.state['recovery']['real']['attempts']),2)
            s.lock.close();s=Supervisor(Path(d))
            with patch.object(s,'step',side_effect=AssertionError('must not rerun')):s.recover_zero('real',Path(d))
            self.assertEqual(s.state['recovery']['real']['outcome'],'BLOCKED');s.lock.close()

    def test_reserved_before_crash_consumes_attempt(self):
        import time
        with tempfile.TemporaryDirectory() as d:
            s=Supervisor(Path(d))
            s.state['recovery']={'real':dict(attempts=[dict(started=time.time(),deadline=time.time()+300)])}
            s.state['steps']['recovery_real_edge_units_v2_0_diagnosis']=dict(status='RUNNING')
            calls=[]
            def step(name,args,seconds):
                calls.append(name);s.state['steps'][name]=dict(status='DONE',returncode=1)
            with patch.object(s,'step',side_effect=step):s.recover_zero('real',Path(d))
            self.assertEqual(calls,['recovery_real_edge_units_v2_1_diagnosis'])
            self.assertEqual(s.state['recovery']['real']['outcome'],'BLOCKED');s.lock.close()

    def test_success_runs_diagnose_tests_and_changed_experiment_once(self):
        with tempfile.TemporaryDirectory() as d:
            s=Supervisor(Path(d));calls=[]
            def step(name,args,seconds):
                calls.append((name,args,seconds));s.state['steps'][name]=dict(status='DONE',returncode=0)
                if name.endswith('diagnosis'):
                    atomic(Path(d)/(name+'.json'),dict(classification='EDGE_UNIT_MISMATCH'))
                if name.endswith('experiment'):
                    folder=Path(d)/name;folder.mkdir()
                    atomic(folder/'report.json',dict(total_fills=5,certified=False))
            with patch.object(s,'step',side_effect=step):s.recover_zero('real',Path(d))
            self.assertEqual(len(calls),3)
            self.assertIn('--repair',calls[-1][1])
            self.assertEqual(s.state['recovery']['real']['outcome'],'RECOVERED')
            self.assertTrue(all(c[2]<=150 for c in calls));s.lock.close()
            s=Supervisor(Path(d))
            with patch.object(s,'step',side_effect=AssertionError('duplicate')):s.recover_zero('real',Path(d))
            self.assertEqual(s.state['exploratory_results']['real']['total_fills'],5);s.lock.close()
