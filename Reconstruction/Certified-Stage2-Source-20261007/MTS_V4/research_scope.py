from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping

from .contracts import SubjectMetadata


class ResearchScopeType(str, Enum):
    SUBJECT = "SUBJECT"
    UNIVERSE = "UNIVERSE"
    COHORT = "COHORT"
    EVENT_COHORT = "EVENT_COHORT"


@dataclass(frozen=True, slots=True)
class ResearchScopeDefinition:
    """Durable owner identity for single- or multi-security research.

    v4 historically called this owner a ``subject_id``. That field remains the
    lineage key for backward compatibility, but the owner is no longer assumed
    to mean one ticker. A universe/cohort scope can own evidence whose rows span
    arbitrarily many securities without sending those rows to the AI provider.
    """

    scope_id: str
    scope_type: ResearchScopeType
    universe_id: str | None = None
    member_security_ids: tuple[str, ...] = ()
    attributes: Mapping[str, Any] = field(default_factory=dict)

    def to_subject_metadata(self, *, display_ticker: str | None = None) -> SubjectMetadata:
        if not self.scope_id.strip():
            raise ValueError("scope_id cannot be blank")
        if self.scope_type is not ResearchScopeType.SUBJECT and self.universe_id is None:
            raise ValueError(f"{self.scope_type.value} research scope requires universe_id")
        payload = {
            "research_scope_type": self.scope_type.value,
            "universe_id": self.universe_id,
            "contains_multiple_securities": self.scope_type is not ResearchScopeType.SUBJECT,
            "member_security_ids": list(self.member_security_ids),
        }
        payload.update(dict(self.attributes))
        return SubjectMetadata(
            subject_id=self.scope_id,
            ticker=display_ticker or self.scope_id,
            asset_class=(
                "EQUITY" if self.scope_type is ResearchScopeType.SUBJECT else "EQUITY_RESEARCH_SCOPE"
            ),
            attributes=payload,
        )


def subject_scope(subject_id: str, ticker: str) -> ResearchScopeDefinition:
    return ResearchScopeDefinition(
        scope_id=subject_id,
        scope_type=ResearchScopeType.SUBJECT,
        member_security_ids=(subject_id,),
        attributes={"ticker": ticker},
    )


def universe_scope(universe_id: str) -> ResearchScopeDefinition:
    return ResearchScopeDefinition(
        scope_id=f"universe:{universe_id}",
        scope_type=ResearchScopeType.UNIVERSE,
        universe_id=universe_id,
    )
