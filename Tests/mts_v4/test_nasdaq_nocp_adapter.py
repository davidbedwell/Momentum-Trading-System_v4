from __future__ import annotations

import json
from pathlib import Path

import pytest

from MTS_V4 import nasdaq_nocp_adapter as adapter


def test_find_rows_and_parse_historical_nocp(monkeypatch):
    payload = {
        "data": {
            "table": {
                "rows": [
                    {"date": "09/11/2026", "nocp": "$123.45"},
                    {"date": "09/10/2026", "nocp": "$120.00"},
                ]
            }
        }
    }

    monkeypatch.setattr(adapter, "_request", lambda url, timeout=30.0: json.dumps(payload).encode())
    result = adapter.fetch_historical_nocp("AMD")
    assert result == {"2026-09-11": "123.45", "2026-09-10": "120.00"}


def test_official_calendar_removes_closed_but_keeps_early_close(monkeypatch):
    html = b"""
    <table>
      <tr><td>September 7, 2026</td><td>Labor Day - U.S.</td><td>Closed</td></tr>
      <tr><td>November 26, 2026</td><td>Thanksgiving Day</td><td>Closed</td></tr>
      <tr><td>November 27, 2026</td><td>Early Close</td><td>1:00 p.m.</td></tr>
    </table>
    """
    monkeypatch.setattr(adapter, "_request", lambda url, timeout=30.0: html)
    closed = adapter.fetch_nasdaq_closed_dates(years=[2026])
    assert "2026-09-07" in closed
    assert "2026-11-26" in closed
    assert "2026-11-27" not in closed


def test_build_snapshot_preserves_missing_nocp_session(monkeypatch):
    monkeypatch.setattr(
        adapter,
        "fetch_nasdaq_closed_dates",
        lambda years: {"2026-09-07"},
    )
    monkeypatch.setattr(
        adapter,
        "fetch_historical_nocp",
        lambda ticker: {
            "2026-09-08": "100.00",
            "2026-09-10": "102.00",
            "2026-09-11": "103.00",
        },
    )
    snapshot = adapter.build_authoritative_snapshot(
        ticker="AMD",
        source_subject_id="equity:AMD",
        start_date="2026-09-08",
        end_date="2026-09-11",
        share_multipliers={},
    )
    rows = snapshot["sessions"]
    assert [row["session_date"] for row in rows] == [
        "2026-09-08",
        "2026-09-09",
        "2026-09-10",
        "2026-09-11",
    ]
    assert rows[1]["nocp"] is None
    assert all(row["source_identity"] == "NASDAQ_NOCP" for row in rows)
    assert all(row["mandatory_share_multiplier"] == "1" for row in rows)


def test_share_multiplier_file(tmp_path: Path):
    path = tmp_path / "actions.json"
    path.write_text('{"2026-10-01":"2"}', encoding="utf-8")
    assert adapter.load_share_multipliers(path) == {"2026-10-01": "2"}


def test_calendar_fails_closed_when_requested_year_absent(monkeypatch):
    monkeypatch.setattr(
        adapter,
        "_request",
        lambda url, timeout=30.0: b"<table><tr><td>January 1, 2026</td><td>Closed</td></tr></table>",
    )
    with pytest.raises(adapter.NasdaqNocpAdapterError):
        adapter.fetch_nasdaq_closed_dates(years=[2027])
