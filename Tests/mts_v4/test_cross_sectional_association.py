from __future__ import annotations

import pytest

from MTS_V4.cross_sectional_association import cross_sectional_association


def test_cross_sectional_association_measures_each_date_then_temporal_uncertainty():
    rows = []
    for day in range(12):
        effective_date = f"2026-01-{day + 1:02d}"
        for security, score in (("A", 0.1), ("B", 0.4), ("C", 0.7), ("D", 0.9)):
            rows.append(
                {
                    "security_id": security,
                    "effective_date": effective_date,
                    "score": score,
                    "forward": score * 0.05 + day * 0.0001,
                }
            )

    result = cross_sectional_association(
        {"joined_panel": rows},
        {
            "predictor_column": "score",
            "outcome_column": "forward",
            "date_column": "effective_date",
            "association_type": "spearman",
            "newey_west_max_lag": 2,
        },
    )

    assert result["input_rows"] == 48
    assert result["cross_sections_with_defined_association"] == 12
    assert result["equal_date_association"]["mean"] == pytest.approx(1.0)
    assert result["sign_fraction"] == 1.0
    assert result["year_stability"]["2026"]["n_dates"] == 12
    assert "dated_associations" not in result
    assert result["derived_dataset_catalog"]["dated_cross_sectional_associations"]["row_count"] == 12


def test_cross_sectional_association_does_not_treat_constant_cross_section_as_signal():
    rows = [
        {"effective_date": "2026-01-02", "score": 1.0, "forward": value}
        for value in (0.1, 0.2, 0.3)
    ]
    result = cross_sectional_association(
        {"joined_panel": rows},
        {
            "predictor_column": "score",
            "outcome_column": "forward",
            "date_column": "effective_date",
            "association_type": "pearson",
            "newey_west_max_lag": 0,
        },
    )
    assert result["cross_sections_with_defined_association"] == 0
    assert result["equal_date_association"]["mean"] is None
