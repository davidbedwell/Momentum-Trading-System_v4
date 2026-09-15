from __future__ import annotations

import pytest

from MTS_V4.universe_sources import UniverseSourceError, normalize_current_sp500_rows


def _records(count: int = 500):
    return [
        {
            "Symbol": "BRK.B" if number == 0 else f"T{number}",
            "GICS Sector": "Sector",
            "GICS Sub-Industry": "Industry",
            "Date added": "2000-01-01" if number == 0 else "2020-01-01",
            "CIK": number + 1,
        }
        for number in range(count)
    ]


def test_universe_intake_normalizes_stable_identity_ticker_and_effective_start():
    rows = normalize_current_sp500_rows(
        _records(),
        acquisition_floor="2005-09-14",
        source_identity="TEST",
    )
    first = next(row for row in rows if row["security_id"] == "SEC_CIK_0000000001")
    assert first["ticker"] == "BRK-B"
    assert first["start_date"] == "2005-09-14"
    assert first["source_identity"] == "TEST"


def test_universe_intake_rejects_implausible_constituent_count():
    with pytest.raises(UniverseSourceError, match="unexpected current S&P constituent count"):
        normalize_current_sp500_rows(
            _records(10),
            acquisition_floor="2005-09-14",
            source_identity="TEST",
        )
