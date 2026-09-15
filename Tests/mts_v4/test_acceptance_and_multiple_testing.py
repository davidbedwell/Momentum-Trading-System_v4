from MTS_V4.acceptance_controls import BLINDED_CONTROLS, deterministic_null
from MTS_V4.multiple_testing import benjamini_hochberg


def test_blinded_control_prompts_do_not_state_expected_direction():
    assert len(BLINDED_CONTROLS) == 5
    assert all("expected" not in control.research_prompt.lower() for control in BLINDED_CONTROLS)


def test_deterministic_null_is_repeatable_and_uses_only_identity_fields():
    rows = ({"security_id": "A", "effective_date": "2025-01-01", "market": 99},)
    first = deterministic_null({"rows": rows}, {})["derived_datasets"]["deterministic_null_dataset"][0]
    second = deterministic_null({"rows": rows}, {})["derived_datasets"]["deterministic_null_dataset"][0]
    assert first["deterministic_null"] == second["deterministic_null"]
    assert 0 <= first["deterministic_null"] <= 1


def test_benjamini_hochberg_adjustment_is_monotone_in_sorted_p_values():
    rows = ({"p": 0.001}, {"p": 0.01}, {"p": 0.04}, {"p": 0.20})
    result = benjamini_hochberg({"rows": rows}, {"p_value_column": "p"})
    adjusted = [row["bh_q_value"] for row in result["derived_datasets"]["bh_adjusted_dataset"]]
    assert adjusted == sorted(adjusted)
    assert all(q >= p["p"] for q, p in zip(adjusted, rows))
