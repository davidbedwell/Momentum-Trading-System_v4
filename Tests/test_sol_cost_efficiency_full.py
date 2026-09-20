from MTS_V4.neutral_pre_sol_context import catalyst_timing_substrate, finra_neutral_substrate
from MTS_V4.rolling_analysis_transform import rolling_numeric
from MTS_V4.share_structure_analysis import sec_share_structure_context


def test_finra_substrate_aggregates_without_ranking():
    rows = [
        {"weekStartDate":"2026-01-05","summaryTypeCode":"ATS_W_SMBL","totalWeeklyShareQuantity":100,"totalWeeklyTradeCount":10},
        {"weekStartDate":"2026-01-05","summaryTypeCode":"ATS_W_SMBL","totalWeeklyShareQuantity":50,"totalWeeklyTradeCount":5},
        {"weekStartDate":"2026-01-05","summaryTypeCode":"OTC_W_SMBL","totalWeeklyShareQuantity":20,"totalWeeklyTradeCount":2},
    ]
    out = finra_neutral_substrate({"finra": rows}, {})
    panel = out["derived_datasets"]["finra_weekly_neutral_panel"]
    assert len(panel) == 2
    assert panel[0]["share_quantity"] == 150.0
    assert "rank" not in panel[0] and "signal" not in panel[0]


def test_catalyst_inventory_classifies_clock_but_not_materiality():
    rows = [{"event_time":"2026-01-05T16:30:00-05:00","event_date":"2026-01-05","event_type":"EARNINGS","headline":None}]
    out = catalyst_timing_substrate({"events": rows}, {})
    event = out["derived_datasets"]["catalyst_timing_inventory"][0]
    assert event["release_clock_class"] == "AFTER_MARKET_HOURS"
    assert "material" not in event and "signal" not in event


def test_share_turnover_prior20_excludes_current_session():
    market = [{"date":f"2026-01-{i:02d}","close":10.0,"volume":100.0+i} for i in range(1,23)]
    facts = [{"fact_kind":"SHARES_OUTSTANDING","known_at":"2025-12-31","period_end":"2025-12-31","value":1000.0,"unit":"shares"}]
    out = sec_share_structure_context({"market":market,"sec":facts}, {})
    panel = out["derived_datasets"]["sec_share_structure_panel"]
    assert panel[0]["prior_20_session_turnover_mean"] is None
    expected = sum((100.0+i)/1000.0 for i in range(1,21))/20
    assert abs(panel[20]["prior_20_session_turnover_mean"] - expected) < 1e-12
    assert panel[20]["prior_20_observation_count"] == 20


def test_rolling_transform_preserves_rows_index_and_supports_lagged_baseline():
    rows = [{"date":str(i),"x":float(i)} for i in range(1,7)]
    out = rolling_numeric({"source":rows}, {"column":"x","window":3,"statistic":"MEAN","lag":1,"output_name":"prior3"})
    panel = out["derived_datasets"]["rolling_numeric_feature"]
    assert len(panel) == len(rows)
    assert [r["index"] for r in panel] == list(range(len(rows)))
    assert panel[3]["prior3"] == 2.0
    assert panel[3]["date"] == "4"


def test_rolling_slope_is_single_pass_reusable_not_compose_chain():
    rows = [{"x":v} for v in (1.0,2.0,3.0,4.0)]
    out = rolling_numeric({"source":rows}, {"column":"x","window":4,"statistic":"SLOPE","lag":0,"output_name":"slope4"})
    assert out["derived_datasets"]["rolling_numeric_feature"][-1]["slope4"] == 1.0
