from __future__ import annotations

from dataclasses import asdict
from enum import Enum
from typing import Mapping, Sequence

from .cache import TemporaryResearchCache
from .checkpoint import CampaignCheckpoint, CheckpointError, JsonCampaignCheckpointStore
from .contracts import EvidenceDescriptor, ResearchDecision, SubjectMetadata
from .orchestrator import ResearchLoopOrchestrator, ResearchLoopOutcome
from .recovery import CampaignRecovery, EvidenceContinuityStatus, RecoveryAssessment
from .research_recording import CampaignResearchRecorder


class CheckpointedCampaignRunner:
    """Operational campaign lifecycle around the scientific research loop.

    This layer owns restart mechanics and durable recording only. It does not
    decide what evidence changes mean scientifically, what question to ask, what
    Analysis to run, how questions relate, what findings matter, or when
    scientific convergence has been reached.
    """

    def __init__(
        self,
        *,
        orchestrator: ResearchLoopOrchestrator,
        cache: TemporaryResearchCache,
        checkpoint_store: JsonCampaignCheckpointStore,
        research_recorder: CampaignResearchRecorder | None = None,
    ) -> None:
        self._orchestrator = orchestrator
        self._cache = cache
        self._store = checkpoint_store
        self._research_recorder = research_recorder

    def run_new(
        self,
        *,
        campaign_id: str,
        subject: SubjectMetadata,
        evidence: Sequence[EvidenceDescriptor],
        max_analyses: int,
    ) -> ResearchLoopOutcome:
        if self._store.load() is not None:
            raise CheckpointError("active campaign checkpoint already exists")
        callback = self._checkpoint_callback(
            campaign_id=campaign_id,
            subject=subject,
            evidence=evidence,
        )
        outcome = self._orchestrator.run(
            subject=subject,
            evidence=evidence,
            max_analyses=max_analyses,
            state_callback=callback,
        )
        self._finalize_if_closed(outcome, evidence)
        return outcome

    def resume(
        self,
        *,
        reacquired_evidence: Sequence[EvidenceDescriptor],
        max_analyses: int,
    ) -> ResearchLoopOutcome:
        checkpoint = self._store.load()
        if checkpoint is None:
            raise CheckpointError("no active campaign checkpoint to resume")
        if not checkpoint.decision.continue_research:
            raise CheckpointError("checkpointed campaign is already scientifically closed")

        assessment = CampaignRecovery.compare(checkpoint, reacquired_evidence)
        recovered_evidence = assessment.recovered
        callback = self._checkpoint_callback(
            campaign_id=checkpoint.campaign_id,
            subject=checkpoint.subject,
            evidence=recovered_evidence,
        )

        # SAME evidence requires no new scientific decision merely because the
        # process restarted. CHANGED or UNVERIFIABLE evidence is first reported
        # to RD so RD owns the scientific consequence of the continuity change.
        continuity = None
        if assessment.status is not EvidenceContinuityStatus.SAME:
            continuity = self._continuity_payload(assessment)

        outcome = self._orchestrator.run(
            subject=checkpoint.subject,
            evidence=recovered_evidence,
            max_analyses=max_analyses,
            initial_decision=checkpoint.decision,
            initial_decisions=checkpoint.decisions_made,
            initial_analyses=checkpoint.analyses_executed,
            evidence_continuity=continuity,
            state_callback=callback,
        )
        self._finalize_if_closed(outcome, recovered_evidence)
        return outcome

    def _checkpoint_callback(
        self,
        *,
        campaign_id: str,
        subject: SubjectMetadata,
        evidence: Sequence[EvidenceDescriptor],
    ):
        durable_evidence = tuple(item.durable_metadata() for item in evidence)

        def save(decision: ResearchDecision, decisions: int, analyses: int) -> None:
            if self._research_recorder is not None:
                self._research_recorder.record_decision(
                    campaign_id=campaign_id,
                    subject=subject,
                    decision=decision,
                    decision_sequence=decisions,
                    analyses_executed=analyses,
                )
            self._store.save(
                CampaignCheckpoint(
                    campaign_id=campaign_id,
                    subject=subject,
                    evidence_metadata=durable_evidence,
                    decision=decision,
                    analyses_executed=analyses,
                    decisions_made=decisions,
                )
            )

        return save

    def _finalize_if_closed(
        self,
        outcome: ResearchLoopOutcome,
        evidence: Sequence[EvidenceDescriptor],
    ) -> None:
        if not outcome.closed:
            return
        # The orchestrator publishes RD-promoted findings and the campaign
        # callback durably records the final RD decision/RP closure before this
        # method runs. Scientific history therefore survives checkpoint cleanup.
        for item in evidence:
            try:
                self._cache.release(item.cache_key)
            except KeyError:
                pass
        self._cache.purge_released()
        self._store.clear()

    @classmethod
    def _continuity_payload(cls, assessment: RecoveryAssessment) -> Mapping[str, object]:
        return {
            "status": assessment.status.value,
            "differences": [cls._json_safe(asdict(item)) for item in assessment.differences],
            "missing_evidence_ids": list(assessment.missing_evidence_ids),
            "unexpected_evidence_ids": list(assessment.unexpected_evidence_ids),
            "scientific_consequence": "AI_RESEARCH_DIRECTOR_DECIDES",
        }

    @classmethod
    def _json_safe(cls, value):
        if isinstance(value, Enum):
            return value.value
        if isinstance(value, Mapping):
            return {str(key): cls._json_safe(item) for key, item in value.items()}
        if isinstance(value, (list, tuple)):
            return [cls._json_safe(item) for item in value]
        return value
