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
