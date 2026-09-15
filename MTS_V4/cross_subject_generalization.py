from __future__ import annotations

import json
import os
from dataclasses import replace
from typing import Any, Mapping, Sequence

from .batch_contracts import BatchResearchDecision
from .contracts import EvidenceDescriptor, SubjectMetadata
from .generalization_state import JsonGeneralizationStateLedger, apply_rd_generalization_updates
from .sol_batch_provider import SolBatchResearchDirector


GENERALIZATION_SUBJECT_ID = "program:cross-subject-generalization"


def generalization_evidence_view(
    evidence: Sequence[EvidenceDescriptor],
    *,
    program_subject_id: str = GENERALIZATION_SUBJECT_ID,
) -> tuple[EvidenceDescriptor, ...]:
    """Expose multi-subject evidence to one program-level Analysis campaign."""
    projected: list[EvidenceDescriptor] = []
    seen_ids: dict[str, str] = {}
    for item in evidence:
        prior_subject = seen_ids.get(item.evidence_id)
        if prior_subject is not None and prior_subject != item.subject_id:
            raise ValueError(
                "cross-subject corpus contains an evidence_id collision across subjects: "
                f"{item.evidence_id} belongs to both {prior_subject} and {item.subject_id}"
            )
        seen_ids[item.evidence_id] = item.subject_id
        provenance = dict(item.provenance)
        existing_origin = provenance.get("origin_subject_id")
        if existing_origin is not None and str(existing_origin) != item.subject_id:
            raise ValueError(
                "evidence provenance already contains a conflicting origin_subject_id: "
                f"{item.evidence_id} provenance={existing_origin!r} descriptor={item.subject_id!r}"
            )
        provenance["origin_subject_id"] = item.subject_id
        provenance["cross_subject_projection"] = "PROGRAM_LEVEL_GENERALIZATION_VIEW"
        projected.append(
            replace(
                item,
                subject_id=program_subject_id,
                provenance=provenance,
                neutral_semantics=(
                    item.neutral_semantics
                    + (" " if item.neutral_semantics else "")
                    + f"Original subject: {item.subject_id}."
                ),
            )
        )
    return tuple(projected)


