from MTS_V4.contracts import SubjectMetadata
from MTS_V4.sec_share_structure_source import (
    SEC_COMPANYFACTS_URL,
    SEC_TICKER_MAP_URL,
    SecEdgarShareStructureSource,
    normalize_sec_share_structure,
    resolve_sec_issuer_ciks,
)


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


def test_xom_resolves_explicit_historical_and_current_issuer_ciks():
    ticker_map = {
        "0": {
            "ticker": "XOM",
            "cik_str": 2115436,
            "title": "ExxonMobil Holdings Corp",
        }
    }

    resolved = resolve_sec_issuer_ciks("XOM", ticker_map)

    assert [item[0] for item in resolved] == ["0000034088", "0002115436"]
    assert resolved[-1][1] == "ExxonMobil Holdings Corp"
    assert resolved[-1][2] == "EXPLICIT_ISSUER_LINEAGE_AND_CURRENT_SEC_TICKER_MAP"


def test_muln_resolves_explicit_historical_cik_when_missing_from_current_ticker_map():
    resolved = resolve_sec_issuer_ciks("MULN", {})

    assert resolved == (("0001499961", None, "EXPLICIT_ISSUER_LINEAGE"),)


def test_sec_source_combines_explicit_issuer_lineage_without_inventing_science(monkeypatch):
    ticker_map = {
        "0": {
            "ticker": "XOM",
            "cik_str": 2115436,
            "title": "ExxonMobil Holdings Corp",
        }
    }
    old_facts = {
        "entityName": "EXXON MOBIL CORP",
        "facts": {
            "dei": {
                "EntityCommonStockSharesOutstanding": {
                    "units": {
                        "shares": [
                            {
                                "end": "2025-03-31",
                                "val": 4_000_000_000,
                                "accn": "OLD",
                                "form": "10-Q",
                                "filed": "2025-05-01",
                            }
                        ]
                    }
                }
            }
        },
    }
    new_facts = {
        "entityName": "ExxonMobil Holdings Corp",
        "facts": {
            "dei": {
                "EntityCommonStockSharesOutstanding": {
                    "units": {
                        "shares": [
                            {
                                "end": "2026-06-30",
                                "val": 4_100_000_000,
                                "accn": "NEW",
                                "form": "10-Q",
                                "filed": "2026-08-03",
                            }
                        ]
                    }
                }
            }
        },
    }

    def fake_get_json(url):
        if url == SEC_TICKER_MAP_URL:
            return ticker_map
        if url == SEC_COMPANYFACTS_URL.format(cik="0000034088"):
            return old_facts
        if url == SEC_COMPANYFACTS_URL.format(cik="0002115436"):
            return new_facts
        raise AssertionError(url)

    monkeypatch.setattr("MTS_V4.sec_share_structure_source._get_json", fake_get_json)

    payload = next(iter(SecEdgarShareStructureSource().acquire(SubjectMetadata(subject_id="equity:XOM", ticker="XOM"))))
    rows = list(payload.payload)

    assert [row["cik"] for row in rows] == ["0000034088", "0002115436"]
    assert [row["known_at"] for row in rows] == ["2025-05-01", "2026-08-03"]
    assert payload.coverage_start == "2025-05-01"
    assert payload.coverage_end == "2026-08-03"
    assert payload.provenance["issuer_ciks"] == ["0000034088", "0002115436"]
    assert payload.provenance["issuer_lineage_policy"] == "EXPLICIT_PROVENANCE_ONLY_NO_HEURISTIC_SUCCESSION_INFERENCE"
