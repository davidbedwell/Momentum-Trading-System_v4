from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping, Sequence


class TemporalIntegrityError(ValueError):
    """Base class for violations of governed scientific time semantics."""


class FutureInformationLeakageError(TemporalIntegrityError):
    """Raised when retrospective information leaks into contemporaneous selection/features."""


class HoldoutConflictError(TemporalIntegrityError):
    """Raised when protected validation/holdout observations are used impermissibly."""


class InformationClass(str, Enum):
    CONTEMPORANEOUS = "CONTEMPORANEOUS"
    RETROSPECTIVE_OUTCOME = "RETROSPECTIVE_OUTCOME"
    STATIC_REFERENCE = "STATIC_REFERENCE"


@dataclass(frozen=True, slots=True)
class TimeInterval:
    start: datetime
    end: datetime
    label: str = ""

    def __post_init__(self) -> None:
        for name, value in (("start", self.start), ("end", self.end)):
            if value.tzinfo is None or value.utcoffset() is None:
                raise ValueError(f"{name} must be timezone-aware")
        if self.end < self.start:
            raise ValueError("interval end must be greater than or equal to start")

    def contains(self, value: datetime) -> bool:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timestamp must be timezone-aware")
        normalized = value.astimezone(timezone.utc)
        return (
            self.start.astimezone(timezone.utc)
            <= normalized
            <= self.end.astimezone(timezone.utc)
        )

    def overlaps(self, other: "TimeInterval") -> bool:
        return not (
            self.end.astimezone(timezone.utc) < other.start.astimezone(timezone.utc)
            or other.end.astimezone(timezone.utc) < self.start.astimezone(timezone.utc)
        )

    def to_payload(self) -> dict[str, str]:
        def iso(value: datetime) -> str:
            return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
        return {"start": iso(self.start), "end": iso(self.end), "label": self.label}


def parse_timestamp(value: str | datetime) -> datetime:
    if isinstance(value, datetime):
        result = value
    elif isinstance(value, str):
        text = value.strip()
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        result = datetime.fromisoformat(text)
    else:
        raise TypeError(f"Unsupported timestamp type: {type(value)!r}")
    if result.tzinfo is None or result.utcoffset() is None:
        raise ValueError("timestamp must be timezone-aware")
    return result.astimezone(timezone.utc)


def interval_from_mapping(value: Mapping[str, Any] | None, *, label: str = "") -> TimeInterval | None:
    if not value:
        return None
    start = value.get("start")
    end = value.get("end")
    if start is None or end is None:
        raise ValueError("interval mapping requires start and end")
    return TimeInterval(
        start=parse_timestamp(start),
        end=parse_timestamp(end),
        label=str(value.get("label", label)),
    )


@dataclass(frozen=True, slots=True)
class TemporalIntegrityReport:
    predictor_columns: tuple[str, ...]
    retrospective_columns: tuple[str, ...]
    selection_columns: tuple[str, ...]
    protected_interval_hits: int
    state: str = "PASSED"

    def to_payload(self) -> dict[str, Any]:
        return {
            "predictor_columns": list(self.predictor_columns),
            "retrospective_columns": list(self.retrospective_columns),
            "selection_columns": list(self.selection_columns),
            "protected_interval_hits": self.protected_interval_hits,
            "state": self.state,
        }


class TemporalIntegrityService:
    """Enforce contemporaneous-vs-retrospective and protected-interval rules."""

    def validate_feature_roles(
        self,
        *,
        information_classes: Mapping[str, InformationClass | str],
        predictor_columns: Sequence[str] = (),
        selection_columns: Sequence[str] = (),
    ) -> TemporalIntegrityReport:
        normalized = {
            str(column): (
                value if isinstance(value, InformationClass) else InformationClass(str(value))
            )
            for column, value in information_classes.items()
        }

        leaked_predictors = tuple(
            column
            for column in predictor_columns
            if normalized.get(column) is InformationClass.RETROSPECTIVE_OUTCOME
        )
        leaked_selection = tuple(
            column
            for column in selection_columns
            if normalized.get(column) is InformationClass.RETROSPECTIVE_OUTCOME
        )

        if leaked_predictors or leaked_selection:
            details = []
            if leaked_predictors:
                details.append(f"retrospective predictors={leaked_predictors}")
            if leaked_selection:
                details.append(f"retrospective selection={leaked_selection}")
            raise FutureInformationLeakageError("; ".join(details))

        retrospective_columns = tuple(
            column
            for column, value in sorted(normalized.items())
            if value is InformationClass.RETROSPECTIVE_OUTCOME
        )

        return TemporalIntegrityReport(
            predictor_columns=tuple(predictor_columns),
            retrospective_columns=retrospective_columns,
            selection_columns=tuple(selection_columns),
            protected_interval_hits=0,
        )

    def validate_protected_usage(
        self,
        timestamps: Sequence[str | datetime],
        *,
        usage: str,
        discovery_interval: TimeInterval | None = None,
        validation_interval: TimeInterval | None = None,
        holdout_interval: TimeInterval | None = None,
    ) -> int:
        usage = usage.upper()
        protected = []
        if usage in {"DISCOVERY", "TRAINING", "EXPLORATION"}:
            if validation_interval is not None:
                protected.append(("validation", validation_interval))
            if holdout_interval is not None:
                protected.append(("holdout", holdout_interval))
        elif usage in {"VALIDATION"}:
            if holdout_interval is not None:
                protected.append(("holdout", holdout_interval))

        hits: list[tuple[str, str]] = []
        for raw in timestamps:
            ts = parse_timestamp(raw)
            for label, interval in protected:
                if interval.contains(ts):
                    hits.append((ts.isoformat(), label))

        if hits:
            raise HoldoutConflictError(
                f"{usage} usage includes {len(hits)} protected observation(s): {hits[:5]}"
            )

        if discovery_interval is not None and usage in {"DISCOVERY", "TRAINING", "EXPLORATION"}:
            outside = [
                parse_timestamp(raw)
                for raw in timestamps
                if not discovery_interval.contains(parse_timestamp(raw))
            ]
            if outside:
                raise TemporalIntegrityError(
                    f"{usage} usage includes {len(outside)} observation(s) outside discovery interval"
                )
        return 0
