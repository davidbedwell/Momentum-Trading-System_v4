"""Regression tests for the latest market-primary/full-universe-secondary override."""
from dataclasses import FrozenInstanceError, replace
import json
from pathlib import Path
import tempfile
import unittest
import numpy as np
import pandas as pd
from .benchmarks import BenchmarkPolicy, SECONDARY, attach_primary, selection_benchmark
from .execution import Gene, Manager, load_panel
from .objective import labels, fit, HorizonMix, predict, objective, benchmark
from .test_objective import fixture
from .run import main
from .verify import verify


def etf(p, symbol, growth):
    c=(100*growth**np.arange(len(p.dates)))[:,None]
    return replace(p,symbols=[symbol],close=c,open=np.vstack([c[0],c[:-1]]),
                   dividends=np.zeros_like(c),primary_benchmark=None)


def frame(symbol,dates,growth):
    close=100*growth**np.arange(len(dates))
    opens=np.r_[close[0],close[:-1]]
    return pd.DataFrame(dict(date=dates,ticker=symbol,open=opens,close=close,
                             high=np.maximum(opens,close)*1.001,low=np.minimum(opens,close)*.999,
                             adj_close=close,volume=100000,dividends=0.,stock_splits=0.))

class BenchmarkOverrideTests(unittest.TestCase):
    def test_profile_is_frozen_and_primary_is_not_chosen_by_returns(self):
        self.assertEqual(BenchmarkPolicy('nasdaq').primary,'QQQ')
        policy=BenchmarkPolicy('broad_us')
        self.assertEqual(policy.primary,'SPY')
        self.assertEqual(policy.record()['secondary'],SECONDARY)
        with self.assertRaises(FrozenInstanceError):
            policy.universe_profile='nasdaq'
        with self.assertRaises(ValueError):
            BenchmarkPolicy('auto_best_return')

    def test_primary_controls_labels_and_fitness_not_secondary(self):
        p=fixture(); ref=etf(p,'SPY',1.002)
        p=replace(p,primary_benchmark=ref)
        rel,absolute=labels(p,5,'2022-07-01')
        passive=ref.open[6,0]/(ref.open[1,0]*1.0005*1.0001)-1
        self.assertAlmostEqual(rel[0,0],absolute[0,0]-passive)
        # Adding an unselected poor stock cannot improve market-relative labels.
        other=replace(p,close=np.c_[p.close,np.full(len(p.dates),1.)],
                      open=np.c_[p.open,np.full(len(p.dates),1.)],
                      dividends=np.c_[p.dividends,np.zeros(len(p.dates))])
        rel2,_=labels(other,5,'2022-07-01')
        np.testing.assert_allclose(rel[:,0],rel2[:,0],equal_nan=True)
        market=selection_benchmark(p,'2022-07-01','2023')
        strategy=dict(metrics=dict(cagr=.1,final_nav=110000,max_drawdown=.079,calmar=1.))
        objective(strategy,market)
        self.assertEqual(strategy['metrics']['primary_benchmark'],'SPY')
        self.assertLess(strategy['metrics']['excess_pp'],0)
        self.assertFalse(strategy['metrics']['success'])
        strategy['metrics']['cagr']=2.;strategy['metrics']['max_drawdown']=.080001
        objective(strategy,market)
        self.assertFalse(strategy['metrics']['feasible'])

    def test_primary_dividend_and_costs_match_window_and_forward_account(self):
        p=fixture();ref=etf(p,'QQQ',1.001);ref.dividends[3,0]=2
        p=replace(p,primary_benchmark=ref)
        rel,absolute=labels(p,5,'2022-07-01')
        passive=(ref.open[6,0]+2)/(ref.open[1,0]*1.0005*1.0001)-1
        self.assertAlmostEqual(absolute[0,0]-rel[0,0],passive)
        buyhold=selection_benchmark(p,'2022','2023')
        self.assertAlmostEqual(buyhold['fills'][0]['price'],ref.open[1,0]*1.0005)
        self.assertGreater(buyhold['equity'][3]['unsettled'],0)

    def test_no_switching_frozen_model_or_future_label_leak(self):
        p=fixture();p=replace(p,primary_benchmark=etf(p,'SPY',1.001))
        g=Gene('trend');mix=HorizonMix((5,),(1.,))
        m=fit(p,g,mix,'2022-07-01')
        p.primary_benchmark.open[140:]*=10
        self.assertEqual(m,fit(p,g,mix,'2022-07-01'))
        switched=replace(p,primary_benchmark=etf(p,'QQQ',1.001))
        with self.assertRaisesRegex(ValueError,'switching'):
            predict(switched,g,m)

    def test_missing_wrong_and_incomplete_etf_fail_without_fallback(self):
        p=fixture()
        with self.assertRaisesRegex(FileNotFoundError,'QQQ requires'):
            attach_primary(p,None,BenchmarkPolicy('nasdaq'),'2023')
        with tempfile.TemporaryDirectory() as root:
            path=Path(root)/'mixed.parquet'
            d=frame('SPY',p.dates,1.001);d.to_parquet(path)
            with self.assertRaisesRegex(ValueError,'QQQ is absent'):
                attach_primary(p,path,BenchmarkPolicy('nasdaq'),'2023')
            d=d.drop(d.index[10]);d.to_parquet(path)
            with self.assertRaisesRegex(ValueError,'missing strategy sessions'):
                attach_primary(p,path,BenchmarkPolicy('broad_us'),'2023')

    def test_runner_freezes_primary_and_complete_universe_for_daily_screen(self):
        # Full chronological orchestration with explicitly synthetic OHLC/dividends.
        dates=pd.bdate_range('2022-01-03','2025-12-31')
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            data=root/'stocks.parquet';refs=root/'etfs.parquet'
            pd.concat([frame('A',dates,1.0002),frame('B',dates,.9998),
                       frame('C',dates,1.0001)]).to_parquet(data)
            pd.concat([frame('SPY',dates,1.0003),frame('QQQ',dates,1.0005)]).to_parquet(refs)
            for profile,expected in [('broad_us','SPY'),('nasdaq','QQQ')]:
                out=main(['--data',str(data),'--benchmark-data',str(refs),'--universe-profile',profile,
                          '--output',str(root/profile),'--generations','1',
                          '--population','4','--budget','10','--horizons','5'])
                self.assertTrue(verify(out)['verified'])
                manifest=json.loads((out/'manifest.json').read_text())
                self.assertEqual(manifest['benchmark'],expected)
                self.assertEqual(manifest['sample'],['A','B','C'])
                self.assertEqual(manifest['universe'],['A','B','C'])
                for year in [2023,2024,2025]:
                    fold=out/f'fold_{year}'
                    frozen=json.loads((fold/'frozen.json').read_text())
                    self.assertEqual(frozen['benchmark'],expected)
                    self.assertEqual(frozen['benchmark_policy'],manifest['benchmark_policy'])
                    primary=json.loads((fold/'benchmark.json').read_text())
                    secondary=json.loads((fold/'secondary_full_universe.json').read_text())
                    self.assertEqual(primary['benchmark_symbols'],[expected])
                    self.assertEqual(secondary['benchmark_symbols'],['A','B','C'])
                    result=json.loads((fold/'forward_frozen.json').read_text())['metrics']
                    self.assertAlmostEqual(result['excess_pp'],100*(result['cagr']-primary['metrics']['cagr']))
                    self.assertAlmostEqual(result['secondary_excess_pp'],100*(result['cagr']-secondary['metrics']['cagr']))
                text=(out/'report.md').read_text()
                self.assertIn(f'Primary benchmark: {expected}',text)
                self.assertIn('complete 3-stock PIT research universe',text)


class CompleteUniverseTests(unittest.TestCase):
    def test_secondary_cannot_be_reduced_to_selected_stocks(self):
        dates=pd.bdate_range('2022-01-03',periods=5)
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);data=root/'stocks.parquet';subset=root/'selected.parquet'
            a=frame('A',dates,1.001)
            pd.concat([a,frame('B',dates,1.001)]).to_parquet(data)
            a.to_parquet(subset)
            with self.assertRaisesRegex(ValueError,'complete stock-data universe'):
                main(['--data',str(data),'--universe-data',str(subset),'--symbols','A',
                      '--output',str(root/'out'),'--generations','1'])
            failure=json.loads((root/'out'/'failure.json').read_text())
            self.assertIn('selected subset',failure['error'])


class NoImplicitBenchmarkTests(unittest.TestCase):
    def test_direct_training_apis_also_forbid_equal_weight_fallback(self):
        p=replace(fixture(),synthetic_benchmark_fixture=False)
        with self.assertRaisesRegex(ValueError,'fallback is forbidden'):
            labels(p,5,'2023')
        with self.assertRaisesRegex(ValueError,'fallback is forbidden'):
            selection_benchmark(p,'2022','2023')
