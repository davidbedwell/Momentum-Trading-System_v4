from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Mapping, Sequence

from .temporal import parse_timestamp


class OverlapPolicy(str, Enum):
    ALLOW = "ALLOW"
    FIRST_QUALIFYING_WINS = "FIRST_QUALIFYING_WINS"
    HIGHEST_MAGNITUDE_WINS = "HIGHEST_MAGNITUDE_WINS"
    CHRONOLOGICAL_EXCLUSION_WINDOW = "CHRONOLOGICAL_EXCLUSION_WINDOW"
    NON_OVERLAPPING_INTERVALS = "NON_OVERLAPPING_INTERVALS"


@dataclass(frozen=True, slots=True)
class EventWindow:
    event_id: str
    start: datetime
    end: datetime
    magnitude: float = 0.0
    metadata: Mapping[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.start.tzinfo is None or self.start.utcoffset() is None:
            raise ValueError("event start must be timezone-aware")
        if self.end.tzinfo is None or self.end.utcoffset() is None:
            raise ValueError("event end must be timezone-aware")
        if self.end < self.start:
            raise ValueError("event end must be >= event start")

    def overlaps(self, other: "EventWindow") -> bool:
        return not (self.end < other.start or other.end < self.start)


@dataclass(frozen=True, slots=True)
class OverlapResult:
    policy: OverlapPolicy
    version: str
    selected: tuple[EventWindow, ...]
    excluded_event_ids: tuple[str, ...]

    def to_payload(self) -> dict[str, Any]:
        return {
            "policy": self.policy.value,
            "version": self.version,
            "selected_event_ids": [event.event_id for event in self.selected],
            "excluded_event_ids": list(self.excluded_event_ids),
        }


def event_from_mapping(value: Mapping[str, Any]) -> EventWindow:
    return EventWindow(
        event_id=str(value["event_id"]),
        start=parse_timestamp(value["start"]),
        end=parse_timestamp(value.get("end", value["start"])),
        magnitude=float(value.get("magnitude", 0.0)),
        metadata=dict(value.get("metadata", {})),
    )


class OverlapService:
    VERSION = "overlap-v1"

    def apply(
        self,
        events: Sequence[EventWindow],
        *,
        policy: OverlapPolicy | str,
        exclusion_window_days: int = 0,
    ) -> OverlapResult:
        selected_policy = policy if isinstance(policy, OverlapPolicy) else OverlapPolicy(str(policy))
        ordered = tuple(sorted(events, key=lambda e: (e.start, e.end, e.event_id)))

        if selected_policy is OverlapPolicy.ALLOW:
            return OverlapResult(selected_policy, self.VERSION, ordered, ())

        if selected_policy is OverlapPolicy.FIRST_QUALIFYING_WINS:
            selected = self._greedy_non_overlap(ordered)
            return self._result(selected_policy, ordered, selected)

        if selected_policy is OverlapPolicy.NON_OVERLAPPING_INTERVALS:
            selected = self._greedy_non_overlap(ordered)
            return self._result(selected_policy, ordered, selected)

        if selected_policy is OverlapPolicy.HIGHEST_MAGNITUDE_WINS:
            remaining = list(ordered)
            selected: list[EventWindow] = []
            while remaining:
                winner = sorted(
                    remaining,
                    key=lambda e: (-abs(e.magnitude), e.start, e.end, e.event_id),
                )[0]
                selected.append(winner)
                remaining = [event for event in remaining if not event.overlaps(winner)]
            selected = sorted(selected, key=lambda e: (e.start, e.end, e.event_id))
            return self._result(selected_policy, ordered, tuple(selected))

        if selected_policy is OverlapPolicy.CHRONOLOGICAL_EXCLUSION_WINDOW:
            if exclusion_window_days < 0:
                raise ValueError("exclusion_window_days must be non-negative")
            selected: list[EventWindow] = []
            blocked_until: datetime | None = None
            for event in ordered:
                if blocked_until is not None and event.start <= blocked_until:
                    continue
                selected.append(event)
                blocked_until = event.end + timedelta(days=exclusion_window_days)
            return self._result(selected_policy, ordered, tuple(selected))

        raise AssertionError(f"Unhandled overlap policy: {selected_policy}")

    @staticmethod
    def _greedy_non_overlap(events: Sequence[EventWindow]) -> tuple[EventWindow, ...]:
        selected: list[EventWindow] = []
        for event in events:
            if all(not event.overlaps(existing) for existing in selected):
                selected.append(event)
        return tuple(selected)

    def _result(
        self,
        policy: OverlapPolicy,
        original: Sequence[EventWindow],
        selected: Sequence[EventWindow],
    ) -> OverlapResult:
        selected_ids = {event.event_id for event in selected}
        excluded = tuple(event.event_id for event in original if event.event_id not in selected_ids)
        return OverlapResult(policy, self.VERSION, tuple(selected), excluded)
