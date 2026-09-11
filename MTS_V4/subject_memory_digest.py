from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Mapping, Sequence

from .cross_subject_memory import (
    InMemoryCrossSubjectScientificMemory,
    ResearchFrontierState,
    ScientificMemoryRecord,
)
from .openai_compatible_provider import OpenAICompatibleResearchDirector


@dataclass(frozen=True, slots=True)
class SubjectScientificDigest:
    subject_id: str
    records: tuple[ScientificMemoryRecord, ...]
    frontier: ResearchFrontierState | None


class SolSubjectScientificMemoryAuthor:
    """Ask Sol to author compact durable knowledge after one subject closes."""

    def __init__(
        self,
        *,
        rd: OpenAICompatibleResearchDirector,
        scientific_memory: InMemoryCrossSubjectScientificMemory,
    ) -> None:
        self._rd = rd
        self._scientific_memory = scientific_memory

    def author_and_persist(
        self,
        *,
        mission: str,
        subject_id: str,
        subject_scientific_context: Mapping[str, object],
    ) -> SubjectScientificDigest:
        prior_frontier = self._scientific_memory.frontier()
        payload = {
            "operation": "AUTHOR_CROSS_SUBJECT_SCIENTIFIC_MEMORY",
            "mission": mission,
            "subject_id": subject_id,
            "subject_scientific_context": subject_scientific_context,
            "prior_cross_subject_memory": self._scientific_memory.context(exclude_subject_id=subject_id),
            "instructions": [
                "Author only compact scientific knowledge that would be useful to a later subject Research Director.",
                "Do not copy raw rows, reusable Analysis datasets, or verbose decision transcripts.",
                "Preserve uncertainty and validation status. A single-subject relationship does not become a generalized fact.",
                "Include scientifically meaningful negative results, contradictions, unresolved issues, data/resource limitations, or methodological lessons when useful.",
                "Prior memory is context, not a mandatory agenda. Update the Research Frontier to reflect what is scientifically worth discriminating next.",
                "Every memory record must identify its source subject and retain supplied RP/finding/hypothesis/result/evidence provenance when known.",
                "Each record_id must be stable and unique. If you repeat a record_id in this response, every field must be exactly identical; never reuse an existing record_id for changed scientific content.",
            ],
            "required_schema": {
                "records": [
                    {
                        "record_id": "stable unique string",
                        "kind": "scientific memory category",
                        "summary": "compact scientific statement",
                        "rp_id": "string or null",
                        "finding_id": "string or null",
                        "hypothesis_id": "string or null",
                        "result_ids": ["exact durable result ids"],
                        "evidence_ids": ["exact durable evidence ids"],
                        "status": "string or null",
                        "metadata": "object",
                    }
                ],
                "frontier": {
                    "summary": "current cross-subject research frontier",
                    "open_questions": ["..."],
                    "candidate_generalizations": ["..."],
                    "contradictions": ["..."],
                    "deprioritized_avenues": ["..."],
                    "missing_resources": ["..."],
                    "source_record_ids": ["record ids supporting this frontier"],
                },
            },
        }
        raw = self._rd._chat_completion(
            [
                {
                    "role": "system",
                    "content": (
                        "You are the MTS scientific Research Director consolidating one completed subject into compact "
                        "cross-subject scientific memory. You own scientific interpretation. Deterministic code only "
                        "persists your explicit records and validates their representation. Return one JSON object only."
                    ),
                },
                {"role": "user", "content": json.dumps(payload, sort_keys=True, default=str)},
            ]
        )
        try:
            decoded = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"subject scientific-memory response is not valid JSON: {exc}") from exc

        raw_records = decoded.get("records")
        if not isinstance(raw_records, Sequence) or isinstance(raw_records, (str, bytes)):
            raise ValueError("subject scientific-memory records must be an array")
        records: list[ScientificMemoryRecord] = []
        for index, item in enumerate(raw_records):
            if not isinstance(item, Mapping):
                raise ValueError(f"records[{index}] must be an object")
            record_id = item.get("record_id")
            kind = item.get("kind")
            summary = item.get("summary")
            if not all(isinstance(value, str) and value.strip() for value in (record_id, kind, summary)):
                raise ValueError(f"records[{index}] requires nonblank record_id, kind, summary")
            records.append(
                ScientificMemoryRecord(
                    record_id=record_id.strip(),
                    subject_id=subject_id,
                    kind=kind.strip(),
                    summary=summary.strip(),
                    rp_id=item.get("rp_id") if isinstance(item.get("rp_id"), str) else None,
                    finding_id=item.get("finding_id") if isinstance(item.get("finding_id"), str) else None,
                    hypothesis_id=item.get("hypothesis_id") if isinstance(item.get("hypothesis_id"), str) else None,
                    result_ids=tuple(str(value) for value in item.get("result_ids", ()) if str(value)),
                    evidence_ids=tuple(str(value) for value in item.get("evidence_ids", ()) if str(value)),
                    status=item.get("status") if isinstance(item.get("status"), str) else None,
                    metadata=dict(item.get("metadata", {})) if isinstance(item.get("metadata"), Mapping) else {},
                )
            )

        raw_frontier = decoded.get("frontier")
        frontier: ResearchFrontierState | None = None
        if isinstance(raw_frontier, Mapping):
            summary = raw_frontier.get("summary")
            if not isinstance(summary, str) or not summary.strip():
                raise ValueError("frontier.summary must be nonblank when frontier is supplied")
            next_version = 1 if prior_frontier is None else prior_frontier.version + 1
            frontier = ResearchFrontierState(
                version=next_version,
                summary=summary.strip(),
                open_questions=tuple(str(v) for v in raw_frontier.get("open_questions", ()) if str(v)),
                candidate_generalizations=tuple(str(v) for v in raw_frontier.get("candidate_generalizations", ()) if str(v)),
                contradictions=tuple(str(v) for v in raw_frontier.get("contradictions", ()) if str(v)),
                deprioritized_avenues=tuple(str(v) for v in raw_frontier.get("deprioritized_avenues", ()) if str(v)),
                missing_resources=tuple(str(v) for v in raw_frontier.get("missing_resources", ()) if str(v)),
                source_record_ids=tuple(str(v) for v in raw_frontier.get("source_record_ids", ()) if str(v)),
            )

        self._scientific_memory.publish_batch(records)
        if frontier is not None:
            self._scientific_memory.set_frontier(frontier)

        return SubjectScientificDigest(subject_id=subject_id, records=tuple(records), frontier=frontier)
