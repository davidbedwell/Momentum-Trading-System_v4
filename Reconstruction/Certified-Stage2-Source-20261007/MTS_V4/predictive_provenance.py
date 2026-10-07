from __future__ import annotations

from dataclasses import replace
from typing import Iterable

from .research_package import (
    PredictiveHypothesisRecord,
    ResearchPackage,
    ResearchPackageError,
    ResearchPackageStateTransition,
)
from .research_package_store import JsonResearchPackageStore


class PredictiveProvenanceError(RuntimeError):
    pass


def _matching_result_owners(
    *,
    store: JsonResearchPackageStore,
    subject_id: str,
    campaign_id: str,
    result_id: str,
) -> tuple[str, ...]:
    owners: list[str] = []
    for rp_id in store.list_ids():
        package = store.load(rp_id)
        if package is None:
            continue
        if package.subject_id != subject_id or package.campaign_id != campaign_id:
            continue
        if any(item.result_id == result_id for item in package.analyses):
            owners.append(package.rp_id)
    return tuple(owners)


def source_result_owners(
    *,
    store: JsonResearchPackageStore,
    package: ResearchPackage,
    hypothesis: PredictiveHypothesisRecord,
) -> tuple[str, ...]:
    """Return mechanically proven RP owners for a frozen hypothesis's source results.

    The function performs no semantic classification. It only proves where the
    exact durable Analysis result identifiers already live inside the same subject
    and campaign. Each source result must have exactly one durable owner.
    """

    owners: list[str] = []
    for result_id in hypothesis.source_result_ids:
        matches = _matching_result_owners(
            store=store,
            subject_id=package.subject_id,
            campaign_id=package.campaign_id,
            result_id=result_id,
        )
        if len(matches) != 1:
            raise PredictiveProvenanceError(
                "predictive source result must have exactly one durable RP owner: "
                f"{result_id} owners={list(matches)}"
            )
        owners.append(matches[0])
    return tuple(owners)


def relocate_predictive_hypothesis(
    *,
    store: JsonResearchPackageStore,
    hypothesis_id: str,
    source_rp_id: str,
    target_rp_id: str,
    target_objective: str,
    target_rationale: str,
    parent_rp_id: str | None = None,
) -> tuple[ResearchPackage, ResearchPackage]:
    """Relocate one frozen hypothesis without changing its scientific definition.

    This is a provenance repair, not a scientific rewrite. The exact hypothesis,
    source result identifiers, trial history, counts, status, and timestamps are
    preserved. A durable transition is written on both packages so the relocation
    remains auditable.
    """

    if not hypothesis_id.strip():
        raise PredictiveProvenanceError("hypothesis_id cannot be blank")
    if source_rp_id == target_rp_id:
        raise PredictiveProvenanceError("source and target RP must differ")
    if not target_objective.strip() or not target_rationale.strip():
        raise PredictiveProvenanceError("target objective/rationale cannot be blank")

    source = store.load(source_rp_id)
    if source is None:
        raise PredictiveProvenanceError(f"source RP does not exist: {source_rp_id}")
    if source.status != "OPEN":
        raise PredictiveProvenanceError(
            f"source RP must be OPEN for provenance repair: {source_rp_id}"
        )

    matches = [
        item for item in source.predictive_hypotheses if item.hypothesis_id == hypothesis_id
    ]
    if len(matches) != 1:
        raise PredictiveProvenanceError(
            f"source RP must contain exactly one {hypothesis_id}: found {len(matches)}"
        )
    hypothesis = matches[0]

    # Prove every frozen source result before mutating either durable package.
    owners = source_result_owners(store=store, package=source, hypothesis=hypothesis)

    target = store.load(target_rp_id)
    if target is None:
        if parent_rp_id is not None:
            parent = store.load(parent_rp_id)
            if parent is None:
                raise PredictiveProvenanceError(f"target parent RP does not exist: {parent_rp_id}")
            if parent.subject_id != source.subject_id or parent.campaign_id != source.campaign_id:
                raise PredictiveProvenanceError(
                    "target parent RP must belong to the same subject and campaign"
                )
        target = ResearchPackage(
            rp_id=target_rp_id,
            subject_id=source.subject_id,
            campaign_id=source.campaign_id,
            originating_question=target_objective,
            originating_rationale=target_rationale,
            parent_rp_id=parent_rp_id,
        )
        store.create(target)
    else:
        if target.status != "OPEN":
            raise PredictiveProvenanceError(f"target RP is CLOSED: {target_rp_id}")
        if target.subject_id != source.subject_id or target.campaign_id != source.campaign_id:
            raise PredictiveProvenanceError(
                "target RP must belong to the same subject and campaign as source RP"
            )
        if target.parent_rp_id != parent_rp_id:
            raise PredictiveProvenanceError(
                "existing target RP parent does not match requested provenance lineage"
            )
        if any(item.hypothesis_id == hypothesis_id for item in target.predictive_hypotheses):
            raise PredictiveProvenanceError(
                f"target RP already contains predictive hypothesis: {hypothesis_id}"
            )

    transition_payload = {
        "kind": "PREDICTIVE_HYPOTHESIS_PROVENANCE_RELOCATION",
        "hypothesis_id": hypothesis_id,
        "source_rp_id": source_rp_id,
        "target_rp_id": target_rp_id,
        "source_result_rp_ids": list(owners),
        "scientific_definition_changed": False,
    }

    target_evolved = target.append_predictive_hypothesis(hypothesis)
    target_evolved = target_evolved.append_state_transition(
        ResearchPackageStateTransition(
            transition_id=f"provenance-relocation-in:{hypothesis_id}:{source_rp_id}:{target_rp_id}",
            state={**transition_payload, "direction": "IN"},
        )
    )
    store.save(target_evolved)

    remaining = tuple(
        item for item in source.predictive_hypotheses if item.hypothesis_id != hypothesis_id
    )
    source_evolved = source._evolve(predictive_hypotheses=remaining)
    source_evolved = source_evolved.append_state_transition(
        ResearchPackageStateTransition(
            transition_id=f"provenance-relocation-out:{hypothesis_id}:{source_rp_id}:{target_rp_id}",
            state={**transition_payload, "direction": "OUT"},
        )
    )
    store.save(source_evolved)

    return source_evolved, target_evolved
