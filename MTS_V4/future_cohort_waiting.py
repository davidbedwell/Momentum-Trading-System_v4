from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Mapping

from .prospective_validation import JsonProspectiveValidationStore, ProspectiveValidationError
from .prospective_validation_runtime import (
    advance_matching_runtime,
    build_public_condition_feed,
    load_authoritative_sessions,
    save_public_condition_feed,
)
from .research_package_store import JsonResearchPackageStore


WAITING_FOR_FUTURE_COHORTS = "WAITING_FOR_FUTURE_COHORTS"
RESOLVED = "RESOLVED"
_MANIFEST_FORMAT = "MTS_V4_FUTURE_COHORT_WAITING_V1"


class FutureCohortWaitingError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class FutureCohortDailyResult:
    evaluated: int
    still_waiting: int
    resolved: int
    objective_defects: int


def _nonblank(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FutureCohortWaitingError(f"{field} must be a nonblank string")
    return value


def _load_manifest(path: Path) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise FutureCohortWaitingError(f"invalid waiting manifest JSON: {exc}") from exc
    if not isinstance(raw, Mapping):
        raise FutureCohortWaitingError("waiting manifest must be an object")
    document = dict(raw)
    if document.get("format") != _MANIFEST_FORMAT:
        raise FutureCohortWaitingError(f"unsupported waiting manifest format: {document.get('format')!r}")
    entries = document.get("entries")
    if not isinstance(entries, list):
        raise FutureCohortWaitingError("waiting manifest entries must be a list")
    return document


def _save_manifest(path: Path, document: Mapping[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(dict(document), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def evaluate_waiting_manifest(
    manifest_path: str | Path,
    *,
    as_of_utc: str | None = None,
) -> FutureCohortDailyResult:
    """Re-evaluate every durable future-cohort waiter without invoking the AI RD.

    Scientific choices are never inferred here. Each entry points to an already
    frozen AI-authored prospective-validation protocol and its source-specific
    authoritative snapshot. The existing deterministic protocol runtime decides
    only whether that frozen protocol can mechanically advance. Unsupported or
    incomplete protocol/data states fail closed and remain WAITING_FOR_FUTURE_COHORTS.
    """

    path = Path(manifest_path)
    document = _load_manifest(path)
    now = as_of_utc or datetime.now(timezone.utc).isoformat()
    entries = document["entries"]

    evaluated = 0
    resolved = 0
    defects = 0

    for index, raw_entry in enumerate(entries):
        if not isinstance(raw_entry, Mapping):
            raise FutureCohortWaitingError(f"entries[{index}] must be an object")
        entry = dict(raw_entry)
        status = entry.get("status")
        if status != WAITING_FOR_FUTURE_COHORTS:
            entries[index] = entry
            continue

        subject_id = _nonblank(entry.get("subject_id"), f"entries[{index}].subject_id")
        validation_state = _nonblank(
            entry.get("validation_state"), f"entries[{index}].validation_state"
        )
        research_package_dir = _nonblank(
            entry.get("research_package_dir"), f"entries[{index}].research_package_dir"
        )
        rp_id = _nonblank(entry.get("rp_id"), f"entries[{index}].rp_id")
        authoritative_snapshot = _nonblank(
            entry.get("authoritative_snapshot"), f"entries[{index}].authoritative_snapshot"
        )
        public_condition_feed = _nonblank(
            entry.get("public_condition_feed"), f"entries[{index}].public_condition_feed"
        )

        evaluated += 1
        entry["last_evaluated_utc"] = now
        entry["objective_defect"] = None
        try:
            validation_store = JsonProspectiveValidationStore(validation_state)
            protocol, _ = validation_store.load()
            if protocol.source_subject_id != subject_id:
                raise ProspectiveValidationError(
                    f"waiting subject/protocol mismatch: {subject_id} != {protocol.source_subject_id}"
                )
            sessions = load_authoritative_sessions(authoritative_snapshot)
            conditions = build_public_condition_feed(
                protocol=protocol,
                sessions=sessions,
                as_of_utc=now,
            )
            save_public_condition_feed(
                public_condition_feed,
                protocol=protocol,
                as_of_utc=now,
                conditions=conditions,
            )
            advance = advance_matching_runtime(
                protocol_store=validation_store,
                research_package_store=JsonResearchPackageStore(research_package_dir),
                rp_id=rp_id,
                conditions=conditions,
            )
            entry["protocol_id"] = protocol.protocol_id
            entry["protocol_fingerprint"] = protocol.fingerprint
            entry["frontier_state"] = advance.frontier_state
            entry["newly_locked_trials"] = list(advance.newly_locked_trials)
            entry["next_trial_id"] = advance.next_trial_id
            entry["gate_closed_through_session_index"] = (
                advance.gate_closed_through_session_index
            )
            if advance.frontier_state == "COMPLETE":
                entry["status"] = RESOLVED
                entry["resolved_at_utc"] = now
                resolved += 1
            else:
                entry["status"] = WAITING_FOR_FUTURE_COHORTS
        except (ProspectiveValidationError, FileNotFoundError, OSError, ValueError) as exc:
            defects += 1
            entry["status"] = WAITING_FOR_FUTURE_COHORTS
            entry["objective_defect"] = f"{type(exc).__name__}: {exc}"

        entries[index] = entry

    document["entries"] = entries
    document["last_daily_evaluation_utc"] = now
    _save_manifest(path, document)
    return FutureCohortDailyResult(
        evaluated=evaluated,
        still_waiting=sum(
            1
            for entry in entries
            if isinstance(entry, Mapping)
            and entry.get("status") == WAITING_FOR_FUTURE_COHORTS
        ),
        resolved=resolved,
        objective_defects=defects,
    )


def new_waiting_manifest(entries: list[Mapping[str, object]]) -> dict[str, object]:
    """Build the durable queue document; callers supply only already-approved paths/IDs."""

    normalized = []
    for raw in entries:
        entry = dict(raw)
        entry["status"] = WAITING_FOR_FUTURE_COHORTS
        normalized.append(entry)
    return {
        "format": _MANIFEST_FORMAT,
        "entries": normalized,
    }