class SolCrossSubjectGeneralizationResearchDirector(SolBatchResearchDirector):
    """Program-level Sol RD for explicit falsifiable cross-subject science."""

    def __init__(
        self,
        *args,
        historical_subject_context: Mapping[str, object],
        prior_cross_subject_memory_documents: Sequence[Mapping[str, object]] = (),
        generalization_state_context: Mapping[str, object] | None = None,
        generalization_state_path: str | None = None,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._historical_subject_context = dict(historical_subject_context)
        self._prior_cross_subject_memory_documents = tuple(dict(document) for document in prior_cross_subject_memory_documents)
        configured_path = generalization_state_path or os.getenv("MTS_GENERALIZATION_STATE_PATH", "").strip()
        self._generalization_ledger = JsonGeneralizationStateLedger(configured_path) if configured_path else None
        if generalization_state_context is not None:
            self._generalization_state_context = dict(generalization_state_context)
        elif self._generalization_ledger is not None:
            self._generalization_state_context = dict(self._generalization_ledger.context())
        else:
            self._generalization_state_context = {}

    def _accept_batch_decision(self, decision: BatchResearchDecision) -> BatchResearchDecision:
        accepted = super()._accept_batch_decision(decision)
        if self._generalization_ledger is not None:
            apply_rd_generalization_updates(research_state=accepted.research_state, ledger=self._generalization_ledger)
            self._generalization_state_context = dict(self._generalization_ledger.context())
        return accepted

    def _batch_common_payload(
        self,
        *,
        subject: SubjectMetadata,
        evidence: Sequence[EvidenceDescriptor],
        available_methods: Sequence[Mapping[str, Any]],
        nexus_context: Mapping[str, object],
        continuation: bool = False,
    ) -> dict[str, object]:
        payload = super()._batch_common_payload(
            subject=subject,
            evidence=evidence,
            available_methods=available_methods,
            nexus_context=nexus_context,
            continuation=continuation,
        )
        payload["cross_subject_generalization_context"] = {
            "historical_subjects": self._historical_subject_context,
            "prior_cross_subject_memory_documents": self._prior_cross_subject_memory_documents,
            "durable_generalization_state": self._generalization_state_context,
            "generalization_state_persistence_enabled": self._generalization_ledger is not None,
            "evidence_origin_contract": (
                "Every advertised evidence descriptor belongs operationally to the synthetic program subject so "
                "it can participate in one Analysis request. Its exact original ticker/subject is preserved in "
                "evidence.provenance.origin_subject_id. Raw payload rows remain temporary cache data and are not "
                "stored in durable scientific memory."
            ),
        }
        return payload

    @classmethod
    def _batch_messages(
        cls,
        *,
        operation: str,
        mission: str,
        payload: Mapping[str, object],
    ) -> list[Mapping[str, str]]:
        messages = super()._batch_messages(operation=operation, mission=mission, payload=payload)
        system = messages[0]["content"] + (
            " This is an explicit CROSS-SUBJECT GENERALIZATION research campaign. The active subject is a synthetic "
            "program-level subject, not a ticker. Advertised evidence may originate from many previously analyzed "
            "tickers; read provenance.origin_subject_id to preserve exact ticker identity. You have scientific authority "
            "to decide whether accumulated findings suggest any falsifiable cross-subject proposition worth testing. "
            "Actively consider transferability, common normalized market-state relationships, heterogeneity, conditional "
            "generalization, reversals of effect, contradictions, and whether a prior relationship is ticker-specific. "
            "Do not assume that similarity implies generalization, and do not inherit a prior threshold, lookback, "
            "horizon, representation, method, or target merely for consistency. Equally, do not avoid a scientifically "
            "warranted cross-subject test merely because prior-subject memory is advisory. If a direct multi-ticker "
            "experiment is scientifically useful, author the Analysis Specifications yourself using the exact advertised "
            "evidence IDs and available methods. If only a transfer test on one ticker is warranted, you may author that "
            "instead. If no cross-subject proposition is currently justified, close with zero analyses and explain why. "
            "Deterministic code does not choose which subjects to compare, how to normalize them, which variables or "
            "methods to use, or whether a generalization is supported. Durable generalization status is also yours to "
            "author explicitly. Deterministic code may validate an allowed state transition but never infer one from "
            "findings or statistical results."
        )
        user = json.loads(messages[1]["content"])
        research_state = user["required_batch_decision_schema"]["research_state"]
        research_state["generalization_updates"] = [
            {
                "action": "CREATE_SUBJECT_TENTATIVE or TRANSITION",
                "generalization_id": "stable nonblank identifier",
                "proposition": "CREATE_SUBJECT_TENTATIVE only: falsifiable proposition",
                "source_subject_ids": "CREATE_SUBJECT_TENTATIVE only: one or more exact subject IDs",
                "source_hypothesis_ids": "optional source hypothesis IDs",
                "source_finding_ids": "optional source finding IDs",
                "to_status": "TRANSITION only: CROSS_SUBJECT_CANDIDATE, CROSS_SUBJECT_VALIDATING, CROSS_SUBJECT_VERIFIED, or CROSS_SUBJECT_NOT_VERIFIED",
                "rationale": "nonblank RD-authored scientific rationale",
                "evidence_subject_ids": "TRANSITION only: exact subjects contributing to this transition",
                "supporting_result_ids": "optional exact supporting result IDs",
                "contradictory_result_ids": "optional exact contradictory result IDs",
                "validation_criteria": "required when entering CROSS_SUBJECT_VALIDATING; frozen before validation",
                "validation_trial_ids": "required for terminal disposition after CROSS_SUBJECT_VALIDATING",
            }
        ]
        user["instructions"].extend(
            [
                "Generalization state is explicit and append-only: SUBJECT_TENTATIVE -> CROSS_SUBJECT_CANDIDATE -> CROSS_SUBJECT_VALIDATING -> CROSS_SUBJECT_VERIFIED or CROSS_SUBJECT_NOT_VERIFIED.",
                "generalization_updates is a decision-local delta, not cumulative state. Do not repeat an update already present in durable_generalization_state.",
                "Do not promote a cross-subject state merely because deterministic code can represent it. Author a generalization_update only when your scientific judgment supports that exact transition.",
                "Entering CROSS_SUBJECT_CANDIDATE requires provenance from at least two subjects. Entering CROSS_SUBJECT_VALIDATING requires you to freeze validation_criteria before the validation trials. A terminal validation disposition must cite the validation_trial_ids.",
                "A materially revised proposition requires a new generalization_id rather than rewriting prior state.",
            ]
        )
        return [
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(user, sort_keys=True, default=str, separators=(",", ":"))},
        ]
