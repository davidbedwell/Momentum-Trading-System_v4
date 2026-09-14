from MTS_V4.share_structure_analysis import sec_share_structure_context


def test_share_structure_uses_only_facts_known_by_each_market_date():
    daily = [
        {"date": "2026-01-10", "close": 10.0, "volume": 100_000},
        {"date": "2026-02-10", "close": 11.0, "volume": 200_000},
        {"date": "2026-03-10", "close": 12.0, "volume": 300_000},
    ]
    sec = [
        {
            "fact_kind": "SHARES_OUTSTANDING",
            "known_at": "2026-01-20",
            "period_end": "2026-01-15",
            "unit": "shares",
            "value": 10_000_000,
        },
        {
            "fact_kind": "SHARES_OUTSTANDING",
            "known_at": "2026-03-01",
            "period_end": "2026-02-25",
            "unit": "shares",
            "value": 20_000_000,
        },
        {
            "fact_kind": "PUBLIC_FLOAT_REPORTED",
            "known_at": "2026-03-01",
            "period_end": "2026-02-25",
            "unit": "USD",
            "value": 50_000_000,
        },
    ]
    result = sec_share_structure_context({"daily": daily, "sec": sec}, {})
    panel = result["derived_datasets"]["sec_share_structure_panel"]
    assert panel[0]["shares_outstanding_known_at_t"] is None
    assert panel[1]["shares_outstanding_known_at_t"] == 10_000_000
    assert panel[2]["shares_outstanding_known_at_t"] == 20_000_000
    assert panel[2]["volume_over_shares_outstanding"] == 0.015
    assert result["sec_public_float_reported_facts"][0]["unit"] == "USD"


def test_same_day_conflicting_share_facts_are_not_silently_selected():
    daily = [{"date": "2026-03-10", "close": 10.0, "volume": 100_000}]
    sec = [
        {"fact_kind": "SHARES_OUTSTANDING", "known_at": "2026-03-01", "period_end": "2026-02-20", "unit": "shares", "value": 10_000_000},
        {"fact_kind": "SHARES_OUTSTANDING", "known_at": "2026-03-01", "period_end": "2026-02-25", "unit": "shares", "value": 12_000_000},
    ]
    panel = sec_share_structure_context({"daily": daily, "sec": sec}, {})["derived_datasets"]["sec_share_structure_panel"]
    assert panel[0]["shares_outstanding_known_at_t"] is None
    assert panel[0]["shares_outstanding_ambiguous"] is True
