from __future__ import annotations

import pytest

from MTS_V4.cross_evidence import cross_evidence_method_spec, temporal_correlation


def test_temporal_correlation_accepts_two_series_from_same_evidence_dataset():
    evidence_id = "evidence:equity:AAPL:ohlcv"
    rows = (
        {"date": "2026-01-01", "volume": 10.0, "high": 100.0},
        {"date": "2026-01-02", "volume": 20.0, "high": 110.0},
        {"date": "2026-01-03", "volume": 30.0, "high": 120.0},
    )

    result = temporal_correlation(
        {evidence_id: rows},
        {
            "left_evidence_id": evidence_id,
            "right_evidence_id": evidence_id,
            "left_time_column": "date",
            "right_time_column": "date",
            "left_value_column": "volume",
            "right_value_column": "high",
            "period": "day",
            "left_aggregation": "mean",
            "right_aggregation": "mean",
            "correlation_type": "pearson",
        },
    )

    assert result["left_evidence_id"] == evidence_id
    assert result["right_evidence_id"] == evidence_id
    assert result["paired_period_count"] == 3
    assert result["correlation"] == pytest.approx(1.0)


def test_temporal_correlation_catalog_discloses_same_dataset_capability():
    spec = cross_evidence_method_spec()
    meanings = {parameter.name: parameter.meaning for parameter in spec.parameters}

    assert "same or different supplied evidence datasets" in spec.description
    assert "may equal right_evidence_id" in meanings["left_evidence_id"]
    assert "may equal left_evidence_id" in meanings["right_evidence_id"]
