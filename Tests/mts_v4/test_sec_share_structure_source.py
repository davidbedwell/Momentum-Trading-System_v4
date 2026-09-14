from MTS_V4.sec_share_structure_source import normalize_sec_share_structure


def test_sec_share_structure_preserves_point_in_time_and_units_without_inventing_float_shares():
    companyfacts = {
        "facts": {
            "dei": {
                "EntityCommonStockSharesOutstanding": {
                    "units": {
                        "shares": [
                            {
                                "end": "2025-03-31",
                                "val": 12_500_000,
                                "accn": "0000000000-25-000001",
                                "fy": 2025,
                                "fp": "Q1",
                                "form": "10-Q",
                                "filed": "2025-05-05",
                            }
                        ]
                    }
                },
                "EntityPublicFloat": {
                    "units": {
                        "USD": [
                            {
                                "end": "2024-06-28",
                                "val": 87_000_000,
                                "accn": "0000000000-24-000099",
                                "fy": 2024,
                                "fp": "FY",
                                "form": "10-K",
                                "filed": "2024-09-10",
                            }
                        ]
                    }
                },
            }
        }
    }

    rows = normalize_sec_share_structure(
        ticker="TEST",
        cik="0000000001",
        companyfacts=companyfacts,
    )

    shares = next(row for row in rows if row["fact_kind"] == "SHARES_OUTSTANDING")
    public_float = next(row for row in rows if row["fact_kind"] == "PUBLIC_FLOAT_REPORTED")

    assert shares["value"] == 12_500_000
    assert shares["unit"] == "shares"
    assert shares["period_end"] == "2025-03-31"
    assert shares["known_at"] == "2025-05-05"
    assert shares["accession"] == "0000000000-25-000001"

    assert public_float["value"] == 87_000_000
    assert public_float["unit"] == "USD"
    assert public_float["period_end"] == "2024-06-28"
    assert public_float["known_at"] == "2024-09-10"
    assert "float_shares" not in public_float


def test_sec_share_structure_retains_amended_or_duplicate_filing_history_for_analysis_reconciliation():
    companyfacts = {
        "facts": {
            "dei": {
                "EntityCommonStockSharesOutstanding": {
                    "units": {
                        "shares": [
                            {
                                "end": "2025-03-31",
                                "val": 10_000_000,
                                "accn": "A",
                                "form": "10-Q",
                                "filed": "2025-05-01",
                            },
                            {
                                "end": "2025-03-31",
                                "val": 10_100_000,
                                "accn": "B",
                                "form": "10-Q/A",
                                "filed": "2025-05-10",
                            },
                        ]
                    }
                }
            }
        }
    }

    rows = normalize_sec_share_structure(
        ticker="TEST",
        cik="0000000001",
        companyfacts=companyfacts,
    )

    assert [row["accession"] for row in rows] == ["A", "B"]
    assert [row["known_at"] for row in rows] == ["2025-05-01", "2025-05-10"]
