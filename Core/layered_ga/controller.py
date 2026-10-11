"""Deterministic controller model for the MTS layered research conveyor.

No scientific interpretation belongs here. The controller advances only from
machine-readable PASS gates and stops on scientific failure or ambiguity.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import FrozenSet
from .architecture import Stage, assert_stage_can_run


class RunState(str, Enum):
    PLANNED="PLANNED"
    PREFLIGHT="PREFLIGHT"
    RUNNING="RUNNING"
    EVALUATING="EVALUATING"
    PASS="PASS"
    FAIL="FAIL"
    AMBIGUOUS="AMBIGUOUS"
    ERROR="ERROR"
    FREEZING="FREEZING"
    DURABILITY_VERIFY="DURABILITY_VERIFY"
    NEXT_STAGE="NEXT_STAGE"
    STOPPED_SCIENTIFIC="STOPPED_SCIENTIFIC"
    STOPPED_REVIEW="STOPPED_REVIEW"
    STOPPED_ENGINEERING="STOPPED_ENGINEERING"
    DURABILITY_FAILED="DURABILITY_FAILED"
    WAITING_FOR_COMPUTE_PROVISIONING="WAITING_FOR_COMPUTE_PROVISIONING"


class GateDecision(str, Enum):
    PASS="PASS"
    FAIL="FAIL"
    AMBIGUOUS="AMBIGUOUS"
    ERROR="ERROR"


@dataclass(frozen=True)
class GateResult:
    decision: GateDecision
    gate_version: str
    failed_criteria: tuple[str, ...] = ()
    scientific_parameters_changed: bool = False


def advancement_allowed(gate: GateResult, durability_verified: bool) -> bool:
    return (
        gate.decision is GateDecision.PASS
        and not gate.failed_criteria
        and not gate.scientific_parameters_changed
        and durability_verified
    )


def terminal_state(gate: GateResult, durability_verified: bool) -> RunState:
    if not durability_verified:
        return RunState.DURABILITY_FAILED
    if gate.decision is GateDecision.FAIL:
        return RunState.STOPPED_SCIENTIFIC
    if gate.decision is GateDecision.AMBIGUOUS:
        return RunState.STOPPED_REVIEW
    if gate.decision is GateDecision.ERROR:
        return RunState.STOPPED_ENGINEERING
    return RunState.NEXT_STAGE


def prerequisites_for_stage(stage: Stage) -> FrozenSet[Stage]:
    # Stage 0 and 1 may execute independently/concurrently. Architecture already
    # encodes that Stage 2 requires both.
    from .architecture import CONTRACTS
    return CONTRACTS[stage].requires_frozen


def authorize_stage(stage: Stage, frozen: set[Stage]) -> None:
    assert_stage_can_run(stage, frozen)


@dataclass(frozen=True)
class DurabilityReceipt:
    git_remote_sha_verified: bool
    backup_manifest_verified: bool
    critical_checksums_verified: bool
    source_preserved: bool

    @property
    def verified(self) -> bool:
        return (
            self.git_remote_sha_verified
            and self.backup_manifest_verified
            and self.critical_checksums_verified
        )


def destructive_action_allowed(receipt: DurabilityReceipt, human_authorized_after_verification: bool) -> bool:
    # Controller can never self-authorize destruction.
    return receipt.verified and human_authorized_after_verification


@dataclass(frozen=True)
class ComputeEnvelope:
    available_vcpus: int
    target_vcpus: int = 64
    target_is_provisioned: bool = False

    def __post_init__(self) -> None:
        if self.available_vcpus < 1 or self.target_vcpus < 1:
            raise ValueError("vCPU counts must be positive")


@dataclass(frozen=True)
class ComputeHandoffPackage:
    code_commit_sha: str
    scientific_config_hash: str
    data_manifest_hash: str
    parent_artifact_hashes: tuple[str, ...]
    environment_specified: bool
    bootstrap_specified: bool
    launch_command_specified: bool
    expected_outputs_specified: bool
    gate_specified: bool
    durability_verified: bool

    @property
    def ready(self) -> bool:
        return bool(
            self.code_commit_sha
            and self.scientific_config_hash
            and self.data_manifest_hash
            and self.environment_specified
            and self.bootstrap_specified
            and self.launch_command_specified
            and self.expected_outputs_specified
            and self.gate_specified
            and self.durability_verified
        )


def compute_handoff_required(
    envelope: ComputeEnvelope,
    calibrated_required_vcpus: int | None,
) -> bool:
    """Return True only when calibration says the next exact workload exceeds this host.

    This function does not provision anything and does not guess that 64 vCPU is
    necessary merely because it is available elsewhere.
    """
    if calibrated_required_vcpus is None:
        return False
    return calibrated_required_vcpus > envelope.available_vcpus


def compute_boundary_state(
    envelope: ComputeEnvelope,
    calibrated_required_vcpus: int | None,
    package: ComputeHandoffPackage | None,
) -> RunState:
    if not compute_handoff_required(envelope, calibrated_required_vcpus):
        return RunState.NEXT_STAGE
    if package is None or not package.ready:
        return RunState.STOPPED_ENGINEERING
    # The package waits. The machine does not. Provisioning is always external
    # and requires an explicit human action.
    return RunState.WAITING_FOR_COMPUTE_PROVISIONING


def controller_may_provision_compute() -> bool:
    return False
