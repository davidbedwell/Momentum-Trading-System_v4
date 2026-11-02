import pytest
from discovery.competitive_ga.native_signal_contract import NativeProposal
from discovery.competitive_ga.causal_calibration import Calibrator,TradeOutcome
from discovery.competitive_ga.causal_manager_proposals import calibrated_proposals
from discovery.competitive_ga.manager_strategy_registry import FAMILIES,require_all

UNITS={'GA4':'native_horizon_score','HORIZONS':'native_horizon_score',
       'GA6':'entry_equity_fraction','GA7':'r_multiple'}


def native(family):
    return NativeProposal('2020-02-01',family,'GA4' if family=='GA4' else family,
        family+'-chrom','ENTER',.07,.02,UNITS[family],
        'manifest','snapshot','2020-01-01')


def test_all_families_accepted_but_not_assumed_ready():
    assert set(FAMILIES)==set(UNITS)
    for family in FAMILIES:
        assert native(family).family==family
    with pytest.raises(RuntimeError,match='full manager experiment blocked'):
        require_all()


def test_four_family_calibration_isolated():
    cal=Calibrator(min_samples=1)
    for family in FAMILIES:
        cal.record(TradeOutcome(family+'-chrom',(family+'_ENTRY',),1,3,.04,'shadow'))
    proposals=calibrated_proposals([native(f) for f in FAMILIES], '2020-02-01',4,cal)
    assert {p.family for p in proposals}==set(FAMILIES)
    assert all(p.edge==.04 for p in proposals)


def test_wrong_family_context_cannot_unlock_capital():
    cal=Calibrator(min_samples=1)
    cal.record(TradeOutcome('GA7-chrom',('GA6_ENTRY',),1,3,.5,'shadow'))
    assert calibrated_proposals([native('GA7')],'2020-02-01',4,cal)==[]
