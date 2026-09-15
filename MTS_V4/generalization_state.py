from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence


class GeneralizationStatus(str, Enum):
    SUBJECT_TENTATIVE = "SUBJECT_TENTATIVE"
    CROSS_SUBJECT_CANDIDATE = "CROSS_SUBJECT_CANDIDATE"
    CROSS_SUBJECT_VALIDATING = "CROSS_SUBJECT_VALIDATING"
    CROSS_SUBJECT_VERIFIED = "CROSS_SUBJECT_VERIFIED"
    CROSS_SUBJECT_NOT_VERIFIED = "CROSS_SUBJECT_NOT_VERIFIED"


_ALLOWED_TRANSITIONS = {
    GeneralizationStatus.SUBJECT_TENTATIVE: {GeneralizationStatus.CROSS_SUBJECT_CANDIDATE},
    GeneralizationStatus.CROSS_SUBJECT_CANDIDATE: {
        GeneralizationStatus.CROSS_SUBJECT_VALIDATING,
        GeneralizationStatus.CROSS_SUBJECT_NOT_VERIFIED,
    },
    GeneralizationStatus.CROSS_SUBJECT_VALIDATING: {
        GeneralizationStatus.CROSS_SUBJECT_VERIFIED,
        GeneralizationStatus.CROSS_SUBJECT_NOT_VERIFIED,
    },
    GeneralizationStatus.CROSS_SUBJECT_VERIFIED: set(),
    GeneralizationStatus.CROSS_SUBJECT_NOT_VERIFIED: set(),
}


@dataclass(frozen=True, slots=True)
class GeneralizationDefinition:
    generalization_id: str
    proposition: str
    source_subject_ids: tuple[str, ...]
    source_hypothesis_ids: tuple[str, ...] = ()
    source_finding_ids: tuple[str, ...] = ()
    authored_by: str = "AI_RD"


@dataclass(frozen=True, slots=True)
class GeneralizationTransition:
    sequence: int
    from_status: GeneralizationStatus | None
    to_status: GeneralizationStatus
    rationale: str
    evidence_subject_ids: tuple[str, ...] = ()
    supporting_result_ids: tuple[str, ...] = ()
    contradictory_result_ids: tuple[str, ...] = ()
    validation_criteria: str | None = None
    validation_trial_ids: tuple[str, ...] = ()
    authored_by: str = "AI_RD"


@dataclass(frozen=True, slots=True)
class GeneralizationSnapshot:
    definition: GeneralizationDefinition
    status: GeneralizationStatus
    transitions: tuple[GeneralizationTransition, ...]


