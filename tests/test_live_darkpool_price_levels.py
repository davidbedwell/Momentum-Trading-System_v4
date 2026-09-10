from __future__ import annotations

from datetime import date

from MTS_V4.contracts import SubjectMetadata
from MTS_V4.live_sources import (
    LiveSourceError,
    UnusualWhalesDarkPoolPriceLevelsSource,
    UnusualWhalesDarkPoolSource,
    standard_live_market_source,
)


class _FakePriceLevelsSource(UnusualWhalesDarkPoolPriceLevelsSource):
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


def test_price_levels_source_walks_history_and_tags_each_row_with_source_date():
    source = _FakePriceLevelsSource(
        responses=[
            [
                {"price": "102", "dark_pool_volume": "30", "regular_volume": "40"},
                {"price": "101.5", "dark_pool_volume": "20", "regular_volume": "10"},
            ],
            [{"price": "100", "dark_pool_volume": "5", "regular_volume": "15"}],
        ],
        history_days=2,
        end_date=date(2026, 9, 9),
    )

    payload = next(iter(source.acquire(_subject())))

    assert [params["date"] for _, params in source.calls] == ["2026-09-09", "2026-09-08"]
    assert payload.row_count == 3
    assert payload.coverage_start == "2026-09-08"
    assert payload.coverage_end == "2026-09-09"
    assert payload.evidence_type == "OFF_EXCHANGE_DARKPOOL_PRICE_LEVELS"
    assert payload.source_identity == "UNUSUAL_WHALES_DARKPOOL_PRICE_LEVELS"
    assert payload.schema == ("price", "dark_pool_volume", "regular_volume", "date")
    assert [row["date"] for row in payload.payload] == ["2026-09-09", "2026-09-09", "2026-09-08"]
    assert payload.provenance["representation"] == "provider_aggregated_price_levels"
    assert payload.provenance["raw_drilldown_source"] == "UNUSUAL_WHALES_DARKPOOL"
    assert payload.provenance["request_count"] == 2
    assert payload.provenance["entitlement_limited"] is False


def test_price_levels_source_preserves_recent_history_at_entitlement_boundary():
    source = _FakePriceLevelsSource(
        responses=[
            [{"price": "102", "dark_pool_volume": "30", "regular_volume": "40"}],
            [{"price": "101", "dark_pool_volume": "20", "regular_volume": "25"}],
            LiveSourceError(
                "request failed for https://api.unusualwhales.com/api/darkpool/AAPL/price-levels?date=2026-09-07: HTTPError: HTTP Error 403: Forbidden"
            ),
        ],
        history_days=3,
        end_date=date(2026, 9, 9),
    )

    payload = next(iter(source.acquire(_subject())))

    assert payload.row_count == 2
    assert payload.provenance["queried_start_date"] == "2026-09-08"
    assert payload.provenance["queried_end_date"] == "2026-09-09"
    assert payload.provenance["queried_weekdays"] == 2
    assert payload.provenance["entitlement_limited"] is True
    assert payload.provenance["first_forbidden_date"] == "2026-09-07"
    assert payload.provenance["request_count"] == 2


def test_price_levels_source_does_not_hide_initial_forbidden_response():
    source = _FakePriceLevelsSource(
        responses=[
            LiveSourceError(
                "request failed for https://api.unusualwhales.com/api/darkpool/AAPL/price-levels?date=2026-09-09: HTTPError: HTTP Error 403: Forbidden"
            )
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


def test_standard_live_source_uses_compact_price_levels_and_retains_raw_source_as_separate_capability():
    source = standard_live_market_source()
    members = source._sources

    assert any(isinstance(member, UnusualWhalesDarkPoolPriceLevelsSource) for member in members)
    assert not any(type(member) is UnusualWhalesDarkPoolSource for member in members)
