import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from ga9.exploratory import inputs, precursor, model_signal, comparison, experiment
from ga9.nasdaq_archive import require_replay_inputs
from ga9.exploratory_exclusions import exclusions

class Tests(unittest.TestCase):
    def test_lineage_exclusion_configuration(self):
        records=exclusions(map(Path, ['FB.parquet','META.parquet','meta.parquet','XLNX.parquet','AMD.parquet','AAL.parquet']))
        self.assertEqual([r['symbol_count'] for r in records],[3,1])
        self.assertTrue(all(r['reason'] for r in records))
        self.assertEqual([r['symbol_count'] for r in exclusions([])],[0,0])

    def test_lineages_cannot_enter_real_training_or_replay(self):
        baseline,_,_=inputs('real')
        from ga9 import exploratory
        original=Path.glob
        def with_aliases(path, pattern):
            found=list(original(path,pattern))
            if path == exploratory.ARCHIVE/'price_raw':
                found += [path/f'{s}.parquet' for s in ('META','meta','FB','XLNX')
                          if path/f'{s}.parquet' not in found]
            return iter(found)
        # Missing fake alias files must never be read, even if ordinary blocking
        # has not recognized an alias. Other symbols and sessions stay identical.
        ordinary=exploratory.blocked_symbols(exploratory.ARCHIVE)
        with patch.object(Path,'glob',with_aliases), patch.object(exploratory,'blocked_symbols',return_value=ordinary-{'FB','META','XLNX'}):
            panel,meta,_=inputs('real')
        self.assertEqual(panel.symbols,baseline.symbols)
        np.testing.assert_array_equal(panel.dates,baseline.dates)
        np.testing.assert_array_equal(panel.close,baseline.close)
        self.assertIn('AMD',panel.symbols)
        self.assertEqual(meta['excluded_lineage_count'],2)
        self.assertEqual(meta['excluded_lineage_symbol_count'],4)
        self.assertEqual([r['symbol_count'] for r in meta['lineage_exclusions']],[3,1])

    def test_forward_exclusion_and_label_purge(self):
        p,_,_=inputs('synthetic')
        self.assertEqual(len(p.dates),756)
        y,e,f=precursor(p,378,40)
        self.assertTrue(np.isnan(y[337:]).all())
        before,model=model_signal(p,'momentum',378,40)
        p.open[378:]*=10;p.close[378:]*=10
        after,_=model_signal(p,'momentum',378,40)
        np.testing.assert_array_equal(before[:378],after[:378])
        self.assertTrue(any(r['failed_lookalikes'] for r in model['bins']))

    def test_missing_comparators_never_success(self):
        p,_,_=inputs('synthetic')
        c=comparison({},p,378,567,dict(cagr=10,max_drawdown=0))
        self.assertFalse(c['target_met'])
        self.assertEqual(c['benchmarks']['SPY']['status'],'MISSING')
        with self.assertRaises(ValueError):require_replay_inputs({'blockers':['PIT']})

    def test_real_development_scope(self):
        p,meta,_=inputs('real')
        self.assertLess(str(p.dates[-1].date()),'2025-01-01')
        self.assertGreaterEqual(str(p.dates[0].date()),'2022-01-01')
        self.assertGreater(len(meta['sources']),0)

    def test_bounded_replay_report(self):
        with tempfile.TemporaryDirectory() as d:
            r=experiment(d,'synthetic',seconds=15,evaluations=1)
            self.assertEqual(r['evaluations'],1)
            self.assertFalse(r['certified'])
            self.assertFalse(r['promotion_allowed'])
            self.assertEqual(len(r['best']['folds']),2)
            self.assertTrue((Path(d)/'best.json').exists())

if __name__=='__main__':unittest.main()

class SupervisorModeTests(unittest.TestCase):
    def test_exploratory_restart_does_not_rerun_completed_work(self):
        import json
        from ga9.supervisor import Supervisor, atomic
        with tempfile.TemporaryDirectory() as d:
            s=Supervisor(Path(d))
            for kind in ('synthetic','real'):
                name=f'exploratory_{kind}_v1_retry0'
                s.state['steps'][name]={'status':'DONE','returncode':0}
                folder=Path(d)/name;folder.mkdir()
                atomic(folder/'report.json',{'certified':False,'target_met':False})
            s.exploratory(once=True)
            self.assertEqual(len(s.state['steps']),2)
            self.assertEqual(s.state['status'],'EXPLORATORY_HALTED')
            self.assertFalse(s.state['promotion_allowed'])
            self.assertFalse(s.state['final_validation_allowed'])
            s.lock.close()
