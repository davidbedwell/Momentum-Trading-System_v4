"""Verify persisted pilot accounting, benchmark identity, freeze and 8% acceptance."""
import argparse
import json
from pathlib import Path
import numpy as np
from .risk import MAX_DRAWDOWN, risk_feasible
from .run import sha
from .benchmarks import BenchmarkPolicy, SECONDARY


def verify(root):
    root=Path(root)
    read=lambda name:json.loads((root/name).read_text())
    manifest=read('manifest.json'); summary=read('results.json')
    assert manifest['risk_limit']==summary['risk_limit']==MAX_DRAWDOWN
    legacy=manifest['benchmark']=='equal_weight_buy_and_hold_exact_sample_PIT'
    if not legacy:
        policy=BenchmarkPolicy(manifest['benchmark_policy']['universe_profile'])
        assert manifest['benchmark']==policy.primary
        assert manifest['benchmark_policy']==policy.record()
        assert manifest['benchmark_policy']['secondary']==SECONDARY
        assert sha(Path(manifest['benchmark_data']))==manifest['benchmark_data_sha256']
        assert sha(Path(manifest['universe_data']))==manifest['universe_data_sha256']
        assert set(manifest['sample']).issubset(manifest['universe'])
    if manifest.get('membership'):
        assert sha(Path(manifest['membership']))==manifest['membership_sha256']
    assert manifest['initial_capital']==100000
    assert sha(Path(manifest['data']))==manifest['data_sha256']
    for fold in summary['folds']:
        directory=root/f"fold_{fold['year']}"
        get=lambda name:json.loads((directory/name).read_text())
        assert sha(directory/'frozen.json')==fold['frozen_sha256']
        frozen=get('frozen.json')
        if 'screen_policy' in manifest:
            assert frozen['screen_policy']==manifest['screen_policy']
            assert frozen['membership_sha256']==manifest['membership_sha256']
        assert frozen['sample']==manifest['sample']
        assert frozen['risk_limit']==MAX_DRAWDOWN
        if not legacy:
            assert frozen['benchmark']==manifest['benchmark']
            assert frozen['benchmark_policy']==manifest['benchmark_policy']
            assert frozen['benchmark_data_sha256']==manifest['benchmark_data_sha256']
            assert frozen['universe']==manifest['universe']
            assert frozen['universe_data_sha256']==manifest['universe_data_sha256']
            assert all(m['benchmark']==manifest['benchmark'] for m in frozen['models'])
        assert frozen['trained_before']==f"{fold['year']}-01-01"
        assert all(m['cutoff']==frozen['trained_before'] for m in frozen['models'])
        selection=get('selection.json')
        assert all(not r['metrics']['feasible'] and r['metrics']['max_drawdown']>MAX_DRAWDOWN
                   for r in get('rejected_risk.json'))
        assert all(r['metrics']['feasible'] for r in selection['journal'] if r['id']==fold['selected_id'])
        passive=get('benchmark.json')
        assert np.isclose(passive['equity'][0]['nav'],100000,rtol=0,atol=1e-8)
        secondary=passive if legacy else get('secondary_full_universe.json')
        universe=manifest['sample'] if legacy else manifest['universe']
        if not legacy:
            assert passive['benchmark_symbols']==[manifest['benchmark']]
            assert secondary['benchmark_symbols']==universe
            assert all(r['benchmark']==manifest['benchmark'] for r in selection['journal'])
        assert all(f['ticker'] in (manifest['sample'] if legacy else [manifest['benchmark']]) for f in passive['fills'])
        assert all(f['ticker'] in universe for f in secondary['fills'])
        assert all(f['date']>passive['equity'][0]['date'] for f in passive['fills'])
        assert all(f['date']>='2024-04-02' for f in secondary['fills'] if f['ticker']=='GEV')
        for row in secondary['equity']:
            if 'GEV' in universe and row['date']<'2024-04-02':
                assert row['cash']+1e-7 >= 100000/len(universe)
        for name in ['forward_frozen','ga8_seed_control','momentum_control']:
            result=get(name+'.json');m=result['metrics']
            assert [r['date'] for r in result['equity']]==[r['date'] for r in passive['equity']]
            for r in result['equity']:
                assert np.isclose(r['nav'],r['cash']+r['unsettled']+r['holdings'])
                assert r['cash']>=-1e-6
            nav=np.r_[100000.,[r['nav'] for r in result['equity']]]
            mdd=float(np.max(1-nav/np.maximum.accumulate(nav)))
            assert np.isclose(m['max_drawdown'],mdd)
            assert m['feasible']==risk_feasible(mdd)
            assert m['success']==bool(risk_feasible(mdd) and m['excess_pp']>0)
            assert np.isclose(m['excess_pp'],100*(m['cagr']-passive['metrics']['cagr']))
            assert np.isclose(m['incremental_nav'],m['final_nav']-passive['metrics']['final_nav'])
            if not legacy:
                assert m['primary_benchmark']==manifest['benchmark']
                assert np.isclose(m['secondary_excess_pp'],100*(m['cagr']-secondary['metrics']['cagr']))
                assert [r['date'] for r in result['equity']]==[r['date'] for r in secondary['equity']]
        rejected=get('forward_rejected_risk.json')
        assert bool(rejected)==(not fold['metrics']['forward_frozen']['feasible'])
        assert fold['accepted']==bool(fold['metrics']['training_refit_in_sample']['feasible'] and
                                      fold['metrics']['forward_frozen']['success'])
    assert summary['all_forward_pass']==bool(len(summary['folds'])==3 and all(f['accepted'] for f in summary['folds']))
    return dict(verified=True,folds=len(summary['folds']),all_forward_pass=summary['all_forward_pass'])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output',type=Path)
    args=parser.parse_args()
    print(json.dumps(verify(args.output),indent=2))

if __name__=='__main__':main()
