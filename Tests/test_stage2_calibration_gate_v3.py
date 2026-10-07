from Core.layered_ga.stage2_calibration_gate_v3 import certify_calibration, SHAPES, EFFECTS


def valid_cases():
    return [
        {
            "family": family, "shape": shape, "effect": effect,
            "target_baseline_evaluated": True,
            "target_region_positive_lcb95": effect == .02,
            "target_region_overlap": effect == .02,
            "null_target_specific_recovery": False,
            "ga_preserves_or_improves": effect == .02,
            "full_63_day_curve": True,
            "independent_effective_n_verified": True,
            "causal_costs_verified": True,
            "long_short_evaluated_separately": True,
        }
        for family in ("MOMENTUM", "BREAKOUT")
        for shape in SHAPES
        for effect in EFFECTS
    ]


def test_full_evidence_can_pass_structural_gate():
    result = certify_calibration(valid_cases(), frozen_parameters_verified=True)
    assert result["decision"] == "PASS"


def test_missing_null_fails_closed():
    cases = [x for x in valid_cases() if not (x["family"] == "MOMENTUM" and x["shape"] == "FAST" and x["effect"] == 0)]
    assert certify_calibration(cases, frozen_parameters_verified=True)["decision"] == "FAIL"


def test_false_null_recovery_fails_closed():
    cases = valid_cases()
    cases[0]["null_target_specific_recovery"] = True
    assert certify_calibration(cases, frozen_parameters_verified=True)["decision"] == "FAIL"


def test_missing_full_path_or_strong_lcb_fails_closed():
    cases = valid_cases()
    cases[0]["full_63_day_curve"] = False
    assert certify_calibration(cases, frozen_parameters_verified=True)["decision"] == "FAIL"
    cases = valid_cases()
    cases[4]["target_region_positive_lcb95"] = False
    assert certify_calibration(cases, frozen_parameters_verified=True)["decision"] == "FAIL"


def test_unverified_frozen_parameters_fail_closed():
    assert certify_calibration(valid_cases(), frozen_parameters_verified=False)["decision"] == "FAIL"


def test_old_result_schema_cannot_be_certified():
    legacy = [{"family": "MOMENTUM", "shape": "FAST", "effect": .02, "best_ga": .02}]
    assert certify_calibration(legacy, frozen_parameters_verified=True)["decision"] == "FAIL"
