from types import SimpleNamespace
import pytest
from discovery.competitive_ga.ga7_native_daily_producer import produce

G=SimpleNamespace(operator='AND',feature_a='x',feature_b='y',
    threshold_a=0.,threshold_b=0.,entry_pct=.07,identity=lambda:'g7')
B={'AAA':{'eligible':True,'features':{'x':.8,'y':.9}},
   'BBB':{'eligible':True,'features':{'x':.2,'y':.9}},
   'CCC':{'eligible':False,'features':{'x':.9,'y':.9}}}


def run(bars=B,genome=G,defensive=False):
    return produce(genome,bars,decision_date='2020-01-03',
        trained_through='2020-01-02',source_hash='manifest',
        snapshot_hash='snapshot',defensive=defensive)


def test_native_ga7_predicates_and_eligibility():
    rows=run()
    assert len(rows)==1 and rows[0].ticker=='AAA'
    assert rows[0].chromosome_id=='g7' and rows[0].target_weight==.07


def test_defense_blocks_entry():
    assert run(defensive=True)==[]


def test_missing_native_features_fail_closed():
    with pytest.raises(ValueError,match='missing native'):
        run({'AAA':{'eligible':True,'features':{'x':.9}}})
