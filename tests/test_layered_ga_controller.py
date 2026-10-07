from Core.layered_ga.architecture import Stage
from Core.layered_ga.controller import (
    DurabilityReceipt, GateDecision, GateResult, RunState,
    advancement_allowed, destructive_action_allowed, prerequisites_for_stage,
    terminal_state,
)


def test_stage0_and_stage1_independent_but_stage2_waits_for_both():
    assert prerequisites_for_stage(Stage.ARCHAEOLOGY) == frozenset()
    assert prerequisites_for_stage(Stage.CONTEXT_MAP) == frozenset()
    assert prerequisites_for_stage(Stage.OPPORTUNITY) == frozenset({Stage.ARCHAEOLOGY, Stage.CONTEXT_MAP})


def test_only_clean_pass_plus_durability_advances():
    good=GateResult(GateDecision.PASS,"v1")
    assert advancement_allowed(good, True)
    assert not advancement_allowed(good, False)
    assert not advancement_allowed(GateResult(GateDecision.FAIL,"v1"), True)
    assert not advancement_allowed(GateResult(GateDecision.AMBIGUOUS,"v1"), True)
    assert not advancement_allowed(GateResult(GateDecision.PASS,"v1",("x",)), True)


def test_scientific_parameter_change_blocks_advance():
    g=GateResult(GateDecision.PASS,"v1",scientific_parameters_changed=True)
    assert not advancement_allowed(g, True)


def test_failure_modes_stop_not_retune():
    assert terminal_state(GateResult(GateDecision.FAIL,"v1"), True) is RunState.STOPPED_SCIENTIFIC
    assert terminal_state(GateResult(GateDecision.AMBIGUOUS,"v1"), True) is RunState.STOPPED_REVIEW
    assert terminal_state(GateResult(GateDecision.ERROR,"v1"), True) is RunState.STOPPED_ENGINEERING


def test_durability_failure_overrides_gate():
    assert terminal_state(GateResult(GateDecision.PASS,"v1"), False) is RunState.DURABILITY_FAILED


def test_controller_cannot_self_authorize_destruction():
    r=DurabilityReceipt(True,True,True,True)
    assert not destructive_action_allowed(r, False)
    assert destructive_action_allowed(r, True)


def test_incomplete_backup_never_allows_destruction():
    r=DurabilityReceipt(True,False,True,True)
    assert not destructive_action_allowed(r, True)
