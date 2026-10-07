import pandas as pd
from Core.g3.earnings import classify_record,first_usable_session,event_features

def test_earnings_report_before_fiscal_is_quarantined():
    r={"report_date":"2020-01-01","date":"2020-03-31","before_after_market":"AfterMarket"}
    assert classify_record(r).startswith("QUARANTINE")

def test_earnings_market_timing_pit_clock():
    sessions=pd.to_datetime(["2020-01-02","2020-01-03","2020-01-06"])
    assert first_usable_session("2020-01-03","BeforeMarket",sessions)==pd.Timestamp("2020-01-03")
    assert first_usable_session("2020-01-03","AfterMarket",sessions)==pd.Timestamp("2020-01-06")
    assert first_usable_session("2020-01-03",None,sessions)==pd.Timestamp("2020-01-06")
    assert first_usable_session("2020-01-04","BeforeMarket",sessions)==pd.Timestamp("2020-01-06")

def test_earnings_features_use_only_event_fields():
    r={"actual":1.2,"estimate":1.0,"percent":20.0}
    f=event_features(r)
    assert f["earnings_actual"]==1.2 and f["earnings_estimate"]==1.0
    assert abs(f["earnings_surprise_abs"]-0.2)<1e-12
    assert f["earnings_surprise_percent"]==20.0
