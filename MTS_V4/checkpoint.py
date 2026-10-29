from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from .contracts import EvidenceMetadata, ResearchDecision, SubjectMetadata


class CheckpointError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class CampaignCheckpoint:
    """Durable mechanical checkpoint for an active research campaign.

    This is operational state, not Nexus knowledge. It may retain AI-authored
    research state and evidence metadata required to resume a campaign, but it
    must never contain raw/reproducible evidence payloads.
    """

    campaign_id: str
    subject: SubjectMetadata
    evidence_metadata: tuple[EvidenceMetadata, ...]
    decision: ResearchDecision
    analyses_executed: int = 0
    decisions_made: int = 0
    metadata: Mapping[str, Any] | None = None


class JsonCampaignCheckpointStore:
    """Atomic JSON checkpoint store outside the Research Nexus."""

    FORMAT = "MTS_V4_CAMPAIGN_CHECKPOINT_V1"

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)

    def save(self, checkpoint: CampaignCheckpoint) -> None:
        document = {
            "format": self.FORMAT,
            "campaign_id": checkpoint.campaign_id,
            "subject": asdict(checkpoint.subject),
            "evidence_metadata": [asdict(item) for item in checkpoint.evidence_metadata],
            "decision": self._decision_to_dict(checkpoint.decision),
            "analyses_executed": checkpoint.analyses_executed,
            "decisions_made": checkpoint.decisions_made,
            "metadata": dict(checkpoint.metadata or {}),
        }
        serialized = json.dumps(document, indent=2, sort_keys=True, default=str) + "\n"
        forbidden = ('"payload"', '"rows"', '"cache_key"')
        if any(token in serialized for token in forbidden):
            raise CheckpointError("campaign checkpoint attempted to persist raw/cache evidence data")
        self._path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self._path.with_suffix(self._path.suffix + ".tmp")
        temporary.write_text(serialized, encoding="utf-8")
        temporary.replace(self._path)

    def load(self) -> CampaignCheckpoint | None:
        if not self._path.exists():
            return None
        document = json.loads(self._path.read_text(encoding="utf-8"))
        if document.get("format") != self.FORMAT:
            raise CheckpointError("unsupported campaign checkpoint format")

        subject = SubjectMetadata(**document["subject"])
        evidence_metadata = tuple(
            EvidenceMetadata(
                **{
                    **raw,
                    "schema": tuple(raw.get("schema", ())),
                }
            )
            for raw in document.get("evidence_metadata", ())
        )
        decision = self._decision_from_dict(document["decision"])
        return CampaignCheckpoint(
            campaign_id=str(document["campaign_id"]),
            subject=subject,
            evidence_metadata=evidence_metadata,
            decision=decision,
            analyses_executed=int(document.get("analyses_executed", 0)),
            decisions_made=int(document.get("decisions_made", 0)),
            metadata=document.get("metadata") or {},
        )

    def clear(self) -> None:
        if self._path.exists():
            self._path.unlink()

    @staticmethod
    def _decision_to_dict(decision: ResearchDecision) -> dict[str, Any]:
        return asdict(decision)

    @staticmethod
    def _decision_from_dict(raw: Mapping[str, Any]) -> ResearchDecision:
        from .rd_codec import ResearchDecisionCodec

        return ResearchDecisionCodec.decode(json.dumps(raw))
