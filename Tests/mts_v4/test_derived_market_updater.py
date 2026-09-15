from datetime import date, timedelta
import json

import pytest

from MTS_V4.derived_market_store import InMemoryDerivedMarketStore, UniverseDefinition
from MTS_V4.derived_market_store import DerivedMarketStoreError
from MTS_V4.derived_market_updater import TemporaryMarketAcquisitionCache, _attach_membership_and_identity, _validate_complete_observed_cross_sections, maintain_standard_market_store
from MTS_V4.universe_membership import IntervalMembership, MembershipInterval


class FakeDailySource:
    source_identity = "FAKE_DAILY"

    def __init__(self):
        self.calls = []

    def fetch(self, *, ticker, start_date, end_date):
        self.calls.append((ticker, start_date, end_date))
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
        rows = []
        cursor = start
        i = 0
        while cursor <= end:
            close = 100.0 + i * 0.1
            rows.append({"date": cursor.isoformat(), "open": close, "high": close + 1, "low": close - 1, "close": close, "volume": 1_000_000 + i})
            cursor += timedelta(days=1)
            i += 1
        return rows


def test_incremental_update_advances_predictor_high_water_without_rewriting_history():
    store = InMemoryDerivedMarketStore()
    universe = UniverseDefinition("test", "test universe", "fixture", True)
    membership = IntervalMembership((MembershipInterval("SEC1", "AAA", "2020-01-01", None, "TECH", source_identity="fixture"),))
    source = FakeDailySource()
    first = maintain_standard_market_store(
        store=store,
        universe=universe,
        membership=membership,
        source=source,
        through_date="2025-01-10",
        initial_start_date="2024-01-01",
        update_id_prefix="first",
    )
    assert first.predictor_last_date == "2025-01-10"
    second = maintain_standard_market_store(
        store=store,
        universe=universe,
        membership=membership,
        source=source,
        through_date="2025-01-17",
        update_id_prefix="second",
    )
    assert second.predictor_first_date == "2025-01-11"
    assert second.predictor_last_date == "2025-01-17"
    assert second.predictor_rows == 7
    assert second.acquisition_start < second.predictor_first_date


def _row(security_id, ticker, effective):
    return {"security_id": security_id, "ticker": ticker, "date": effective}


def test_cross_section_accepts_and_audits_one_leading_pre_regular_trading_session():
    membership = IntervalMembership((
        MembershipInterval("SEC-PEER", "PEER", "2012-12-31", None, source_identity="fixture"),
        MembershipInterval("SEC-ABBV", "ABBV", "2012-12-31", None, source_identity="fixture"),
    ))
    rows = (
        _row("SEC-PEER", "PEER", "2012-12-31"),
        _row("SEC-PEER", "PEER", "2013-01-02"),
        _row("SEC-ABBV", "ABBV", "2013-01-02"),
    )

    result = _validate_complete_observed_cross_sections(
        rows=rows,
        membership=membership,
        start_date="2012-12-31",
        end_date="2013-01-02",
    )

    assert result.observed_counts == {"2012-12-31": 1, "2013-01-02": 2}
    assert result.tradable_start_adjustments == ({
        "security_id": "SEC-ABBV",
        "ticker": "ABBV",
        "source_membership_start": "2012-12-31",
        "first_regular_market_observation": "2013-01-02",
        "excluded_leading_observed_sessions": ("2012-12-31",),
        "reason": "SOURCE_MEMBERSHIP_PRECEDES_FIRST_REGULAR_MARKET_OBSERVATION",
    },)


def test_cross_section_rejects_more_than_one_leading_observed_session():
    membership = IntervalMembership((
        MembershipInterval("SEC-PEER", "PEER", "2020-01-01", None, source_identity="fixture"),
        MembershipInterval("SEC-LATE", "LATE", "2020-01-01", None, source_identity="fixture"),
    ))
    rows = (
        _row("SEC-PEER", "PEER", "2020-01-01"),
        _row("SEC-PEER", "PEER", "2020-01-02"),
        _row("SEC-PEER", "PEER", "2020-01-03"),
        _row("SEC-LATE", "LATE", "2020-01-03"),
    )

    with pytest.raises(DerivedMarketStoreError, match="cross-section preflight found 1 defects"):
        _validate_complete_observed_cross_sections(
            rows=rows,
            membership=membership,
            start_date="2020-01-01",
            end_date="2020-01-03",
        )


