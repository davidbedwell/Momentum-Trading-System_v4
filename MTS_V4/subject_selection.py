from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Mapping, Sequence

from .adaptive_batch import SubjectEligibilityEnvelope
from .cross_subject_memory import CrossSubjectScientificMemory
from .openai_compatible_provider import OpenAICompatibleResearchDirector


@dataclass(frozen=True, slots=True)
class RDSubjectSelectionDecision:
    subject_id: str
    rationale: str


class SolAdaptiveSubjectSelector:
    """Ask the approved AI RD to choose the next subject scientifically.

    Deterministic code supplies the human eligibility envelope and validates the
    returned identity/rationale. It never ranks or chooses a ticker itself.
    """

    def __init__(
        self,
        *,
        rd: OpenAICompatibleResearchDirector,
        scientific_memory: CrossSubjectScientificMemory,
        eligibility: SubjectEligibilityEnvelope,
    ) -> None:
        self._rd = rd
        self._scientific_memory = scientific_memory
        self._eligibility = eligibility

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
            )
            if not defects:
                eligible_candidates.append(subject_id)
        if not eligible_candidates:
            raise ValueError("no objectively eligible candidate subjects remain")

        payload = {
            "operation": "SELECT_NEXT_RESEARCH_SUBJECT",
            "mission": mission,
            "eligible_candidate_subject_ids": eligible_candidates,
            "previously_seen_subject_ids": list(previously_seen),
            "cross_subject_scientific_memory": memory_context,
            "human_governance": {
                "selection_authority": "AI_RD",
                "objective_eligibility_enforced_by_code": True,
                "scientific_guideline": (
                    "Choose the previously unseen subject that is most scientifically useful next given accumulated "
                    "knowledge. Across selections, seek enough variation to discriminate whether relationships "
                    "generalize, reverse, weaken, or depend on subject characteristics. Avoid redundant selections "
                    "whose similarity contributes little new discrimination. Prior hypotheses are context, not a "
                    "mandatory agenda; replication/discrimination, independent exploration, or both are permitted."
                ),
            },
            "required_schema": {
                "subject_id": "exact string from eligible_candidate_subject_ids",
                "rationale": "nonblank scientific reason this subject is useful next given current knowledge",
            },
        }
        raw = self._rd._chat_completion(
            [
                {
                    "role": "system",
                    "content": (
                        "You are the MTS scientific Research Director. Select the next research subject. "
                        "Scientific subject selection is your authority. Deterministic code only enforces the supplied "
                        "objective eligibility envelope. Return one JSON object only."
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
        if not isinstance(subject_id, str) or subject_id not in eligible_candidates:
            raise ValueError("RD selected a subject outside the supplied objectively eligible candidate set")
        if not isinstance(rationale, str) or not rationale.strip():
            raise ValueError("RD subject-selection rationale must be nonblank")
        return RDSubjectSelectionDecision(subject_id=subject_id, rationale=rationale.strip())
