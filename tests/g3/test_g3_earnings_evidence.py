import pandas as pd
from Core.g3.earnings_evidence import earnings_daily_features

def test_aftermarket_event_not_visible_until_next_session():
    sessions=pd.to_datetime(["2020-01-02","2020-01-03","2020-01-06","2020-01-07"])
    e=[{"report_date":"2020-01-03","date":"2019-12-31","before_after_market":"AfterMarket","actual":1.2,"estimate":1.0,"percent":20.0}]
    f=earnings_daily_features("T",e,sessions)
    assert pd.isna(f.loc["2020-01-03","earnings_actual"])
    assert f.loc["2020-01-06","earnings_actual"]==1.2

def test_beforemarket_event_visible_same_session():
    sessions=pd.to_datetime(["2020-01-02","2020-01-03","2020-01-06"])
    e=[{"report_date":"2020-01-03","date":"2019-12-31","before_after_market":"BeforeMarket","actual":2.0,"estimate":1.5,"percent":33.3}]
    f=earnings_daily_features("T",e,sessions)
    assert f.loc["2020-01-03","earnings_actual"]==2.0
def test_aligned_real_evidence_is_same_calendar_date_across_tickers():
    from Core.g3.earnings_evidence import build_earnings_index,aligned_evidence_with_earnings
    tickers=["AAPL","MSFT","XOM"]
    ev=build_earnings_index(tickers)
    dates,X,Y,cols=aligned_evidence_with_earnings(tickers,ev)
    assert len(dates)>4000
    assert X.shape[0]==Y.shape[0]==len(dates)
    assert X.shape[1]==Y.shape[1]==len(tickers)
    assert dates.is_monotonic_increasing and dates.is_unique
    # N2 now permutes outcomes only among stocks sharing this exact date index.
    from Core.g3.controls import apply_aligned_n2
    z=apply_aligned_n2(Y[-100:],123)
    for d in range(100):
        assert {tuple(v) for v in z[d]}=={tuple(v) for v in Y[-100:][d]}
