from __future__ import annotations

from .research_package_store import JsonResearchPackageStore


class PredictiveVerificationEligibilityError(RuntimeError):
    pass


def previously_analyzed_subject_ids(
    package_store: JsonResearchPackageStore,
) -> frozenset[str]:
    """Return subjects that have ever entered unrestricted MTS exploration.

    This is objective provenance bookkeeping. A subject becomes permanently seen
    when any durable RP records an EXPLORATION Analysis request for that subject.
    Blind VALIDATION work by itself does not mark a new subject as previously
    analyzed; after validation, the subject becomes seen when unrestricted
    EXPLORATION begins.
    """

    seen: set[str] = set()
    for rp_id in package_store.list_ids():
        package = package_store.load(rp_id)
        if package is None:
            continue
        if any(item.research_phase == "EXPLORATION" for item in package.analyses):
            seen.add(package.subject_id)
    return frozenset(seen)


def require_unseen_verification_subject(
    *,
    package_store: JsonResearchPackageStore,
    subject_id: str,
) -> None:
    """Reject predictive verification on any subject previously analyzed by MTS."""

    if subject_id in previously_analyzed_subject_ids(package_store):
        raise PredictiveVerificationEligibilityError(
            "predictive verification requires a ticker/subject not previously analyzed by MTS: "
            f"{subject_id} is already seen"
        )
