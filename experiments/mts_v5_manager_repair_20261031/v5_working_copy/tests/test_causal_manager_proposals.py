from discovery.competitive_ga.causal_calibration import Calibrator,TradeOutcome
from discovery.competitive_ga.native_signal_contract import NativeProposal
from discovery.competitive_ga.causal_manager_proposals import calibrated_proposals
from discovery.competitive_ga.manager_order_adapter import orders
from discovery.competitive_ga.manager_policy_v2 import Genes


def native(date='2020-02-01',family='GA6',cid='c1',ticker='ABC'):
    return NativeProposal(date,ticker,family,cid,'ENTER',.07,.03,
        'entry_equity_fraction' if family=='GA6' else 'r_multiple',
        'manifest-hash','features-hash','2020-01-01')


def test_no_calibration_no_capital():
    cal=Calibrator(min_samples=2)
    assert calibrated_proposals([native()], '2020-02-01',10,cal)==[]
    assert orders([],{},1.,Genes())==[]


def test_only_prior_matured_outcomes_can_enable_native_orders():
    cal=Calibrator(min_samples=2)
    cal.record(TradeOutcome('c1',('GA6_ENTRY',),1,5,.12,'shadow'))
    cal.record(TradeOutcome('c1',('GA6_ENTRY',),2,10,.08,'actual'))
    assert calibrated_proposals([native()], '2020-02-01',10,cal)==[]
    eligible=calibrated_proposals([native()], '2020-02-01',11,cal)
    assert len(eligible)==1 and eligible[0].edge==.10
    result=orders(eligible,{},1.,Genes())
    assert len(result)==1 and result[0].target_weight==.07


def test_native_scores_with_different_units_not_used_as_edge():
    cal=Calibrator(min_samples=1)
    cal.record(TradeOutcome('c1',('GA6_ENTRY',),1,2,.04,'shadow'))
    result=calibrated_proposals([native(family='GA7')],'2020-02-01',4,cal)
    assert result==[]  # GA6 outcomes cannot calibrate GA7
    cal.record(TradeOutcome('c1',('GA7_ENTRY',),1,2,.04,'shadow'))
    result=calibrated_proposals([native(family='GA7')],'2020-02-01',4,cal)
    assert result[0].edge==.04
