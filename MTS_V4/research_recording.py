from __future__ import annotations

from dataclasses import asdict
from typing import Mapping

from .contracts import AnalysisRequest, ResearchDecision, SubjectMetadata
from .decision_journal import JsonResearchDecisionJournal
from .research_package import (
    ResearchAnalysisRecord,
    ResearchPackage,
    ResearchQuestionRecord,
)
from .research_package_store import JsonResearchPackageStore


class ResearchRecordingError(RuntimeError):
    pass


class CampaignResearchRecorder:
    """Mechanical persistence of AI-authored research structure.

    RD chooses RP identity, question lineage, scientific interpretation,
    findings, and closure. This recorder validates only durable identity and
    lineage relationships and persists exactly what RD authored.
    """

    def __init__(
        self,
        *,
        package_store: JsonResearchPackageStore,
        decision_journal: JsonResearchDecisionJournal,
    ) -> None:
        self._packages = package_store
        self._journal = decision_journal

    def record_decision(
        self,
        *,
        campaign_id: str,
        subject: SubjectMetadata,
        decision: ResearchDecision,
        decision_sequence: int,
        analyses_executed: int,
    ) -> None:
        self._journal.append(
            campaign_id=campaign_id,
            decision_sequence=decision_sequence,
            analyses_executed=analyses_executed,
            decision=decision,
        )

        if decision.interpreted_request_id is not None:
            self._record_interpretation(decision)

        if decision.next_request is not None:
            self._record_request(
                campaign_id=campaign_id,
                subject=subject,
                request=decision.next_request,
            )

        self._record_findings(decision)

        if not decision.continue_research:
            self._record_closure(decision)

    def _record_request(
        self,
        *,
        campaign_id: str,
        subject: SubjectMetadata,
        request: AnalysisRequest,
    ) -> None:
        if not request.rp_id or not request.question_id:
            raise ResearchRecordingError(
                "live RD Analysis request is missing rp_id/question_id lineage"
            )
        if request.subject_id != subject.subject_id:
            raise ResearchRecordingError("RP request subject does not match active subject")

        package = self._packages.load(request.rp_id)
        created = package is None
        if package is None:
            package = ResearchPackage(
                rp_id=request.rp_id,
                subject_id=subject.subject_id,
                campaign_id=campaign_id,
                parent_rp_id=request.parent_rp_id,
                originating_question=request.question,
                originating_rationale=request.rationale,
            )
            self._packages.create(package)
        elif package.campaign_id != campaign_id:
            raise ResearchRecordingError(
                f"research package belongs to another campaign: {request.rp_id}"
            )

        changed = False
        if not any(item.question_id == request.question_id for item in package.questions):
            package = package.append_question(
                ResearchQuestionRecord(
                    question_id=request.question_id,
                    parent_question_id=request.parent_question_id,
                    question=request.question,
                    rationale=request.rationale,
                    research_phase=request.research_phase.value,
                )
            )
            changed = True

        if not any(item.request_id == request.request_id for item in package.analyses):
            package = package.append_analysis(
                ResearchAnalysisRecord(
                    request_id=request.request_id,
                    question_id=request.question_id,
                    method_id=request.method_id,
                    parameters=dict(request.parameters),
                    evidence_ids=tuple(request.evidence_ids),
                    analysis_inputs=tuple(asdict(item) for item in request.analysis_inputs),
                )
            )
            changed = True

        if changed:
            self._packages.save(package)
        elif created:
            # Creation without a question/analysis cannot occur because both are
            # required above; retained only as a defensive invariant.
            raise ResearchRecordingError("new RP was created without durable request lineage")

    def _record_interpretation(self, decision: ResearchDecision) -> None:
        if decision.interpreted_result_id is None:
            raise ResearchRecordingError(
                "interpreted_request_id requires interpreted_result_id"
            )
        match: ResearchPackage | None = None
        for rp_id in self._packages.list_ids():
            candidate = self._packages.load(rp_id)
            if candidate is None:
                continue
            if any(
                item.request_id == decision.interpreted_request_id
                for item in candidate.analyses
            ):
                if match is not None:
                    raise ResearchRecordingError(
                        f"interpreted request appears in multiple RPs: {decision.interpreted_request_id}"
                    )
                match = candidate
        if match is None:
            raise ResearchRecordingError(
                f"interpreted request is not present in a durable RP: {decision.interpreted_request_id}"
            )
        existing = next(
            item
            for item in match.analyses
            if item.request_id == decision.interpreted_request_id
        )
        if (
            existing.result_id == decision.interpreted_result_id
            and existing.execution_status == decision.interpreted_execution_status
            and existing.interpretation == decision.analysis_interpretation
        ):
            return
        evolved = match.record_analysis_outcome(
            request_id=decision.interpreted_request_id,
            result_id=decision.interpreted_result_id,
            execution_status=decision.interpreted_execution_status,
            interpretation=decision.analysis_interpretation,
        )
        self._packages.save(evolved)

    def _record_findings(self, decision: ResearchDecision) -> None:
        if not decision.promote_findings:
            return
        if not decision.rp_id:
            raise ResearchRecordingError("promoted findings require decision.rp_id")
        package = self._packages.load(decision.rp_id)
        if package is None:
            raise ResearchRecordingError(
                f"finding references unknown research package: {decision.rp_id}"
            )
        existing_ids = {
            str(item.get("finding_id"))
            for item in package.findings
            if isinstance(item, Mapping)
        }
        evolved = package
        for finding in decision.promote_findings:
            if finding.finding_id in existing_ids:
                continue
            evolved = evolved.append_finding(asdict(finding))
            existing_ids.add(finding.finding_id)
        if evolved is not package:
            self._packages.save(evolved)

    def _record_closure(self, decision: ResearchDecision) -> None:
        if not decision.rp_id:
            raise ResearchRecordingError("scientific closure requires decision.rp_id")
        package = self._packages.load(decision.rp_id)
        if package is None:
            raise ResearchRecordingError(
                f"scientific closure references unknown research package: {decision.rp_id}"
            )
        if package.status == "CLOSED":
            return
        close_reason = (decision.close_reason or "AI_RD_SCIENTIFIC_CLOSURE").strip()
        final_assessment = decision.analysis_interpretation
        self._packages.save(
            package.close(
                close_reason=close_reason,
                final_assessment=final_assessment,
            )
        )
