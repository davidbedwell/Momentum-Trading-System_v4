from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from MTS_V4.earnings_event_features import build_earnings_event_rows

NY = ZoneInfo("America/New_York")


def test_after_close_earnings_aligns_to_next_market_close():
    events = ({"security_id": "A", "event_type": "EARNINGS", "event_time": "2025-01-02T21:15:00+00:00", "surprise_pct": 5.0, "reported_eps": 1.1, "eps_estimate": 1.0},)
    closes = {"A": (datetime(2025, 1, 2, 16, 0, tzinfo=NY), datetime(2025, 1, 3, 16, 0, tzinfo=NY))}
    rows = build_earnings_event_rows(events, market_close_times_by_security=closes)
    assert rows[0]["effective_date"] == "2025-01-03"
    assert rows[0]["earnings_surprise_pct__v1"] == 5.0


def test_naive_event_timestamp_is_rejected_not_guessed():
    events = ({"security_id": "A", "event_type": "EARNINGS", "event_time": "2025-01-02T16:15:00"},)
    closes = {"A": (datetime(2025, 1, 3, 16, 0, tzinfo=NY),)}
    with pytest.raises(ValueError, match="timezone"):
        build_earnings_event_rows(events, market_close_times_by_security=closes)


def test_provider_before_market_class_aligns_to_same_session_close():
    events = ({"security_id": "A", "event_type": "EARNINGS", "report_date": "2025-01-02", "availability_class": "BeforeMarket"},)
    closes = {"A": (datetime(2025, 1, 2, 16, 0, tzinfo=NY), datetime(2025, 1, 3, 16, 0, tzinfo=NY))}
    rows = build_earnings_event_rows(events, market_close_times_by_security=closes)
    assert rows[0]["effective_date"] == "2025-01-02"


def test_provider_after_market_class_aligns_to_next_session_close():
    events = ({"security_id": "A", "event_type": "EARNINGS", "report_date": "2025-01-02", "availability_class": "AfterMarket"},)
    closes = {"A": (datetime(2025, 1, 2, 16, 0, tzinfo=NY), datetime(2025, 1, 3, 16, 0, tzinfo=NY))}
    rows = build_earnings_event_rows(events, market_close_times_by_security=closes)
    assert rows[0]["effective_date"] == "2025-01-03"


def test_unknown_provider_timing_is_conservatively_delayed_to_next_session_close():
    events = ({"security_id": "A", "event_type": "EARNINGS", "report_date": "2025-01-02", "availability_class": "Unknown"},)
    closes = {"A": (datetime(2025, 1, 3, 16, 0, tzinfo=NY),)}
    rows = build_earnings_event_rows(events, market_close_times_by_security=closes)
    assert rows[0]["effective_date"] == "2025-01-03"
    assert rows[0]["earnings_timing_known__v1"] == 0.0


def test_event_before_available_calendar_is_excluded_not_shifted_forward():
    events = ({"security_id": "A", "event_type": "EARNINGS", "report_date": "2024-12-01", "availability_class": "AfterMarket"},)
    closes = {"A": (datetime(2025, 1, 3, 16, 0, tzinfo=NY),)}
    assert build_earnings_event_rows(events, market_close_times_by_security=closes) == ()


def test_same_session_conflicts_preserve_count_and_null_conflicting_values():
    events = (
        {"security_id": "A", "event_type": "EARNINGS", "report_date": "2025-01-02", "availability_class": "AfterMarket", "reported_eps": 2.0, "eps_estimate": 1.8, "surprise_pct": 11.1},
        {"security_id": "A", "event_type": "EARNINGS", "report_date": "2025-01-02", "availability_class": "Unknown", "reported_eps": 2.0, "eps_estimate": 1.9, "surprise_pct": 5.3},
    )
    closes = {"A": (datetime(2025, 1, 2, 16, 0, tzinfo=NY), datetime(2025, 1, 3, 16, 0, tzinfo=NY))}
    rows = build_earnings_event_rows(events, market_close_times_by_security=closes)
    assert len(rows) == 1
    assert rows[0]["earnings_event_count__v1"] == 2.0
    assert rows[0]["earnings_reported_eps__v1"] == 2.0
    assert rows[0]["earnings_estimate_eps__v1"] is None
    assert rows[0]["earnings_surprise_pct__v1"] is None
    assert rows[0]["earnings_timing_known__v1"] == 0.0
