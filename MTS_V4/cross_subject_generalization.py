from __future__ import annotations

from dataclasses import replace
from typing import Any, Mapping, Sequence

from .contracts import EvidenceDescriptor, SubjectMetadata
from .sol_batch_provider import SolBatchResearchDirector


GENERALIZATION_SUBJECT_ID = "program:cross-subject-generalization"


def generalization_evidence_view(
    evidence: Sequence[EvidenceDescriptor],
    *,
    program_subject_id: str = GENERALIZATION_SUBJECT_ID,
) -> tuple[EvidenceDescriptor, ...]:
    """Expose multi-subject evidence to one program-level Analysis campaign.

    Raw payloads remain in the ordinary temporary cache under their original cache
    keys.  Only the campaign-local descriptor is projected onto the synthetic
    program subject so the existing compiler/executor can accept an RD-authored
    analysis spanning multiple tickers.  The exact original subject is retained in
    provenance and is never inferred from scientific content.
    """

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
    """Program-level Sol RD for explicit falsifiable cross-subject science.

    This is not a deterministic replication scheduler.  Sol receives the complete
    available corpus and decides whether any transfer test, pooled relationship,
    heterogeneity analysis, conditional generalization, contradiction study, or
    other cross-subject work is scientifically justified.  Zero Analysis
    Specifications remains a valid scientific decision.
    """

    def __init__(
        self,
        *args,
        historical_subject_context: Mapping[str, object],
        prior_cross_subject_memory_documents: Sequence[Mapping[str, object]] = (),
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._historical_subject_context = dict(historical_subject_context)
        self._prior_cross_subject_memory_documents = tuple(
            dict(document) for document in prior_cross_subject_memory_documents
        )

    def _batch_common_payload(
        self,
        *,
        subject: SubjectMetadata,
        evidence: Sequence[EvidenceDescriptor],
        available_methods: Sequence[Mapping[str, Any]],
        nexus_context: Mapping[str, object],
    ) -> dict[str, object]:
        payload = super()._batch_common_payload(
            subject=subject,
            evidence=evidence,
            available_methods=available_methods,
            nexus_context=nexus_context,
        )
        payload["cross_subject_generalization_context"] = {
            "historical_subjects": self._historical_subject_context,
            "prior_cross_subject_memory_documents": self._prior_cross_subject_memory_documents,
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
        messages = super()._batch_messages(
            operation=operation,
            mission=mission,
            payload=payload,
        )
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
            "methods to use, or whether a generalization is supported."
        )
        return [{"role": "system", "content": system}, *messages[1:]]
