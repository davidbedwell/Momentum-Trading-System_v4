import pytest
from discovery.competitive_ga.horizons_native_daily_producer import produce

GENOME={'ids':[0],'w':[1.], 'qual':.0,'short':False,
        'alloc':'strength','replace_margin':0.}
PANEL={'AAA':{'ret5':.1},'BBB':{'ret5':.3},'CCC':{'ret5':.2}}


def run(panel=PANEL,previous=None,genome=GENOME):
    return produce(genome,panel,previous=previous,
        decision_date='2020-02-03',chromosome_id='h1',
        trained_through='2020-01-31',source_hash='manifest',
        snapshot_hash='snapshot')


def test_real_native_cross_sectional_rank_drives_entry():
    result=run()
    assert result
    assert all(p.family=='HORIZONS' for p in result)
    assert all(p.native_score==PANEL[p.ticker]['ret5'] for p in result)
    assert any(p.action=='ENTER' for p in result)


def test_native_exit_from_previous_position():
    result=run(previous={'AAA':.08})
    assert any(p.ticker=='AAA' and p.action=='EXIT' for p in result)


def test_missing_feature_and_short_genome_fail_closed():
    with pytest.raises(ValueError,match='missing causal'):
        run(panel={'AAA':{'ret5':.1},'BBB':{}})
    with pytest.raises(ValueError,match='short-enabled'):
        run(genome={**GENOME,'short':True})
