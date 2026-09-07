from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable, Mapping

from .checkpoint import CampaignCheckpoint
from .contracts import EvidenceDescriptor, EvidenceMetadata
from .intake import IntakeEngine


class EvidenceContinuityStatus(str, Enum):
    SAME = "SAME"
    CHANGED = "CHANGED"
    UNVERIFIABLE = "UNVERIFIABLE"


@dataclass(frozen=True, slots=True)
class EvidenceDifference:
    evidence_id: str
    field: str
    expected: object
    actual: object


@dataclass(frozen=True, slots=True)
class RecoveryAssessment:
    """Objective description of reacquired evidence continuity.

    For SAME evidence, ``recovered`` preserves the checkpoint identity/metadata
    while retaining the new temporary cache key. For CHANGED or UNVERIFIABLE
    evidence, ``recovered`` contains the newly acquired identities so RD can
    explicitly decide what to do with the changed evidence.
    """

    status: EvidenceContinuityStatus
    recovered: tuple[EvidenceDescriptor, ...]
    differences: tuple[EvidenceDifference, ...] = ()
    missing_evidence_ids: tuple[str, ...] = ()
    unexpected_evidence_ids: tuple[str, ...] = ()


class CampaignRecovery:
    """Compare content/source continuity separately from acquisition timestamps."""

    @staticmethod
    def compare(
        checkpoint: CampaignCheckpoint,
        reacquired: Iterable[EvidenceDescriptor],
    ) -> RecoveryAssessment:
        expected_items = tuple(checkpoint.evidence_metadata)
        actual_items = tuple(reacquired)

        expected_groups: dict[tuple[str, str, str, str], list[EvidenceMetadata]] = {}
        actual_groups: dict[tuple[str, str, str, str], list[EvidenceDescriptor]] = {}
        for item in expected_items:
            expected_groups.setdefault(CampaignRecovery._logical_key(item), []).append(item)
        for item in actual_items:
            actual_groups.setdefault(CampaignRecovery._logical_key(item), []).append(item)

        missing: list[str] = []
        unexpected: list[str] = []
        matched: list[tuple[EvidenceMetadata, EvidenceDescriptor]] = []
        differences: list[EvidenceDifference] = []

        for key in sorted(set(expected_groups) | set(actual_groups)):
            expected_group = expected_groups.get(key, [])
            actual_group = actual_groups.get(key, [])
            if len(expected_group) != 1 or len(actual_group) != 1:
                if len(expected_group) > len(actual_group):
                    missing.extend(item.evidence_id for item in expected_group[len(actual_group):])
                if len(actual_group) > len(expected_group):
                    unexpected.extend(item.evidence_id for item in actual_group[len(expected_group):])
                continue
            expected = expected_group[0]
            actual = actual_group[0]
            matched.append((expected, actual))
            differences.extend(CampaignRecovery._compare_one(expected, actual))

        if (
            missing
            or unexpected
            or len(matched) != len(expected_items)
            or len(matched) != len(actual_items)
        ):
            return RecoveryAssessment(
                status=EvidenceContinuityStatus.UNVERIFIABLE,
                recovered=actual_items,
                differences=tuple(differences),
                missing_evidence_ids=tuple(sorted(missing)),
                unexpected_evidence_ids=tuple(sorted(unexpected)),
            )

        if differences:
            return RecoveryAssessment(
                status=EvidenceContinuityStatus.CHANGED,
                recovered=actual_items,
                differences=tuple(differences),
            )

        # SAME means the reacquired payload may safely satisfy the old AI-authored
        # evidence reference. Preserve the checkpoint's exact durable metadata so
        # immutable Nexus history is not rewritten merely because reacquisition
        # happened at a new time or because a legacy checkpoint predates hashes.
        rebound = tuple(
            replace(
                actual,
                evidence_id=expected.evidence_id,
                subject_id=expected.subject_id,
                evidence_type=expected.evidence_type,
                artifact_type=expected.artifact_type,
                source_identity=expected.source_identity,
                coverage_start=expected.coverage_start,
                coverage_end=expected.coverage_end,
                row_count=expected.row_count,
                schema=expected.schema,
                provenance=dict(expected.provenance),
                neutral_semantics=expected.neutral_semantics,
                content_identity=expected.content_identity,
            )
            for expected, actual in matched
        )
        return RecoveryAssessment(
            status=EvidenceContinuityStatus.SAME,
            recovered=tuple(sorted(rebound, key=lambda item: item.evidence_id)),
        )

    @staticmethod
    def _logical_key(item: EvidenceMetadata | EvidenceDescriptor) -> tuple[str, str, str, str]:
        return (
            item.subject_id,
            item.evidence_type,
            item.artifact_type,
            item.source_identity,
        )

    @staticmethod
    def _compare_one(
        expected: EvidenceMetadata,
        actual: EvidenceDescriptor,
    ) -> tuple[EvidenceDifference, ...]:
        actual_fields: Mapping[str, object] = {
            "coverage_start": actual.coverage_start,
            "coverage_end": actual.coverage_end,
            "row_count": actual.row_count,
            "schema": tuple(actual.schema),
            "meaningful_provenance": dict(
                IntakeEngine.meaningful_provenance(actual.provenance)
            ),
            "neutral_semantics": actual.neutral_semantics,
        }
        expected_fields: Mapping[str, object] = {
            "coverage_start": expected.coverage_start,
            "coverage_end": expected.coverage_end,
            "row_count": expected.row_count,
            "schema": tuple(expected.schema),
            "meaningful_provenance": dict(
                IntakeEngine.meaningful_provenance(expected.provenance)
            ),
            "neutral_semantics": expected.neutral_semantics,
        }
        differences: list[EvidenceDifference] = []
        for name, actual_value in actual_fields.items():
            expected_value = expected_fields[name]
            if actual_value != expected_value:
                differences.append(
                    EvidenceDifference(
                        evidence_id=expected.evidence_id,
                        field=name,
                        expected=expected_value,
                        actual=actual_value,
                    )
                )

        # Legacy checkpoints may not contain a content hash. Absence of a hash is
        # not treated as proof of change; their durable source/coverage/schema
        # metadata remains the available continuity evidence.
        if (
            expected.content_identity is not None
            and actual.content_identity != expected.content_identity
        ):
            differences.append(
                EvidenceDifference(
                    evidence_id=expected.evidence_id,
                    field="content_identity",
                    expected=expected.content_identity,
                    actual=actual.content_identity,
                )
            )
        return tuple(differences)