class GeneralizationStateLedger:
    """Append-only representation of RD-authored cross-subject scientific state.

    Deterministic code validates identity and transition representation only. It
    never infers that evidence supports a transition and never authors scientific
    rationale, validation criteria, or a verified/not-verified disposition.
    """

    def __init__(self) -> None:
        self._definitions: dict[str, GeneralizationDefinition] = {}
        self._transitions: dict[str, list[GeneralizationTransition]] = {}

    @staticmethod
    def _nonblank(value: str, field_name: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field_name} cannot be blank")

    def create(self, definition: GeneralizationDefinition, *, rationale: str) -> GeneralizationSnapshot:
        self._nonblank(definition.generalization_id, "generalization_id")
        self._nonblank(definition.proposition, "proposition")
        self._nonblank(definition.authored_by, "authored_by")
        self._nonblank(rationale, "rationale")
        if not definition.source_subject_ids:
            raise ValueError("SUBJECT_TENTATIVE requires at least one source_subject_id")
        if definition.generalization_id in self._definitions:
            existing = self._definitions[definition.generalization_id]
            if existing == definition:
                return self.snapshot(definition.generalization_id)
            raise ValueError("generalization_id already exists with different definition")
        self._definitions[definition.generalization_id] = definition
        self._transitions[definition.generalization_id] = [
            GeneralizationTransition(
                sequence=1,
                from_status=None,
                to_status=GeneralizationStatus.SUBJECT_TENTATIVE,
                rationale=rationale,
                evidence_subject_ids=tuple(dict.fromkeys(definition.source_subject_ids)),
                authored_by=definition.authored_by,
            )
        ]
        return self.snapshot(definition.generalization_id)

    def transition(
        self,
        generalization_id: str,
        *,
        to_status: GeneralizationStatus,
        rationale: str,
        evidence_subject_ids: Sequence[str] = (),
        supporting_result_ids: Sequence[str] = (),
        contradictory_result_ids: Sequence[str] = (),
        validation_criteria: str | None = None,
        validation_trial_ids: Sequence[str] = (),
        authored_by: str = "AI_RD",
    ) -> GeneralizationSnapshot:
        self._nonblank(rationale, "rationale")
        self._nonblank(authored_by, "authored_by")
        current = self.snapshot(generalization_id)
        if to_status not in _ALLOWED_TRANSITIONS[current.status]:
            raise ValueError(f"invalid generalization transition: {current.status.value} -> {to_status.value}")
        subjects = tuple(dict.fromkeys(str(value) for value in evidence_subject_ids if str(value).strip()))
        if to_status is GeneralizationStatus.CROSS_SUBJECT_CANDIDATE:
            all_subjects = set(current.definition.source_subject_ids) | set(subjects)
            if len(all_subjects) < 2:
                raise ValueError("CROSS_SUBJECT_CANDIDATE requires evidence provenance from at least two subjects")
        if to_status is GeneralizationStatus.CROSS_SUBJECT_VALIDATING:
            if validation_criteria is None or not validation_criteria.strip():
                raise ValueError("CROSS_SUBJECT_VALIDATING requires frozen validation_criteria authored by RD")
        if to_status in {GeneralizationStatus.CROSS_SUBJECT_VERIFIED, GeneralizationStatus.CROSS_SUBJECT_NOT_VERIFIED}:
            if current.status is GeneralizationStatus.CROSS_SUBJECT_VALIDATING and not validation_trial_ids:
                raise ValueError("terminal validation disposition requires validation_trial_ids")
        transition = GeneralizationTransition(
            sequence=len(current.transitions) + 1,
            from_status=current.status,
            to_status=to_status,
            rationale=rationale,
            evidence_subject_ids=subjects,
            supporting_result_ids=tuple(str(value) for value in supporting_result_ids),
            contradictory_result_ids=tuple(str(value) for value in contradictory_result_ids),
            validation_criteria=validation_criteria,
            validation_trial_ids=tuple(str(value) for value in validation_trial_ids),
            authored_by=authored_by,
        )
        self._transitions[generalization_id].append(transition)
        return self.snapshot(generalization_id)

    def snapshot(self, generalization_id: str) -> GeneralizationSnapshot:
        definition = self._definitions.get(generalization_id)
        if definition is None:
            raise KeyError(generalization_id)
        transitions = tuple(self._transitions[generalization_id])
        return GeneralizationSnapshot(definition, transitions[-1].to_status, transitions)

    def snapshots(self) -> tuple[GeneralizationSnapshot, ...]:
        return tuple(self.snapshot(key) for key in sorted(self._definitions))

    def context(self) -> Mapping[str, object]:
        return {
            "policy": {
                "scientific_authority": "AI_RD",
                "deterministic_status_inference": False,
                "append_only_transition_history": True,
            },
            "generalizations": [asdict(item) for item in self.snapshots()],
        }


