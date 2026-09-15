from MTS_V4.cross_sectional_statistics import cohort_effect


def test_cohort_effect_uses_equal_date_differences_and_reports_hac_uncertainty():
    rows = []
    for day in range(20):
        date = f"2025-01-{day + 1:02d}"
        rows.extend((
            {"effective_date": date, "score": 0.9, "future": 0.02 + day * 0.0001},
            {"effective_date": date, "score": 0.8, "future": 0.01 + day * 0.0001},
            {"effective_date": date, "score": 0.2, "future": -0.01 + day * 0.0001},
            {"effective_date": date, "score": 0.1, "future": -0.02 + day * 0.0001},
        ))
    result = cohort_effect(
        {"panel": rows},
        {"cohort_column": "score", "outcome_column": "future", "threshold": 0.5, "direction": "GE", "newey_west_max_lag": 3},
    )
    assert result["selected_n"] == 40
    assert result["control_n"] == 40
    assert result["equal_date_paired_difference"]["n_dates"] == 20
    assert result["equal_date_paired_difference"]["mean"] > 0
