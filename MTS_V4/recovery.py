from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from .checkpoint import CampaignCheckpoint, CheckpointError
from .contracts import EvidenceDescriptor, EvidenceMetadata


@dataclass(frozen=True, slots=True)
class RecoveryAssessment:
    recovered: tuple[EvidenceDescriptor, ...]


class CampaignRecovery:
    """Objectively verify reacquired evidence before resuming a campaign.

    Recovery does not decide whether the evidence is scientifically adequate.
    It only proves that the campaign-local evidence now staged in temporary
    cache matches the durable evidence identity/coverage/schema recorded in the
    checkpoint.
    """

    @staticmethod
    def verify(
        checkpoint: CampaignCheckpoint,
        reacquired: Iterable[EvidenceDescriptor],
    ) -> RecoveryAssessment:
        expected = {item.evidence_id: item for item in checkpoint.evidence_metadata}
        actual = {item.evidence_id: item for item in reacquired}
        if set(actual) != set(expected):
            missing = tuple(sorted(set(expected) - set(actual)))
            unexpected = tuple(sorted(set(actual) - set(expected)))
            raise CheckpointError(
                f"reacquired evidence identity mismatch; missing={missing}; unexpected={unexpected}"
            )

        for evidence_id in sorted(expected):
            CampaignRecovery._verify_one(expected[evidence_id], actual[evidence_id])

        return RecoveryAssessment(
            recovered=tuple(actual[key] for key in sorted(actual))
        )

    @staticmethod
    def _verify_one(expected: EvidenceMetadata, actual: EvidenceDescriptor) -> None:
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
        for name, actual_value in fields.items():
            expected_value = getattr(expected, name)
            if actual_value != expected_value:
                raise CheckpointError(
                    f"reacquired evidence {expected.evidence_id} changed {name}: "
                    f"expected={expected_value!r}; actual={actual_value!r}"
                )
