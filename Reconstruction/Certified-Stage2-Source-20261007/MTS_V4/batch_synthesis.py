from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Mapping

from .adaptive_batch import BatchLedger
from .cross_subject_memory import CrossSubjectScientificMemory
from .openai_compatible_provider import OpenAICompatibleResearchDirector


@dataclass(frozen=True, slots=True)
class BatchScientificSynthesis:
    batch_id: str
    synthesis: Mapping[str, object]


class SolBatchScientificSynthesizer:
    """Sol-authored scientific interpretation of an objective three-subject ledger."""

    def __init__(
        self,
        *,
        rd: OpenAICompatibleResearchDirector,
        scientific_memory: CrossSubjectScientificMemory,
    ) -> None:
        self._rd = rd
        self._scientific_memory = scientific_memory

    def synthesize(self, *, mission: str, ledger: BatchLedger) -> BatchScientificSynthesis:
        context_method = getattr(self._scientific_memory, "context", None)
        memory_context = context_method() if callable(context_method) else {
            "records": [record.compact_context() for record in self._scientific_memory.records()],
            "frontier": (
                self._scientific_memory.frontier().compact_context()
                if self._scientific_memory.frontier() is not None
                else None
            ),
        }
        payload = {
            "operation": "SYNTHESIZE_THREE_SUBJECT_BATCH",
            "mission": mission,
            "batch_ledger": ledger.compact_context(),
            "cross_subject_scientific_memory": memory_context,
            "instructions": [
                "Interpret the batch scientifically; deterministic ledger fields are facts, not conclusions.",
                "Identify relationships replicated, contradicted, not tested, or plausibly conditional/regime-dependent.",
                "Identify new cross-subject candidate generalizations without treating repetition alone as verification.",
                "Identify subject-specific anomalies and changes that should be made to the Research Frontier.",
                "Assess whether the chosen subjects provided useful scientific discrimination.",
                "Recommend the next scientific subject-selection direction, but do not choose outside the later supplied eligibility envelope.",
                "For every subject with zero promoted findings, diagnose why. Distinguish no surviving relationship, weak/inconsistent effect, conflicting evidence, inadequate history/sample, unusable source fields/data quality, unavailable Analysis capability, tentative hypothesis not appropriate for promotion, need for future blind validation, scientific progression failure/stall, and representation/system failure as applicable.",
                "Prior-subject hypotheses are context rather than a mandatory agenda. Do not anchor the batch synthesis to the earliest discovered relationship.",
            ],
            "required_schema": {
                "replicated_relationships": "array",
                "contradicted_relationships": "array",
                "untested_relationships": "array with reasons",
                "conditional_or_regime_effects": "array",
                "candidate_generalizations": "array",
                "subject_anomalies": "array",
                "zero_finding_diagnoses": "object keyed by zero-finding subject_id",
                "frontier_update": "object containing scientific summary/open questions/candidates/contradictions/deprioritized avenues/missing resources",
                "cohort_discrimination_assessment": "string",
                "next_subject_selection_direction": "string",
            },
        }
        raw = self._rd._chat_completion(
            [
                {
                    "role": "system",
                    "content": (
                        "You are the MTS scientific Research Director conducting a mandatory post-batch scientific synthesis. "
                        "You own scientific interpretation and generalization. Return one JSON object only."
                    ),
                },
                {"role": "user", "content": json.dumps(payload, sort_keys=True, default=str)},
            ]
        )
        try:
            decoded = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"batch synthesis response is not valid JSON: {exc}") from exc
        required = {
            "replicated_relationships",
            "contradicted_relationships",
            "untested_relationships",
            "conditional_or_regime_effects",
            "candidate_generalizations",
            "subject_anomalies",
            "zero_finding_diagnoses",
            "frontier_update",
            "cohort_discrimination_assessment",
            "next_subject_selection_direction",
        }
        missing = sorted(required - set(decoded))
        if missing:
            raise ValueError(f"batch synthesis missing required fields: {missing}")
        zero_subjects = {row.subject_id for row in ledger.subjects if row.findings_promoted == 0}
        diagnoses = decoded.get("zero_finding_diagnoses")
        if not isinstance(diagnoses, Mapping):
            raise ValueError("zero_finding_diagnoses must be an object")
        missing_zero = sorted(subject for subject in zero_subjects if not str(diagnoses.get(subject, "")).strip())
        if missing_zero:
            raise ValueError(f"batch synthesis omitted zero-finding diagnosis for: {missing_zero}")
        return BatchScientificSynthesis(batch_id=ledger.batch_id, synthesis=decoded)
