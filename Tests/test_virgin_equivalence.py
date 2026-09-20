from __future__ import annotations

import pytest

from MTS_V4.virgin_equivalence import (
    EquivalenceProtocolError,
    VirginCandidate,
    blinded_pair,
    build_hybrid_appeal_context,
    deterministic_select_virgins,
    freeze_arm_manifest,
    freeze_starting_package,
    qualify_experiment,
    verify_identical_start,
)


def _candidate(symbol: str, **changes) -> VirginCandidate:
    values = dict(
        subject_id=symbol,
        partition="DISCOVERY",
        prior_sol_exposure=False,
        prior_gemini_exposure=False,
        prior_campaign_exposure=False,
        starting_data_available=True,
    )
    values.update(changes)
    return VirginCandidate(**values)


def _start(symbol="ABC"):
    return freeze_starting_package(symbol, {
        "mission": "frozen mission",
        "subject": {"subject_id": symbol},
        "evidence": [{"evidence_id": "e1"}],
        "available_analysis_methods": [{"method_id": "m1"}],
        "starting_state": {"state": "virgin"},
    })


def test_selection_is_deterministic_and_excludes_exposed_tickers():
    rows = [_candidate("AAA"), _candidate("BBB"), _candidate("CCC"), _candidate("DDD"),
            _candidate("SOLX", prior_sol_exposure=True), _candidate("VER", partition="VERIFICATION_A")]
    first = deterministic_select_virgins(rows, protocol_seed="frozen-v1")
    second = deterministic_select_virgins(reversed(rows), protocol_seed="frozen-v1")
    assert first["selected_subject_ids"] == second["selected_subject_ids"]
    assert "SOLX" not in first["selected_subject_ids"]
    assert "VER" not in first["selected_subject_ids"]
    assert len(first["selected_subject_ids"]) == 3


def test_selection_fails_closed_without_three_proven_virgins():
    with pytest.raises(EquivalenceProtocolError, match="fewer than three"):
        deterministic_select_virgins([_candidate("AAA"), _candidate("BBB")], protocol_seed="x")


def test_starting_package_identity_is_hash_enforced():
    a = _start()
    b = dict(a)
    assert verify_identical_start(a, b) == a["sha256"]
    b["package"] = dict(b["package"], mission="changed")
    with pytest.raises(EquivalenceProtocolError):
        verify_identical_start(a, b)


def test_appeal_gets_full_record_but_cannot_restart_direct_sol():
    start = _start()
    context = build_hybrid_appeal_context(
        starting_package=start,
        gemini_work=[{"decision": "d1"}],
        analysis_results=[{"analysis": "r1"}],
        max_sol_calls=2,
        max_sol_spend_usd=2.0,
    )
    assert context["gemini_complete_work_product"]
    assert context["all_hybrid_analysis_results"]
    assert context["authority"]["may_request_bounded_corrective_analysis"] is True
    assert context["authority"]["may_restart_unrestricted_direct_sol_workflow"] is False


def _arm(name: str, start_sha: str):
    return freeze_arm_manifest(
        subject_id="ABC", arm=name, starting_sha256=start_sha,
        artifacts=[{"sha256": "a" * 64}], usage=[{"cost": 1.0}], complete=True,
    )


def test_blinding_removes_arm_identity_and_cost():
    start = _start()
    a = _arm("DIRECT_SOL", start["sha256"])
    b = _arm("GEMINI_SOL_HYBRID", start["sha256"])
    pair = blinded_pair(a, b, salt="secret")
    for label in ("ARM_X", "ARM_Y"):
        assert "arm" not in pair[label]
        assert "usage" not in pair[label]


def test_any_material_direct_sol_miss_is_automatic_failure():
    comparisons = [
        {"materially_equivalent": True, "material_direct_sol_finding_missed": False,
         "disqualifying_false_hybrid_promotion": False},
        {"materially_equivalent": True, "material_direct_sol_finding_missed": True,
         "disqualifying_false_hybrid_promotion": False},
        {"materially_equivalent": True, "material_direct_sol_finding_missed": False,
         "disqualifying_false_hybrid_promotion": False},
    ]
    result = qualify_experiment(comparisons, direct_cost_usd=30.0, hybrid_cost_usd=10.0)
    assert result["cost_saving_fraction"] > .35
    assert result["qualified"] is False


def test_35_percent_savings_is_required_after_equivalence():
    comparisons = [{"materially_equivalent": True, "material_direct_sol_finding_missed": False,
                    "disqualifying_false_hybrid_promotion": False} for _ in range(3)]
    assert qualify_experiment(comparisons, direct_cost_usd=30.0, hybrid_cost_usd=19.5)["qualified"] is True
    assert qualify_experiment(comparisons, direct_cost_usd=30.0, hybrid_cost_usd=19.51)["qualified"] is False
