from __future__ import annotations

from datetime import date

from MTS_V4.contracts import SubjectMetadata
from MTS_V4.live_sources import LiveSourceError, UnusualWhalesDarkPoolSource


class _FakeDarkPoolSource(UnusualWhalesDarkPoolSource):
    def __init__(self, responses, **kwargs):
        super().__init__(api_key="test-key", **kwargs)
        self._responses = iter(responses)
        self.calls = []

    def _get(self, path, params=None):
        self.calls.append((path, dict(params or {})))
        response = next(self._responses)
        if isinstance(response, Exception):
            raise response
        return response


def _subject():
    return SubjectMetadata(subject_id="equity:AAPL", ticker="AAPL", attributes={})


def test_darkpool_source_walks_requested_weekdays_newest_to_oldest():
    source = _FakeDarkPoolSource(
        responses=[
            [{"trade_id": "w1", "executed_at": "2026-09-09T15:00:00Z", "price": "102", "size": 12}],
            [{"trade_id": "t1", "executed_at": "2026-09-08T15:00:00Z", "price": "101", "size": 11}],
            [{"trade_id": "m1", "executed_at": "2026-09-07T15:00:00Z", "price": "100", "size": 10}],
        ],
        history_days=3,
        end_date=date(2026, 9, 9),
        limit=500,
    )

    payload = next(iter(source.acquire(_subject())))

    assert [params["date"] for _, params in source.calls] == [
        "2026-09-09",
        "2026-09-08",
        "2026-09-07",
    ]
    assert payload.row_count == 3
    assert payload.coverage_start == "2026-09-07T15:00:00Z"
    assert payload.coverage_end == "2026-09-09T15:00:00Z"
    assert payload.provenance["requested_start_date"] == "2026-09-07"
    assert payload.provenance["requested_end_date"] == "2026-09-09"
    assert payload.provenance["queried_start_date"] == "2026-09-07"
    assert payload.provenance["queried_end_date"] == "2026-09-09"
    assert payload.provenance["entitlement_limited"] is False
    assert payload.provenance["first_forbidden_date"] is None
    assert payload.provenance["request_count"] == 3
    assert payload.provenance["pagination"] == "date+older_than"


def test_darkpool_source_skips_weekends_in_calendar_window():
    source = _FakeDarkPoolSource(
        responses=[
            [{"trade_id": "m1", "executed_at": "2026-09-07T15:00:00Z"}],
            [{"trade_id": "f1", "executed_at": "2026-09-04T15:00:00Z"}],
        ],
        history_days=4,
        end_date=date(2026, 9, 7),
    )

    next(iter(source.acquire(_subject())))

    assert [params["date"] for _, params in source.calls] == [
        "2026-09-07",
        "2026-09-04",
    ]


def test_darkpool_source_paginates_full_day_with_older_than_cursor():
    page1 = [
        {"trade_id": "a", "executed_at": "2026-09-09T20:00:00Z"},
        {"trade_id": "b", "executed_at": "2026-09-09T19:00:00Z"},
    ]
    page2 = [
        {"trade_id": "c", "executed_at": "2026-09-09T18:00:00Z"},
    ]
    source = _FakeDarkPoolSource(
        responses=[page1, page2],
        history_days=1,
        end_date=date(2026, 9, 9),
        limit=2,
    )

    payload = next(iter(source.acquire(_subject())))

    assert payload.row_count == 3
    assert source.calls[0][1] == {"date": "2026-09-09", "limit": 2}
    assert source.calls[1][1] == {
        "date": "2026-09-09",
        "limit": 2,
        "older_than": "2026-09-09T19:00:00Z",
    }


def test_darkpool_source_rejects_non_advancing_pagination_cursor():
    page = [
        {"trade_id": "a", "executed_at": "2026-09-09T20:00:00Z"},
        {"trade_id": "b", "executed_at": "2026-09-09T19:00:00Z"},
    ]
    repeated = [
        {"trade_id": "c", "executed_at": "2026-09-09T20:00:00Z"},
        {"trade_id": "d", "executed_at": "2026-09-09T19:00:00Z"},
    ]
    source = _FakeDarkPoolSource(
        responses=[page, repeated],
        history_days=1,
        end_date=date(2026, 9, 9),
        limit=2,
    )

    try:
        next(iter(source.acquire(_subject())))
    except LiveSourceError as exc:
        assert "pagination cursor did not advance" in str(exc)
    else:
        raise AssertionError("expected non-advancing pagination cursor to fail")


def test_darkpool_source_stops_at_historical_403_after_successful_newer_queries():
    source = _FakeDarkPoolSource(
        responses=[
            [{"trade_id": "w1", "executed_at": "2026-09-09T15:00:00Z"}],
            [{"trade_id": "t1", "executed_at": "2026-09-08T15:00:00Z"}],
            LiveSourceError(
                "request failed for https://api.unusualwhales.com/api/darkpool/AAPL?date=2026-09-07&limit=500: HTTPError: HTTP Error 403: Forbidden"
            ),
        ],
        history_days=3,
        end_date=date(2026, 9, 9),
    )

    payload = next(iter(source.acquire(_subject())))

    assert payload.row_count == 2
    assert [params["date"] for _, params in source.calls] == [
        "2026-09-09",
        "2026-09-08",
        "2026-09-07",
    ]
    assert payload.provenance["queried_start_date"] == "2026-09-08"
    assert payload.provenance["queried_end_date"] == "2026-09-09"
    assert payload.provenance["queried_weekdays"] == 2
    assert payload.provenance["entitlement_limited"] is True
    assert payload.provenance["first_forbidden_date"] == "2026-09-07"
    assert payload.provenance["request_count"] == 2


def test_darkpool_source_does_not_hide_initial_403():
    source = _FakeDarkPoolSource(
        responses=[
            LiveSourceError(
                "request failed for https://api.unusualwhales.com/api/darkpool/AAPL?date=2026-09-09&limit=500: HTTPError: HTTP Error 403: Forbidden"
            ),
        ],
        history_days=1,
        end_date=date(2026, 9, 9),
    )

    try:
        next(iter(source.acquire(_subject())))
    except LiveSourceError as exc:
        assert "HTTP Error 403" in str(exc)
    else:
        raise AssertionError("expected initial 403 to remain fatal")
