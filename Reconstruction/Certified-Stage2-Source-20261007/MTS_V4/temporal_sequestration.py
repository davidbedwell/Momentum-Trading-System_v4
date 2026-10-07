from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
import hashlib
import json
from typing import Any, Mapping, Sequence

from .intake import IntakePayload


class TemporalSequestrationError(RuntimeError):
    pass


def _day(value: object, *, field_name: str) -> date:
    text = str(value).strip()
    if not text:
        raise TemporalSequestrationError(f"blank temporal value in {field_name}")
    # Accept ISO dates and ISO datetimes while preserving calendar-day ordering.
    candidate = text[:10]
    try:
        return date.fromisoformat(candidate)
    except ValueError as exc:
        raise TemporalSequestrationError(
            f"non-ISO temporal value in {field_name}: {text!r}"
        ) from exc


def _content_identity(payload: object) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class TemporalSequestrationPlan:
    """An externally authored temporal boundary enforced mechanically.

    Deterministic code does not choose these dates. The plan must be authored by
    the Research Director or explicit human governance before hidden outcomes are
    exposed to scientific reasoning.
    """

    temporal_field: str
    exploration_end_date: str
    blind_start_date: str
    blind_end_date: str

    def __post_init__(self) -> None:
        if not self.temporal_field.strip():
            raise TemporalSequestrationError("temporal_field cannot be blank")
        exploration_end = _day(self.exploration_end_date, field_name="exploration_end_date")
        blind_start = _day(self.blind_start_date, field_name="blind_start_date")
        blind_end = _day(self.blind_end_date, field_name="blind_end_date")
        if blind_start <= exploration_end:
            raise TemporalSequestrationError(
                "blind_start_date must be after exploration_end_date"
            )
        if blind_end < blind_start:
            raise TemporalSequestrationError("blind_end_date precedes blind_start_date")


@dataclass(frozen=True, slots=True)
class SequesteredPayloads:
    exploration: IntakePayload
    blind: IntakePayload
    excluded_after_blind: IntakePayload | None
    plan: TemporalSequestrationPlan
    source_content_identity: str


def _slice_payload(
    source: IntakePayload,
    rows: Sequence[Mapping[str, object]],
    *,
    partition_name: str,
    temporal_field: str,
) -> IntakePayload:
    values = [_day(row[temporal_field], field_name=temporal_field) for row in rows]
    coverage_start = min(values).isoformat() if values else None
    coverage_end = max(values).isoformat() if values else None
    provenance = dict(source.provenance)
    provenance.update(
        {
            "temporal_partition": partition_name,
            "temporal_partition_field": temporal_field,
            "parent_source_content_identity": _content_identity(source.payload),
        }
    )
    return IntakePayload(
        payload=[dict(row) for row in rows],
        evidence_type=source.evidence_type,
        artifact_type=source.artifact_type,
        source_identity=source.source_identity,
        coverage_start=coverage_start,
        coverage_end=coverage_end,
        row_count=len(rows),
        schema=source.schema,
        provenance=provenance,
        neutral_semantics=source.neutral_semantics,
    )


def sequester_temporal_payload(
    source: IntakePayload,
    *,
    plan: TemporalSequestrationPlan,
) -> SequesteredPayloads:
    """Split one row-oriented payload without exposing blind rows to exploration.

    The function is deliberately ignorant of scientific meaning. It validates and
    enforces a pre-authored temporal boundary, preserving exact source rows and
    provenance. Rows after the blind window are kept separate so they can remain
    eligible for later rolling exploration/validation rather than being silently
    consumed by the first blind test.
    """

    if not isinstance(source.payload, Sequence) or isinstance(
        source.payload, (str, bytes, bytearray)
    ):
        raise TemporalSequestrationError(
            "temporal sequestration requires a row-oriented sequence payload"
        )
    rows: list[Mapping[str, object]] = []
    for index, row in enumerate(source.payload):
        if not isinstance(row, Mapping):
            raise TemporalSequestrationError(
                f"temporal sequestration row {index} is not an object"
            )
        if plan.temporal_field not in row:
            raise TemporalSequestrationError(
                f"temporal field {plan.temporal_field!r} missing from row {index}"
            )
        rows.append(row)

    exploration_end = _day(plan.exploration_end_date, field_name="exploration_end_date")
    blind_start = _day(plan.blind_start_date, field_name="blind_start_date")
    blind_end = _day(plan.blind_end_date, field_name="blind_end_date")

    exploration_rows: list[Mapping[str, object]] = []
    blind_rows: list[Mapping[str, object]] = []
    after_rows: list[Mapping[str, object]] = []
    gap_rows: list[Mapping[str, object]] = []

    for row in rows:
        observed = _day(row[plan.temporal_field], field_name=plan.temporal_field)
        if observed <= exploration_end:
            exploration_rows.append(row)
        elif blind_start <= observed <= blind_end:
            blind_rows.append(row)
        elif observed > blind_end:
            after_rows.append(row)
        else:
            gap_rows.append(row)

    if gap_rows:
        raise TemporalSequestrationError(
            "sequestration plan leaves source rows in an unassigned temporal gap; "
            "choose contiguous exploration/blind boundaries or explicitly exclude them before partitioning"
        )
    if not exploration_rows:
        raise TemporalSequestrationError("exploration partition is empty")
    if not blind_rows:
        raise TemporalSequestrationError("blind partition is empty")

    exploration = _slice_payload(
        source,
        exploration_rows,
        partition_name="EXPLORATION_VISIBLE",
        temporal_field=plan.temporal_field,
    )
    blind = _slice_payload(
        source,
        blind_rows,
        partition_name="BLIND_SEALED",
        temporal_field=plan.temporal_field,
    )
    after = (
        _slice_payload(
            source,
            after_rows,
            partition_name="POST_BLIND_UNEXPOSED",
            temporal_field=plan.temporal_field,
        )
        if after_rows
        else None
    )
    return SequesteredPayloads(
        exploration=exploration,
        blind=blind,
        excluded_after_blind=after,
        plan=plan,
        source_content_identity=_content_identity(source.payload),
    )
