from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Mapping

from .checkpoint import CampaignCheckpoint
from .contracts import EvidenceDescriptor, EvidenceMetadata


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

    A changed acquisition is evidence about the evidence, not a scientific
    failure. RD decides what any change means for the campaign.
    """

    status: EvidenceContinuityStatus
    recovered: tuple[EvidenceDescriptor, ...]
    differences: tuple[EvidenceDifference, ...] = ()
    missing_evidence_ids: tuple[str, ...] = ()
    unexpected_evidence_ids: tuple[str, ...] = ()


class CampaignRecovery:
    """Compare reacquired campaign evidence with the prior acquisition record.

    Recovery does not decide scientific adequacy and does not stop a campaign
    merely because source data changed. It reports SAME, CHANGED, or
    UNVERIFIABLE plus exact objective differences so the AI Research Director
    can determine the scientific consequence.
    """

    @staticmethod
    def compare(
        checkpoint: CampaignCheckpoint,
        reacquired: Iterable[EvidenceDescriptor],
    ) -> RecoveryAssessment:
        expected = {item.evidence_id: item for item in checkpoint.evidence_metadata}
        actual = {item.evidence_id: item for item in reacquired}

        missing = tuple(sorted(set(expected) - set(actual)))
        unexpected = tuple(sorted(set(actual) - set(expected)))
        if missing or unexpected:
            return RecoveryAssessment(
                status=EvidenceContinuityStatus.UNVERIFIABLE,
                recovered=tuple(actual[key] for key in sorted(actual)),
                missing_evidence_ids=missing,
                unexpected_evidence_ids=unexpected,
            )

        differences: list[EvidenceDifference] = []
        for evidence_id in sorted(expected):
            differences.extend(
                CampaignRecovery._compare_one(expected[evidence_id], actual[evidence_id])
            )

        return RecoveryAssessment(
            status=(
                EvidenceContinuityStatus.CHANGED
                if differences
                else EvidenceContinuityStatus.SAME
            ),
            recovered=tuple(actual[key] for key in sorted(actual)),
            differences=tuple(differences),
        )

    @staticmethod
    def _compare_one(
        expected: EvidenceMetadata,
        actual: EvidenceDescriptor,
    ) -> tuple[EvidenceDifference, ...]:
        fields: Mapping[str, object] = {
            "subject_id": actual.subject_id,
            "evidence_type": actual.evidence_type,
            "artifact_type": actual.artifact_type,
            "source_identity": actual.source_identity,
            "coverage_start": actual.coverage_start,
            "coverage_end": actual.coverage_end,
            "row_count": actual.row_count,
            "schema": tuple(actual.schema),
            "provenance": dict(actual.provenance),
            "neutral_semantics": actual.neutral_semantics,
        }
        differences: list[EvidenceDifference] = []
        for name, actual_value in fields.items():
            expected_value = getattr(expected, name)
            if actual_value != expected_value:
                differences.append(
                    EvidenceDifference(
                        evidence_id=expected.evidence_id,
                        field=name,
                        expected=expected_value,
                        actual=actual_value,
                    )
                )
        return tuple(differences)
