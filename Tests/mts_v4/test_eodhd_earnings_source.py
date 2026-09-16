import json
import urllib.parse

import pytest

from MTS_V4.contracts import SubjectMetadata
from MTS_V4.eodhd_earnings_source import EODHDEarningsCalendarSource


def test_eodhd_earnings_normalizes_through_intake_payload_without_token_provenance():
    captured = {}
    def fetch(url, timeout):
        captured["url"] = url
        return {"earnings": [{"code": "AAPL.US", "report_date": "2025-01-30", "date": "2024-12-31", "before_after_market": "AfterMarket", "actual": 2.40, "estimate": 2.35, "percent": 2.13, "currency": "USD"}]}
    source = EODHDEarningsCalendarSource("secret", "2025-01-01", "2025-12-31", fetch_json=fetch)
    payload = tuple(source.acquire(SubjectMetadata("equity:AAPL", "AAPL", attributes={"security_id": "SEC_AAPL"})))[0]
    assert payload.row_count == 1
    assert payload.payload[0]["security_id"] == "SEC_AAPL"
    assert payload.payload[0]["availability_class"] == "AfterMarket"
    assert "secret" not in json.dumps(payload.provenance)
    assert urllib.parse.parse_qs(urllib.parse.urlparse(captured["url"]).query)["api_token"] == ["secret"]


def test_eodhd_earnings_rejects_duplicate_report_period_identity():
    row = {"code": "AAPL.US", "report_date": "2025-01-30", "date": "2024-12-31", "before_after_market": "AfterMarket", "actual": 2.4, "estimate": 2.3, "percent": 4.35}
    source = EODHDEarningsCalendarSource("secret", "2025-01-01", "2025-12-31", fetch_json=lambda *_: {"earnings": [row, row]})
    with pytest.raises(ValueError, match="duplicate"):
        tuple(source.acquire(SubjectMetadata("equity:AAPL", "AAPL", attributes={"security_id": "SEC_AAPL"})))
