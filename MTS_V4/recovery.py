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

    ``recovered`` uses checkpoint evidence identities when a logical source can
    be matched unambiguously. This preserves old AI-authored request/checkpoint
    references while the descriptor continues to point at the newly staged
    temporary payload through its current cache key.
    """

    status: EvidenceContinuityStatus
    recovered: tuple[EvidenceDescriptor, ...]
    differences: tuple[EvidenceDifference, ...] = ()
    missing_evidence_ids: tuple[str, ...] = ()
    unexpected_evidence_ids: tuple[str, ...] = ()


class CampaignRecovery:
    """Compare reacquired evidence without confusing acquisition time with content.

    Matching is based on stable source identity (subject/type/artifact/source),
    not a newly minted acquisition identity. Content identity and scientifically
    meaningful source metadata are compared separately. Operational acquisition
    timestamps are deliberately excluded from continuity semantics.
    """

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
        rebound: list[EvidenceDescriptor] = []
        differences: list[EvidenceDifference] = []

        all_keys = sorted(set(expected_groups) | set(actual_groups))
        for key in all_keys:
            expected_group = expected_groups.get(key, [])
            actual_group = actual_groups.get(key, [])
            if len(expected_group) != 1 or len(actual_group) != 1:
                if len(expected_group) > len(actual_group):
                    missing.extend(item.evidence_id for item in expected_group[len(actual_group):])
                if len(actual_group) > len(expected_group):
                    unexpected.extend(item.evidence_id for item in actual_group[len(expected_group):])
                # Multiple indistinguishable logical sources cannot be rebound
                # safely without inventing identity correspondence.
                if len(expected_group) != 1 or len(actual_group) != 1:
                    continue

            expected = expected_group[0]
            actual = actual_group[0]
            rebound_actual = replace(actual, evidence_id=expected.evidence_id)
            rebound.append(rebound_actual)
            differences.extend(CampaignRecovery._compare_one(expected, rebound_actual))

        if missing or unexpected or len(rebound) != len(expected_items) or len(rebound) != len(actual_items):
            return RecoveryAssessment(
                status=EvidenceContinuityStatus.UNVERIFIABLE,
                recovered=tuple(rebound),
                differences=tuple(differences),
                missing_evidence_ids=tuple(sorted(missing)),
                unexpected_evidence_ids=tuple(sorted(unexpected)),
            )

        return RecoveryAssessment(
            status=(EvidenceContinuityStatus.CHANGED if differences else EvidenceContinuityStatus.SAME),
            recovered=tuple(sorted(rebound, key=lambda item: item.evidence_id)),
            differences=tuple(differences),
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
        fields: Mapping[str, object] = {
            "coverage_start": actual.coverage_start,
            "coverage_end": actual.coverage_end,
            "row_count": actual.row_count,
            "schema": tuple(actual.schema),
            "meaningful_provenance": dict(IntakeEngine.meaningful_provenance(actual.provenance)),
            "neutral_semantics": actual.neutral_semantics,
        }
        expected_fields: Mapping[str, object] = {
            "coverage_start": expected.coverage_start,
            "coverage_end": expected.coverage_end,
            "row_count": expected.row_count,
            "schema": tuple(expected.schema),
            "meaningful_provenance": dict(IntakeEngine.meaningful_provenance(expected.provenance)),
            "neutral_semantics": expected.neutral_semantics,
        }
        differences: list[EvidenceDifference] = []
        for name, actual_value in fields.items():
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

        # Old V1 checkpoints predate content hashes. Their source/coverage/schema
        # metadata remains usable; absence of a historical hash is not fabricated
        # into a change. New checkpoints compare content identity directly.
        if expected.content_identity is not None and actual.content_identity != expected.content_identity:
            differences.append(
                EvidenceDifference(
                    evidence_id=expected.evidence_id,
                    field="content_identity",
                    expected=expected.content_identity,
                    actual=actual.content_identity,
                )
            )
        return tuple(differences)
