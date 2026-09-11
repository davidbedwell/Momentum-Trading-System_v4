from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Mapping, Sequence

from .adaptive_batch import SubjectEligibilityEnvelope
from .cross_subject_memory import CrossSubjectScientificMemory
from .openai_compatible_provider import OpenAICompatibleResearchDirector


_ALLOWED_MODES = {"EXPLORATION", "VALIDATION_FIRST"}


@dataclass(frozen=True, slots=True)
class RDSubjectSelectionDecision:
    subject_id: str
    rationale: str
    mode: str = "EXPLORATION"
    hypothesis_id: str | None = None

    def __post_init__(self) -> None:
        if self.mode not in _ALLOWED_MODES:
            raise ValueError(f"unsupported subject selection mode: {self.mode}")
        if self.mode == "VALIDATION_FIRST":
            if not isinstance(self.hypothesis_id, str) or not self.hypothesis_id.strip():
                raise ValueError("VALIDATION_FIRST selection requires nonblank hypothesis_id")
        elif self.hypothesis_id is not None:
            raise ValueError("EXPLORATION selection must not bind a validation hypothesis_id")


class SolAdaptiveSubjectSelector:
    """Ask the approved AI RD to choose the next subject scientifically.

    Deterministic code supplies the human eligibility envelope and validates the
    returned identity/rationale/phase representation. It never ranks or chooses
    a ticker, hypothesis, or scientific role itself.

    Previously researched subjects remain eligible for EXPLORATION. Prior MTS
    exposure blocks only retrospective blind VALIDATION_FIRST, where unseen
    status is part of the objective protocol integrity requirement.

    ``validatable_hypothesis_ids`` is an objective execution-capability envelope.
    When supplied, Sol may choose VALIDATION_FIRST only for one of those exact
    already-frozen hypotheses. An empty set means no blind-validation protocol is
    mechanically executable in the current runner, so only EXPLORATION is a valid
    role. ``None`` preserves the legacy unrestricted selection contract.
    """

    def __init__(
        self,
        *,
        rd: OpenAICompatibleResearchDirector,
        scientific_memory: CrossSubjectScientificMemory,
        eligibility: SubjectEligibilityEnvelope,
        validatable_hypothesis_ids: frozenset[str] | None = None,
    ) -> None:
        self._rd = rd
        self._scientific_memory = scientific_memory
        self._eligibility = eligibility
        self._validatable_hypothesis_ids = validatable_hypothesis_ids

    def choose_next(
        self,
        *,
        mission: str,
        previously_seen: Sequence[str],
        candidate_subject_ids: Sequence[str],
        available_sources_by_subject: Mapping[str, Sequence[str]] | None = None,
    ) -> RDSubjectSelectionDecision:
        if not candidate_subject_ids:
            raise ValueError("candidate_subject_ids cannot be empty")
        context_method = getattr(self._scientific_memory, "context", None)
        memory_context = context_method() if callable(context_method) else {
            "records": [record.compact_context() for record in self._scientific_memory.records()],
            "frontier": (
                self._scientific_memory.frontier().compact_context()
                if self._scientific_memory.frontier() is not None
                else None
            ),
        }
        eligible_candidates: list[str] = []
        available_sources_by_subject = available_sources_by_subject or {}
        for subject_id in candidate_subject_ids:
            defects = self._eligibility.objective_defects(
                subject_id=subject_id,
                previously_seen=previously_seen,
                available_sources=available_sources_by_subject.get(subject_id, ()),
                require_unseen=False,
            )
            if not defects:
                eligible_candidates.append(subject_id)
        if not eligible_candidates:
            raise ValueError("no objectively eligible candidate subjects remain")

        validation_capability_constrained = self._validatable_hypothesis_ids is not None
        validatable_ids = sorted(self._validatable_hypothesis_ids or ())
        allowed_modes = (
            ["EXPLORATION"]
            if validation_capability_constrained and not validatable_ids
            else ["EXPLORATION", "VALIDATION_FIRST"]
        )

        payload = {
            "operation": "SELECT_NEXT_RESEARCH_SUBJECT",
            "mission": mission,
            "eligible_candidate_subject_ids": eligible_candidates,
            "previously_researched_subject_ids": list(previously_seen),
            "cross_subject_scientific_memory": memory_context,
            "human_governance": {
                "selection_authority": "AI_RD",
                "objective_eligibility_enforced_by_code": True,
                "allowed_selection_modes": allowed_modes,
                "mechanically_executable_validation_hypothesis_ids": validatable_ids,
                "blind_validation_requires_unseen_subject": True,
                "exploration_may_revisit_previously_researched_subject": True,
                "scientific_guideline": (
                    "Choose the subject that is most scientifically useful next given accumulated knowledge. "
                    "Previously researched subjects remain eligible for EXPLORATION when revisiting them is useful; "
                    "a prior failure or absence of findings is not an exploration exclusion. Across selections, seek "
                    "enough variation to discriminate whether relationships generalize, reverse, weaken, or depend on "
                    "subject characteristics, but revisit a prior subject when the Research Frontier makes that the "
                    "better scientific choice. Prior hypotheses are context, not a mandatory agenda. If a prior frozen "
                    "hypothesis is scientifically suitable for a retrospective blind test, VALIDATION_FIRST may be "
                    "chosen only on a subject absent from previously_researched_subject_ids and only when its exact "
                    "hypothesis_id appears in mechanically_executable_validation_hypothesis_ids. The blind trial must "
                    "be completed and scored before unrestricted exploration begins on that same ticker."
                ),
            },
            "required_schema": {
                "subject_id": "exact string from eligible_candidate_subject_ids",
                "rationale": "nonblank scientific reason this subject is useful next given current knowledge",
                "mode": "one exact string from human_governance.allowed_selection_modes",
                "hypothesis_id": (
                    "null for EXPLORATION; for VALIDATION_FIRST, exact string from "
                    "human_governance.mechanically_executable_validation_hypothesis_ids"
                ),
            },
        }
        raw = self._rd._chat_completion(
            [
                {
                    "role": "system",
                    "content": (
                        "You are the MTS scientific Research Director. Select the next research subject and whether "
                        "its scientifically useful first role is unrestricted EXPLORATION or blind VALIDATION_FIRST "
                        "of an existing frozen hypothesis. Scientific subject/role selection is your authority. "
                        "Deterministic code only enforces the supplied objective eligibility and phase-order rules. "
                        "Return one JSON object only."
                    ),
                },
                {"role": "user", "content": json.dumps(payload, sort_keys=True, default=str)},
            ]
        )
        try:
            decoded = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"subject selection response is not valid JSON: {exc}") from exc
        subject_id = decoded.get("subject_id")
        rationale = decoded.get("rationale")
        mode = decoded.get("mode", "EXPLORATION")
        hypothesis_id = decoded.get("hypothesis_id")
        if not isinstance(subject_id, str) or subject_id not in eligible_candidates:
            raise ValueError("RD selected a subject outside the supplied objectively eligible candidate set")
        if not isinstance(rationale, str) or not rationale.strip():
            raise ValueError("RD subject-selection rationale must be nonblank")
        if not isinstance(mode, str) or mode not in _ALLOWED_MODES:
            raise ValueError("RD subject-selection mode must be EXPLORATION or VALIDATION_FIRST")
        if mode not in allowed_modes:
            raise ValueError(
                "RD selected a subject role that is not mechanically executable in the current runner"
            )
        if mode == "VALIDATION_FIRST":
            if subject_id in set(previously_seen):
                raise ValueError("VALIDATION_FIRST requires a subject unseen by prior MTS research")
            if not isinstance(hypothesis_id, str) or not hypothesis_id.strip():
                raise ValueError("VALIDATION_FIRST selection requires nonblank hypothesis_id")
            if (
                validation_capability_constrained
                and hypothesis_id not in self._validatable_hypothesis_ids
            ):
                raise ValueError(
                    "RD selected VALIDATION_FIRST with a hypothesis that is not mechanically executable"
                )
        else:
            hypothesis_id = None
        return RDSubjectSelectionDecision(
            subject_id=subject_id,
            rationale=rationale.strip(),
            mode=mode,
            hypothesis_id=hypothesis_id.strip() if isinstance(hypothesis_id, str) else None,
        )
