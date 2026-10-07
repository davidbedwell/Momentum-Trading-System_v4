from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable, Mapping, Protocol, Sequence


class UniverseMembershipError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class MembershipInterval:
    """Point-in-time membership and identity interval.

    Dates are inclusive. ``end_date=None`` means membership remains effective.
    ``security_id`` is stable; ticker/sector/industry are attributes known for the
    interval and may change in later intervals without changing security identity.
    """

    security_id: str
    ticker: str
    start_date: str
    end_date: str | None = None
    sector_id: str | None = None
    industry_id: str | None = None
    source_identity: str = ""

    def contains(self, effective_date: str) -> bool:
        value = date.fromisoformat(effective_date)
        start = date.fromisoformat(self.start_date)
        end = date.max if self.end_date is None else date.fromisoformat(self.end_date)
        return start <= value <= end


class PointInTimeMembership(Protocol):
    def members_on(self, effective_date: str) -> tuple[MembershipInterval, ...]: ...
    def intervals(self) -> tuple[MembershipInterval, ...]: ...


class IntervalMembership:
    def __init__(self, intervals: Sequence[MembershipInterval]) -> None:
        self._intervals = tuple(intervals)
        self._validate()

    def intervals(self) -> tuple[MembershipInterval, ...]:
        return self._intervals

    def members_on(self, effective_date: str) -> tuple[MembershipInterval, ...]:
        date.fromisoformat(effective_date)
        return tuple(item for item in self._intervals if item.contains(effective_date))

    def active_between(self, start_date: str, end_date: str) -> tuple[MembershipInterval, ...]:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
        if start > end:
            raise UniverseMembershipError("start_date cannot follow end_date")
        selected = []
        for item in self._intervals:
            item_start = date.fromisoformat(item.start_date)
            item_end = date.max if item.end_date is None else date.fromisoformat(item.end_date)
            if item_start <= end and item_end >= start:
                selected.append(item)
        return tuple(selected)

    def _validate(self) -> None:
        by_security: dict[str, list[MembershipInterval]] = {}
        for item in self._intervals:
            if not item.security_id.strip() or not item.ticker.strip():
                raise UniverseMembershipError("security_id and ticker cannot be blank")
            start = date.fromisoformat(item.start_date)
            end = date.max if item.end_date is None else date.fromisoformat(item.end_date)
            if start > end:
                raise UniverseMembershipError(f"membership interval starts after it ends: {item}")
            by_security.setdefault(item.security_id, []).append(item)
        for security_id, items in by_security.items():
            ordered = sorted(items, key=lambda item: item.start_date)
            prior_end: date | None = None
            for item in ordered:
                start = date.fromisoformat(item.start_date)
                if prior_end is not None and start <= prior_end:
                    raise UniverseMembershipError(
                        f"overlapping identity/membership intervals for {security_id}"
                    )
                prior_end = date.max if item.end_date is None else date.fromisoformat(item.end_date)


def load_membership_csv(path: str | Path, *, source_identity: str | None = None) -> IntervalMembership:
    """Load an explicit point-in-time membership file; never infer historical membership.

    Required columns: security_id,ticker,start_date. Optional: end_date,sector_id,
    industry_id,source_identity. This loader deliberately has no 'current members'
    fallback because projecting current constituents backward is prohibited.
    """

    source = Path(path)
    with source.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"security_id", "ticker", "start_date"}
        missing = required.difference(reader.fieldnames or ())
        if missing:
            raise UniverseMembershipError(f"membership CSV missing columns: {tuple(sorted(missing))}")
        rows = []
        for raw in reader:
            rows.append(
                MembershipInterval(
                    security_id=str(raw.get("security_id", "")).strip(),
                    ticker=str(raw.get("ticker", "")).strip().upper(),
                    start_date=str(raw.get("start_date", "")).strip(),
                    end_date=(str(raw.get("end_date", "")).strip() or None),
                    sector_id=(str(raw.get("sector_id", "")).strip() or None),
                    industry_id=(str(raw.get("industry_id", "")).strip() or None),
                    source_identity=(
                        str(raw.get("source_identity", "")).strip()
                        or source_identity
                        or source.name
                    ),
                )
            )
    return IntervalMembership(rows)
