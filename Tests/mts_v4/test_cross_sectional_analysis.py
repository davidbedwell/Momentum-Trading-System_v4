from __future__ import annotations

import pytest

from MTS_V4.cross_sectional_analysis import cross_sectional_rank


def test_cross_sectional_rank_operates_within_effective_date():
    rows = (
        {"effective_date": "2026-09-11", "security_id": "A", "ret_252": 0.10},
        {"effective_date": "2026-09-11", "security_id": "B", "ret_252": 0.30},
        {"effective_date": "2026-09-11", "security_id": "C", "ret_252": 0.20},
        {"effective_date": "2026-09-14", "security_id": "A", "ret_252": 0.40},
        {"effective_date": "2026-09-14", "security_id": "B", "ret_252": 0.10},
    )
    result = cross_sectional_rank(
        {"panel": rows},
        {
            "value_column": "ret_252",
            "output_column": "ret_252_percentile",
            "group_by": ["effective_date"],
            "ascending": True,
        },
    )
    ranked = result["derived_datasets"]["cross_sectional_ranked_dataset"]
    first_date = {row["security_id"]: row["ret_252_percentile"] for row in ranked[:3]}
    second_date = {row["security_id"]: row["ret_252_percentile"] for row in ranked[3:]}
    assert first_date == {"A": 0.0, "B": 1.0, "C": 0.5}
    assert second_date == {"A": 1.0, "B": 0.0}


def test_cross_sectional_rank_ties_use_average_rank():
    rows = (
        {"effective_date": "2026-09-11", "security_id": "A", "value": 1.0},
        {"effective_date": "2026-09-11", "security_id": "B", "value": 1.0},
        {"effective_date": "2026-09-11", "security_id": "C", "value": 2.0},
    )
    result = cross_sectional_rank(
        {"panel": rows},
        {
            "value_column": "value",
            "output_column": "pct",
            "group_by": ["effective_date"],
        },
    )
    ranked = result["derived_datasets"]["cross_sectional_ranked_dataset"]
    assert ranked[0]["pct"] == pytest.approx(0.25)
    assert ranked[1]["pct"] == pytest.approx(0.25)
    assert ranked[2]["pct"] == pytest.approx(1.0)
