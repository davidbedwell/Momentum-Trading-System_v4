from __future__ import annotations

import threading

from MTS_V4.derived_market_updater import _attach_membership_and_identity
from MTS_V4.universe_membership import IntervalMembership, MembershipInterval


class CoordinatedSource:
    source_identity = "TEST"

    def __init__(self, workers: int) -> None:
        self._barrier = threading.Barrier(workers, timeout=5)
        self._lock = threading.Lock()
        self.active = 0
        self.maximum_active = 0

    def fetch(self, *, ticker: str, start_date: str, end_date: str):
        with self._lock:
            self.active += 1
            self.maximum_active = max(self.maximum_active, self.active)
        self._barrier.wait()
        with self._lock:
            self.active -= 1
        return ({
            "date": "2020-01-02",
            "open": 1.0,
            "high": 1.0,
            "low": 1.0,
            "close": 1.0,
            "volume": 1.0,
        },)


def test_market_acquisition_uses_bounded_parallelism_and_restores_order():
    membership = IntervalMembership(tuple(
        MembershipInterval(
            security_id=f"SEC-{number}",
            ticker=f"T{number}",
            start_date="2020-01-01",
            source_identity="TEST",
        )
        for number in range(6)
    ))
    source = CoordinatedSource(workers=3)

    rows = _attach_membership_and_identity(
        membership=membership,
        source=source,
        start_date="2020-01-01",
        end_date="2020-01-03",
        shares_source=None,
        download_workers=3,
    )

    assert source.maximum_active == 3
    assert [row["security_id"] for row in rows] == [f"SEC-{number}" for number in range(6)]