class JsonGeneralizationStateLedger(GeneralizationStateLedger):
    SCHEMA_VERSION = 1

    def __init__(self, path: str | Path) -> None:
        super().__init__()
        self._path = Path(path)
        self._load()

    @property
    def path(self) -> Path:
        return self._path

    def create(self, definition: GeneralizationDefinition, *, rationale: str) -> GeneralizationSnapshot:
        snapshot = super().create(definition, rationale=rationale)
        self._persist()
        return snapshot

    def transition(self, generalization_id: str, **kwargs: Any) -> GeneralizationSnapshot:
        snapshot = super().transition(generalization_id, **kwargs)
        self._persist()
        return snapshot

    def _load(self) -> None:
        if not self._path.exists():
            return
        document = json.loads(self._path.read_text(encoding="utf-8"))
        if int(document.get("schema_version", 0)) != self.SCHEMA_VERSION:
            raise ValueError("unsupported generalization-state schema_version")
        for raw in document.get("generalizations", []):
            definition_raw = raw["definition"]
            definition = GeneralizationDefinition(
                generalization_id=str(definition_raw["generalization_id"]),
                proposition=str(definition_raw["proposition"]),
                source_subject_ids=tuple(str(v) for v in definition_raw.get("source_subject_ids", ())),
                source_hypothesis_ids=tuple(str(v) for v in definition_raw.get("source_hypothesis_ids", ())),
                source_finding_ids=tuple(str(v) for v in definition_raw.get("source_finding_ids", ())),
                authored_by=str(definition_raw.get("authored_by", "AI_RD")),
            )
            transitions = raw.get("transitions", [])
            if not transitions:
                raise ValueError("generalization snapshot has no transition history")
            first = transitions[0]
            super().create(definition, rationale=str(first["rationale"]))
            for item in transitions[1:]:
                super().transition(
                    definition.generalization_id,
                    to_status=GeneralizationStatus(str(item["to_status"])),
                    rationale=str(item["rationale"]),
                    evidence_subject_ids=tuple(str(v) for v in item.get("evidence_subject_ids", ())),
                    supporting_result_ids=tuple(str(v) for v in item.get("supporting_result_ids", ())),
                    contradictory_result_ids=tuple(str(v) for v in item.get("contradictory_result_ids", ())),
                    validation_criteria=item.get("validation_criteria"),
                    validation_trial_ids=tuple(str(v) for v in item.get("validation_trial_ids", ())),
                    authored_by=str(item.get("authored_by", "AI_RD")),
                )

    def _persist(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        document = {
            "schema_version": self.SCHEMA_VERSION,
            "policy": {
                "scientific_content_authority": "AI_RD",
                "deterministic_status_inference": False,
                "raw_rows_present": False,
            },
            "generalizations": [asdict(item) for item in self.snapshots()],
        }
        payload = json.dumps(document, indent=2, sort_keys=True, default=str) + "\n"
        fd, temporary = tempfile.mkstemp(prefix=self._path.name + ".", suffix=".tmp", dir=str(self._path.parent), text=True)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, self._path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)


def apply_rd_generalization_updates(
    *,
    research_state: Mapping[str, object],
    ledger: GeneralizationStateLedger,
) -> tuple[GeneralizationSnapshot, ...]:
    """Persist explicit RD-authored updates; never infer an update from findings."""
    raw_updates = research_state.get("generalization_updates", ())
    if raw_updates is None:
        return ()
    if not isinstance(raw_updates, (list, tuple)):
        raise ValueError("research_state.generalization_updates must be an array")
    applied: list[GeneralizationSnapshot] = []
    for raw in raw_updates:
        if not isinstance(raw, Mapping):
            raise ValueError("generalization update must be an object")
        action = str(raw.get("action", "")).strip().upper()
        generalization_id = str(raw.get("generalization_id", "")).strip()
        if action == "CREATE_SUBJECT_TENTATIVE":
            definition = GeneralizationDefinition(
                generalization_id=generalization_id,
                proposition=str(raw.get("proposition", "")),
                source_subject_ids=tuple(str(v) for v in raw.get("source_subject_ids", ())),
                source_hypothesis_ids=tuple(str(v) for v in raw.get("source_hypothesis_ids", ())),
                source_finding_ids=tuple(str(v) for v in raw.get("source_finding_ids", ())),
                authored_by="AI_RD",
            )
            applied.append(ledger.create(definition, rationale=str(raw.get("rationale", ""))))
            continue
        if action != "TRANSITION":
            raise ValueError(f"unknown generalization update action: {action}")
        applied.append(
            ledger.transition(
                generalization_id,
                to_status=GeneralizationStatus(str(raw.get("to_status", ""))),
                rationale=str(raw.get("rationale", "")),
                evidence_subject_ids=tuple(str(v) for v in raw.get("evidence_subject_ids", ())),
                supporting_result_ids=tuple(str(v) for v in raw.get("supporting_result_ids", ())),
                contradictory_result_ids=tuple(str(v) for v in raw.get("contradictory_result_ids", ())),
                validation_criteria=(str(raw["validation_criteria"]) if raw.get("validation_criteria") is not None else None),
                validation_trial_ids=tuple(str(v) for v in raw.get("validation_trial_ids", ())),
                authored_by="AI_RD",
            )
        )
    return tuple(applied)
