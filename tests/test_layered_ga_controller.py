from Core.layered_ga.architecture import Stage
from Core.layered_ga.controller import (
    DurabilityReceipt, GateDecision, GateResult, RunState,
    advancement_allowed, destructive_action_allowed, prerequisites_for_stage,
    terminal_state, ComputeEnvelope, ComputeHandoffPackage, compute_handoff_required,
    compute_boundary_state, controller_may_provision_compute,
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


def _ready_package():
    return ComputeHandoffPackage(
        code_commit_sha="abc",
        scientific_config_hash="science",
        data_manifest_hash="data",
        parent_artifact_hashes=("parent",),
        environment_specified=True,
        bootstrap_specified=True,
        launch_command_specified=True,
        expected_outputs_specified=True,
        gate_specified=True,
        durability_verified=True,
    )


def test_thunder_six_cpu_does_not_assume_64_is_needed():
    env=ComputeEnvelope(available_vcpus=6, target_vcpus=64, target_is_provisioned=False)
    assert not compute_handoff_required(env, None)
    assert not compute_handoff_required(env, 6)
    assert compute_boundary_state(env, 6, None) is RunState.NEXT_STAGE


def test_calibrated_heavy_work_stops_with_package_waiting_not_machine():
    env=ComputeEnvelope(available_vcpus=6, target_vcpus=64, target_is_provisioned=False)
    assert compute_handoff_required(env, 64)
    assert compute_boundary_state(env, 64, _ready_package()) is RunState.WAITING_FOR_COMPUTE_PROVISIONING


def test_incomplete_handoff_package_cannot_claim_ready():
    env=ComputeEnvelope(available_vcpus=6, target_vcpus=64, target_is_provisioned=False)
    assert compute_boundary_state(env, 64, None) is RunState.STOPPED_ENGINEERING


def test_controller_never_provisions_paid_compute():
    assert controller_may_provision_compute() is False

def test_full_conveyor_declares_every_downstream_stage_runner():
    from Core.layered_ga.conveyor import RUNNERS
    assert set(RUNNERS) == set(range(2,11))

def test_full_conveyor_has_no_chat_wait_state_between_scientific_stages():
    from Core.layered_ga.conveyor import STAGE_DIRS
    assert set(STAGE_DIRS) == set(range(0,11))
    assert all('chat' not in x.lower() for x in STAGE_DIRS.values())
