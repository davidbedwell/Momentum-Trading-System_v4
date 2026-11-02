import pytest
from discovery.competitive_ga.native_shadow_trade_reconstruction import reconstruct
from discovery.competitive_ga.causal_calibration import Calibrator


def test_next_open_entry_horizon_exit_fees_and_causal_maturity():
    dates=[f'2020-01-{i:02d}' for i in range(2,8)]
    prices=[(d,'A',100+10*i) for i,d in enumerate(dates)]
    result=reconstruct([(dates[0],'A','g1')],prices,horizon=2,fee=.001)
    assert len(result['outcomes'])==1
    origin,buy,sell,ticker,outcome=result['outcomes'][0]
    assert (origin,buy,sell)==(dates[0],dates[1],dates[3])
    assert outcome.decision_session==0 and outcome.maturity_session==3
    assert outcome.net_r==pytest.approx((130*.999)/(110*1.001)-1)
    cal=Calibrator(min_samples=1)
    cal.record(outcome)
    assert cal.estimate('g1',('GA6_ENTRY',),3) is None
    assert cal.estimate('g1',('GA6_ENTRY',),4) is not None


def test_end_of_data_cannot_create_fictitious_outcome():
    prices=[('2020-01-02','A',100),('2020-01-03','A',110)]
    result=reconstruct([('2020-01-02','A','g1')],prices,horizon=2)
    assert result['unmatured']==1 and result['outcomes']==[]


def test_missing_signal_price_not_assumed():
    result=reconstruct([('2020-01-02','MISSING','g1')],[('2020-01-02','A',100)])
    assert result['missing']==1
