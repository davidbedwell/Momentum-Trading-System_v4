"""Synthetic assertions for historical evidence handling and permutation statistic."""
import pytest
pytest.importorskip('numpy')
pytest.importorskip('pandas')
from sector_pipeline import core
from sector_pipeline.expanded_stage1 import sector_label, fast_placebo, annual_members


def test_historical_sector_never_backfilled_or_modernized():
    assert sector_label('-') == 'UNKNOWN'
    assert sector_label('') == 'UNKNOWN'
    assert sector_label('Communication Services') == 'UNKNOWN'
    assert sector_label('Real Estate') == 'UNKNOWN'
    assert sector_label('Telecommunications') == 'Telecommunication Services'
    assert sector_label('Financials') == 'Financials'


def test_vectorized_placebo_retains_actual_ic_and_required_count():
    rows=[]
    for month in ('2007-04-30','2007-05-31'):
        for sector in ('A','B'):
            for i in range(12):
                rows.append(dict(asof=month,sector=sector,horizon=1,H1_rank=(i+1)/12,
                                 H5_rank=(i+1)/12,excess=(i-3)**2))
    fast=fast_placebo(rows,'H1',1)
    reference=core.placebo(rows,'H1',1)
    assert fast['real']==pytest.approx(reference['real'])
    assert fast['shuffles']==1000
    assert fast==fast_placebo(rows,'H1',1)
    assert fast_placebo(rows,'H5',1)['real']==pytest.approx(-fast['real'])
    assert -1<=fast['percentile99']<=1


def test_undefined_hypothesis_never_fabricates_placebos():
    assert fast_placebo([], 'H4', 1)['shuffles']==0
    assert fast_placebo([], 'H4', 1)['real'] is None


def test_compaction_preserves_every_month_and_sector_transition():
    from sector_pipeline.expanded_stage1 import compact_members
    members=[dict(symbol='A',sector='X',start='2007-04-30',end='2007-05-01'),
             dict(symbol='A',sector='X',start='2007-05-31',end='2007-06-01'),
             dict(symbol='A',sector='Y',start='2007-06-29',end='2007-06-30')]
    compact=compact_members(members)
    assert len(compact)==2
    assert compact[0]['end']=='2007-06-01'
    assert compact[1]['sector']=='Y'
