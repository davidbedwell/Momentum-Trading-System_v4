from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping

from .batch_contracts import BatchResearchDecision


class RollingProgramStateError(RuntimeError):
    pass


class RollingProgramDisposition(str, Enum):
    CONTINUE_EXPLORATION = "CONTINUE_EXPLORATION"
    RUN_BLIND_VALIDATION = "RUN_BLIND_VALIDATION"
    RESUME_EXPLORATION = "RESUME_EXPLORATION"
    AWAIT_NEW_EVIDENCE = "AWAIT_NEW_EVIDENCE"
    SUBJECT_COMPLETE = "SUBJECT_COMPLETE"


@dataclass(frozen=True, slots=True)
class RollingProgramInstruction:
    """AI-authored scientific lifecycle transition, mechanically represented."""

    disposition: RollingProgramDisposition
    hypothesis_id: str | None = None
    rationale: str = ""


def rolling_program_instruction(decision: BatchResearchDecision) -> RollingProgramInstruction:
    """Decode the RD-authored lifecycle instruction without inventing a transition."""

    raw = decision.research_state.get("rolling_program")
    if not isinstance(raw, Mapping):
        raise RollingProgramStateError(
            "research_state.rolling_program is required for rolling research decisions"
        )
    disposition_raw = raw.get("disposition")
    try:
        disposition = RollingProgramDisposition(str(disposition_raw))
    except ValueError as exc:
        raise RollingProgramStateError(
            f"invalid rolling program disposition: {disposition_raw!r}"
        ) from exc
    hypothesis_id = raw.get("hypothesis_id")
    if hypothesis_id is not None and (
        not isinstance(hypothesis_id, str) or not hypothesis_id.strip()
    ):
        raise RollingProgramStateError("rolling_program.hypothesis_id must be nonblank or null")
    rationale = raw.get("rationale", "")
    if not isinstance(rationale, str):
        raise RollingProgramStateError("rolling_program.rationale must be a string")

    if disposition is RollingProgramDisposition.RUN_BLIND_VALIDATION and hypothesis_id is None:
        raise RollingProgramStateError(
            "RUN_BLIND_VALIDATION requires rolling_program.hypothesis_id"
        )
    if disposition in {
        RollingProgramDisposition.CONTINUE_EXPLORATION,
        RollingProgramDisposition.RESUME_EXPLORATION,
    } and not decision.continue_research:
        raise RollingProgramStateError(
            f"{disposition.value} requires continue_research=true"
        )
    if disposition in {
        RollingProgramDisposition.AWAIT_NEW_EVIDENCE,
        RollingProgramDisposition.SUBJECT_COMPLETE,
    } and decision.continue_research:
        raise RollingProgramStateError(
            f"{disposition.value} requires continue_research=false"
        )
    return RollingProgramInstruction(
        disposition=disposition,
        hypothesis_id=hypothesis_id,
        rationale=rationale,
    )
