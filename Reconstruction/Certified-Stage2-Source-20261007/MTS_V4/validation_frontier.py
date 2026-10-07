from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
from datetime import date, datetime, timezone
import json
from pathlib import Path
from typing import Any, Mapping


class ValidationFrontierError(RuntimeError):
    pass


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_day(value: str, field_name: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValidationFrontierError(
            f"{field_name} must be an ISO calendar date YYYY-MM-DD: {value!r}"
        ) from exc


def trial_id(hypothesis_id: str, ordinal: int) -> str:
    """Return a trial identity without implying a new hypothesis."""
    if not hypothesis_id.strip():
        raise ValidationFrontierError("hypothesis_id cannot be blank")
    if ordinal <= 0:
        raise ValidationFrontierError("trial ordinal must be positive")
    return f"{hypothesis_id}-T{ordinal:02d}"


@dataclass(frozen=True, slots=True)
class BlindEvidenceWindow:
    """Mechanically sequestered subject window reserved for blind validation.

    The dates are an execution boundary, not a scientific conclusion. The choice
    of what window should be reserved belongs to the Research Director or explicit
    human governance before its outcomes are exposed.
    """

    window_id: str
    subject_id: str
    start_date: str
    end_date: str
    state: str = "SEALED"
    hypothesis_id: str | None = None
    trial_ids: tuple[str, ...] = ()
    sealed_at: str = field(default_factory=_utc_now)
    exposed_at: str | None = None

    def __post_init__(self) -> None:
        if not self.window_id.strip() or not self.subject_id.strip():
            raise ValidationFrontierError("window_id and subject_id cannot be blank")
        start = _parse_day(self.start_date, "start_date")
        end = _parse_day(self.end_date, "end_date")
        if end < start:
            raise ValidationFrontierError("blind window end_date precedes start_date")
        if self.state not in {"SEALED", "LOCKED_FOR_VALIDATION", "EXPOSED"}:
            raise ValidationFrontierError(f"invalid blind window state: {self.state}")
        if self.state == "SEALED" and (self.hypothesis_id is not None or self.trial_ids):
            raise ValidationFrontierError(
                "SEALED window cannot already contain hypothesis/trial assignments"
            )
        if self.state == "EXPOSED" and self.exposed_at is None:
            raise ValidationFrontierError("EXPOSED window requires exposed_at")

    def lock(self, *, hypothesis_id: str, trial_ids: tuple[str, ...]) -> "BlindEvidenceWindow":
        if self.state != "SEALED":
            raise ValidationFrontierError(
                f"only SEALED blind evidence can be locked: {self.window_id}"
            )
        if not hypothesis_id.strip():
            raise ValidationFrontierError("hypothesis_id cannot be blank")
        if not trial_ids or len(set(trial_ids)) != len(trial_ids):
            raise ValidationFrontierError("locked validation requires unique trial_ids")
        return replace(
            self,
            state="LOCKED_FOR_VALIDATION",
            hypothesis_id=hypothesis_id,
            trial_ids=tuple(trial_ids),
        )

    def expose(self) -> "BlindEvidenceWindow":
        if self.state != "LOCKED_FOR_VALIDATION":
            raise ValidationFrontierError(
                f"only a locked validation window may be exposed: {self.window_id}"
            )
        return replace(self, state="EXPOSED", exposed_at=_utc_now())


@dataclass(frozen=True, slots=True)
class SubjectValidationFrontier:
    subject_id: str
    windows: tuple[BlindEvidenceWindow, ...] = ()

    def _require_nonoverlap(self, candidate: BlindEvidenceWindow) -> None:
        candidate_start = _parse_day(candidate.start_date, "start_date")
        candidate_end = _parse_day(candidate.end_date, "end_date")
        for existing in self.windows:
            existing_start = _parse_day(existing.start_date, "start_date")
            existing_end = _parse_day(existing.end_date, "end_date")
            if candidate_start <= existing_end and existing_start <= candidate_end:
                raise ValidationFrontierError(
                    "blind evidence windows may not overlap: "
                    f"{candidate.window_id} overlaps {existing.window_id}"
                )

    def seal_window(self, window: BlindEvidenceWindow) -> "SubjectValidationFrontier":
        if window.subject_id != self.subject_id:
            raise ValidationFrontierError("blind window belongs to another subject")
        if any(item.window_id == window.window_id for item in self.windows):
            raise ValidationFrontierError(f"duplicate blind window_id: {window.window_id}")
        self._require_nonoverlap(window)
        return replace(self, windows=self.windows + (window,))

    def update_window(self, updated: BlindEvidenceWindow) -> "SubjectValidationFrontier":
        matches = [index for index, item in enumerate(self.windows) if item.window_id == updated.window_id]
        if len(matches) != 1:
            raise ValidationFrontierError(
                f"window update requires exactly one match: {updated.window_id}"
            )
        index = matches[0]
        original = self.windows[index]
        if (
            original.subject_id != updated.subject_id
            or original.start_date != updated.start_date
            or original.end_date != updated.end_date
            or original.sealed_at != updated.sealed_at
        ):
            raise ValidationFrontierError("blind window immutable identity changed")
        windows = list(self.windows)
        windows[index] = updated
        return replace(self, windows=tuple(windows))

    @property
    def sealed_windows(self) -> tuple[BlindEvidenceWindow, ...]:
        return tuple(item for item in self.windows if item.state == "SEALED")

    @property
    def active_validation_windows(self) -> tuple[BlindEvidenceWindow, ...]:
        return tuple(item for item in self.windows if item.state == "LOCKED_FOR_VALIDATION")

    @property
    def exposed_windows(self) -> tuple[BlindEvidenceWindow, ...]:
        return tuple(item for item in self.windows if item.state == "EXPOSED")


class JsonValidationFrontierStore:
    FORMAT = "MTS_V4_VALIDATION_FRONTIER_V1"

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def load(self, *, subject_id: str) -> SubjectValidationFrontier:
        if not self.path.exists():
            return SubjectValidationFrontier(subject_id=subject_id)
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        if raw.get("format") != self.FORMAT:
            raise ValidationFrontierError("unsupported validation frontier format")
        stored_subject = str(raw.get("subject_id", ""))
        if stored_subject != subject_id:
            raise ValidationFrontierError(
                f"validation frontier belongs to another subject: {stored_subject}"
            )
        windows = tuple(BlindEvidenceWindow(**item) for item in raw.get("windows", ()))
        return SubjectValidationFrontier(subject_id=subject_id, windows=windows)

    def save(self, frontier: SubjectValidationFrontier) -> None:
        document = {
            "format": self.FORMAT,
            "subject_id": frontier.subject_id,
            "windows": [asdict(item) for item in frontier.windows],
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        temporary.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        temporary.replace(self.path)
