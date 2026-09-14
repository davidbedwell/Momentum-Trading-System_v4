from MTS_V4.intraday_analysis_substrate import intraday_participation_substrate


def _bar(date, time, session, price, volume):
    return {
        "timestamp": f"{date}T{time}:00-04:00",
        "date": date,
        "market_time": time,
        "session": session,
        "open": price,
        "high": price + 0.1,
        "low": price - 0.1,
        "close": price,
        "volume": volume,
    }


def test_intraday_substrate_precomputes_neutral_measurements_and_time_matched_rvol():
    rows = [
        _bar("2026-09-10", "09:25", "PREMARKET", 9.8, 50),
        _bar("2026-09-10", "09:30", "REGULAR", 10.0, 100),
        _bar("2026-09-10", "09:35", "REGULAR", 10.2, 200),
        _bar("2026-09-11", "09:25", "PREMARKET", 10.8, 80),
        _bar("2026-09-11", "09:30", "REGULAR", 11.0, 200),
        _bar("2026-09-11", "09:35", "REGULAR", 11.2, 400),
    ]
    events = [{"event_time": "2026-09-11T08:00:00-04:00", "event_date": "2026-09-11", "event_type": "NEWS", "headline": "example"}]
    structure = [{"as_of_utc": "2026-09-11T12:00:00Z", "float_shares": 1_000_000}]
    result = intraday_participation_substrate({"intraday": rows, "events": events, "structure": structure}, {})
    panel = result["derived_datasets"]["intraday_measurement_panel"]
    summaries = result["derived_datasets"]["intraday_session_summary"]

    second_day_open = next(row for row in panel if row["date"] == "2026-09-11" and row["market_time"] == "09:30")
    assert second_day_open["time_adjusted_relative_volume"] == 2.0
    assert second_day_open["time_adjusted_rvol_prior_session_count"] == 1
    assert second_day_open["opening_range_5m_high"] == 11.1
    assert second_day_open["vwap"] is not None
    assert summaries[-1]["event_records"][0]["event_type"] == "NEWS"
    assert summaries[-1]["current_session_volume_over_current_float"] == 0.0006
    assert result["policy"]["deterministic_signal"] is False
    assert result["policy"]["scientific_interpretation"] == "AI_RESEARCH_DIRECTOR_ONLY"


def test_current_float_is_not_back_projected_to_historical_sessions():
    rows = [
        _bar("2026-09-10", "09:30", "REGULAR", 10.0, 100),
        _bar("2026-09-11", "09:30", "REGULAR", 11.0, 200),
    ]
    structure = [{"as_of_utc": "2026-09-11T12:00:00Z", "float_shares": 1_000_000}]
    summaries = intraday_participation_substrate({"intraday": rows, "structure": structure}, {})["derived_datasets"]["intraday_session_summary"]
    assert summaries[0]["current_float_shares_if_current_session"] is None
    assert summaries[0]["current_session_volume_over_current_float"] is None
    assert summaries[1]["current_float_shares_if_current_session"] == 1_000_000


def test_forward_returns_are_explicitly_exploration_outcomes_not_prediction_features():
    rows = [_bar("2026-09-11", f"09:{30 + 5*i:02d}", "REGULAR", 10.0 + i, 100) for i in range(5)]
    result = intraday_participation_substrate({"intraday": rows}, {})
    first = result["derived_datasets"]["intraday_measurement_panel"][0]
    assert first["forward_return_5m"] == 0.1
    assert result["policy"]["forward_outcomes_are_exploration_only_not_prediction_features"] is True
