from __future__ import annotations

from .research_package_store import JsonResearchPackageStore


class HistoricalPredictiveVerificationEligibilityError(RuntimeError):
    pass


def previously_analyzed_subject_ids(
    package_store: JsonResearchPackageStore,
) -> frozenset[str]:
    """Return subjects that have previously entered unrestricted MTS exploration.

    This is objective provenance bookkeeping for retrospective historical blind
    verification. A subject becomes historically seen when a durable RP records
    an EXPLORATION Analysis request for that subject. Blind VALIDATION work by
    itself does not mark a new subject as previously analyzed; after validation,
    the subject becomes seen when unrestricted EXPLORATION begins.

    This inventory does not prohibit genuine live prospective prediction or
    trading on a familiar subject whose future outcome has not yet occurred.
    """

    seen: set[str] = set()
    for rp_id in package_store.list_ids():
        package = package_store.load(rp_id)
        if package is None:
            continue
        if any(item.research_phase == "EXPLORATION" for item in package.analyses):
            seen.add(package.subject_id)
    return frozenset(seen)


def require_unseen_historical_verification_subject(
    *,
    package_store: JsonResearchPackageStore,
    subject_id: str,
) -> None:
    """Reject retrospective historical blind verification on an already-seen subject.

    This function governs only historical replay/holdout verification. It must
    not be used to gate current or future-facing prospective prediction/trading.
    """

    if subject_id in previously_analyzed_subject_ids(package_store):
        raise HistoricalPredictiveVerificationEligibilityError(
            "retrospective historical predictive verification requires a ticker/subject "
            f"not previously analyzed by MTS: {subject_id} is already historically seen"
        )
