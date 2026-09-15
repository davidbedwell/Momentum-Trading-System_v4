from datetime import date, timedelta

from MTS_V4.derived_market_store import InMemoryDerivedMarketStore, UniverseDefinition
from MTS_V4.derived_market_updater import maintain_standard_market_store
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