def test_calibration_cross_section_audits_longer_current_ticker_history_gap():
    membership = IntervalMembership((
        MembershipInterval("SEC-PEER", "PEER", "2020-01-01", None, source_identity="CALIBRATION_ONLY"),
        MembershipInterval("SEC-HWM", "HWM", "2020-01-01", None, source_identity="CALIBRATION_ONLY"),
    ))
    rows = (
        _row("SEC-PEER", "PEER", "2020-01-01"),
        _row("SEC-PEER", "PEER", "2020-01-02"),
        _row("SEC-PEER", "PEER", "2020-01-03"),
        _row("SEC-HWM", "HWM", "2020-01-03"),
    )

    result = _validate_complete_observed_cross_sections(
        rows=rows,
        membership=membership,
        start_date="2020-01-01",
        end_date="2020-01-03",
    )

    assert result.observed_counts == {
        "2020-01-01": 1,
        "2020-01-02": 1,
        "2020-01-03": 2,
    }
    assert result.tradable_start_adjustments[0]["security_id"] == "SEC-HWM"
    assert result.tradable_start_adjustments[0]["excluded_leading_observed_sessions"] == (
        "2020-01-01",
        "2020-01-02",
    )
    assert result.tradable_start_adjustments[0]["reason"] == (
        "CALIBRATION_CURRENT_TICKER_HISTORY_BEGINS_AFTER_SOURCE_MEMBERSHIP"
    )


def test_cross_section_still_rejects_missing_session_after_regular_trading_begins():
    membership = IntervalMembership((
        MembershipInterval("SEC-PEER", "PEER", "2020-01-01", None, source_identity="fixture"),
        MembershipInterval("SEC-GAP", "GAP", "2020-01-01", None, source_identity="fixture"),
    ))
    rows = (
        _row("SEC-PEER", "PEER", "2020-01-01"),
        _row("SEC-GAP", "GAP", "2020-01-01"),
        _row("SEC-PEER", "PEER", "2020-01-02"),
        _row("SEC-PEER", "PEER", "2020-01-03"),
        _row("SEC-GAP", "GAP", "2020-01-03"),
    )

    with pytest.raises(DerivedMarketStoreError, match="cross-section preflight found 1 defects"):
        _validate_complete_observed_cross_sections(
            rows=rows,
            membership=membership,
            start_date="2020-01-01",
            end_date="2020-01-03",
        )


class CountingDailySource:
    source_identity = "COUNTING"

    def __init__(self):
        self.calls = 0

    def fetch(self, *, ticker, start_date, end_date):
        self.calls += 1
        return ({"date": "2020-01-02", "open": 1.0, "high": 2.0, "low": 0.5, "close": 1.5, "volume": 10.0},)


def test_temporary_acquisition_cache_reuses_verified_download(tmp_path):
    membership = IntervalMembership((
        MembershipInterval("SEC-1", "AAA", "2020-01-01", None, source_identity="CALIBRATION_ONLY"),
    ))
    source = CountingDailySource()
    cache = TemporaryMarketAcquisitionCache(tmp_path / "cache")

    first = _attach_membership_and_identity(
        membership=membership,
        source=source,
        start_date="2020-01-01",
        end_date="2020-01-03",
        shares_source=None,
        download_workers=1,
        acquisition_cache=cache,
    )
    second = _attach_membership_and_identity(
        membership=membership,
        source=source,
        start_date="2020-01-01",
        end_date="2020-01-03",
        shares_source=None,
        download_workers=1,
        acquisition_cache=cache,
    )

    assert first == second
    assert source.calls == 1


def test_preflight_audit_collects_multiple_defects_and_survives_failure(tmp_path):
    membership = IntervalMembership((
        MembershipInterval("SEC-PEER", "PEER", "2020-01-01", None, source_identity="fixture"),
        MembershipInterval("SEC-NONE", "NONE", "2020-01-01", None, source_identity="fixture"),
        MembershipInterval("SEC-GAP", "GAP", "2020-01-01", None, source_identity="fixture"),
    ))
    rows = (
        _row("SEC-PEER", "PEER", "2020-01-01"),
        _row("SEC-GAP", "GAP", "2020-01-01"),
        _row("SEC-PEER", "PEER", "2020-01-02"),
        _row("SEC-PEER", "PEER", "2020-01-03"),
        _row("SEC-GAP", "GAP", "2020-01-03"),
    )
    cache = TemporaryMarketAcquisitionCache(tmp_path / "cache")

    with pytest.raises(DerivedMarketStoreError, match="cross-section preflight found 2 defects"):
        _validate_complete_observed_cross_sections(
            rows=rows,
            membership=membership,
            start_date="2020-01-01",
            end_date="2020-01-03",
            acquisition_cache=cache,
        )

    audit = json.loads((cache.root / "cross_section_audit.json").read_text())
    assert audit["passed"] is False
    assert audit["error_count"] == 2
    assert {item["type"] for item in audit["error_examples"]} == {
        "NO_ELIGIBLE_HISTORY",
        "INCOMPLETE_OBSERVED_CROSS_SECTION",
    }
